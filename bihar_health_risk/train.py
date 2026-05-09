"""Train and compare models with spatial (grouped) cross-validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from bihar_health_risk.config import DISTRICT_COL, MODELS_DIR, TARGET_COL, YEAR_COL
from bihar_health_risk.dataio import drop_rows_missing_target, get_X_y, load_master_table, validate_columns
from bihar_health_risk.preprocess import add_exposure_interactions, build_numeric_preprocessor, clip_nonnegative, sanitize_numeric


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


@dataclass
class CVResult:
    name: str
    rmse_mean: float
    mae_mean: float
    r2_mean: float
    oof_predictions: np.ndarray


def make_models(random_state: int = 42) -> dict[str, Any]:
    try:
        from xgboost import XGBRegressor

        xgb = XGBRegressor(
            n_estimators=400,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            random_state=random_state,
            n_jobs=-1,
        )
    except ImportError:
        xgb = None

    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=8,
        min_samples_leaf=2,
        random_state=random_state,
        n_jobs=-1,
    )
    ridge = Ridge(alpha=5.0, random_state=random_state)
    return {"ridge": ridge, "rf": rf, **({"xgb": xgb} if xgb is not None else {})}


def build_full_pipeline(estimator: Any, feature_names: list[str], *, scale_for_linear: bool) -> Pipeline:
    if scale_for_linear:
        pre = ColumnTransformer(
            transformers=[
                (
                    "num",
                    Pipeline(
                        [
                            ("imp", build_numeric_preprocessor("median")),
                            ("sc", StandardScaler()),
                        ]
                    ),
                    feature_names,
                )
            ],
            remainder="drop",
        )
    else:
        pre = ColumnTransformer(
            transformers=[("num", build_numeric_preprocessor("median"), feature_names)],
            remainder="drop",
        )
    return Pipeline([("pre", pre), ("model", estimator)])


def spatial_group_cv(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    model_name: str,
    estimator: Any,
    *,
    n_splits: int = 5,
    random_state: int = 42,
) -> CVResult:
    gkf = GroupKFold(n_splits=n_splits)
    pipe = build_full_pipeline(
        estimator,
        list(X.columns),
        scale_for_linear=(model_name == "ridge"),
    )
    y = y.astype(float)
    groups = groups.astype(str)

    rmses, maes, r2s = [], [], []
    oof = np.full(len(y), np.nan)

    for train_idx, test_idx in gkf.split(X, y, groups):
        Xt, Xv = X.iloc[train_idx], X.iloc[test_idx]
        yt, yv = y.iloc[train_idx], y.iloc[test_idx]
        pipe.fit(Xt, yt)
        pred = pipe.predict(Xv)
        oof[test_idx] = pred
        rmses.append(_rmse(yv.values, pred))
        maes.append(mean_absolute_error(yv.values, pred))
        r2s.append(r2_score(yv.values, pred))

    m_r2 = float(np.mean(r2s))
    if not np.isfinite(m_r2):
        m_r2 = float("nan")
    return CVResult(
        name=model_name,
        rmse_mean=float(np.mean(rmses)),
        mae_mean=float(np.mean(maes)),
        r2_mean=m_r2,
        oof_predictions=oof,
    )


def _n_splits_for_groups(n_groups: int, requested: int) -> int:
    return max(2, min(requested, n_groups))


def run_training(
    data_path: Path,
    feature_cols: list[str],
    *,
    n_splits: int = 5,
    random_state: int = 42,
    use_interactions: bool = True,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Load data, run spatial CV, refit best model on all rows, save pipeline and metrics."""
    out_dir = out_dir or MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    feature_cols = list(feature_cols)
    df = load_master_table(data_path)
    if use_interactions:
        df = add_exposure_interactions(df)
        if "Rain_x_OpenDefec" not in feature_cols and "Rain_x_OpenDefec" in df.columns:
            feature_cols = feature_cols + ["Rain_x_OpenDefec"]

    validate_columns(df, feature_cols, require_target=True)
    df = drop_rows_missing_target(df)
    df = sanitize_numeric(df, feature_cols + [TARGET_COL])
    nonnegative = [
        c
        for c in feature_cols
        if c in df.columns and ("GW_" in c or c == "n_wells") and "pH" not in c.lower()
    ]
    df = clip_nonnegative(df, nonnegative)

    X, y, groups = get_X_y(df, feature_cols, groups=DISTRICT_COL)
    if groups is None:
        raise ValueError(f"Column '{DISTRICT_COL}' required for spatial GroupKFold.")

    n_groups = groups.nunique()
    splits = _n_splits_for_groups(n_groups, n_splits)

    models = make_models(random_state=random_state)
    results: list[CVResult] = []
    for name, est in models.items():
        if est is None:
            continue
        results.append(spatial_group_cv(X, y, groups, name, est, n_splits=splits, random_state=random_state))

    best = min(results, key=lambda r: r.rmse_mean)
    y_arr = y.values.astype(float)
    oof_best = best.oof_predictions
    valid_oof = np.isfinite(oof_best)
    if valid_oof.any():
        yt, yp = y_arr[valid_oof], oof_best[valid_oof]
        pooled_oof_rmse = _rmse(yt, yp)
        pooled_oof_r2 = float(r2_score(yt, yp))
        naive_mean = float(np.mean(y_arr))
        naive_rmse = _rmse(yt, np.full_like(yt, naive_mean))
        rho, rho_p = spearmanr(yt, yp)
        pooled_spearman_r = float(rho) if np.isfinite(rho) else float("nan")
        pooled_spearman_p = float(rho_p) if np.isfinite(rho_p) else float("nan")
        rmse_gain_vs_naive_pct = (
            float(100.0 * (naive_rmse - pooled_oof_rmse) / naive_rmse) if naive_rmse > 0 else float("nan")
        )
    else:
        pooled_oof_rmse = pooled_oof_r2 = naive_rmse = float("nan")
        pooled_spearman_r = pooled_spearman_p = rmse_gain_vs_naive_pct = float("nan")

    best_est = models[best.name]
    final_pipe = build_full_pipeline(
        best_est,
        list(X.columns),
        scale_for_linear=(best.name == "ridge"),
    )
    final_pipe.fit(X, y)

    artifact_path = out_dir / "best_model.joblib"
    joblib.dump({"pipeline": final_pipe, "feature_cols": list(X.columns), "model_name": best.name}, artifact_path)

    metrics = {
        "project_framing": {
            "primary_goal": (
                "Reproducible fusion of official CGWB + HMIS + Census data, with spatially honest "
                "validation (held-out districts). HMIS log-burden is an external referent for "
                "associational checks—not a forecasting target."
            ),
            "success_criteria": [
                "Transparent pipeline and artifacts",
                "GroupKFold by district (no leakage across geography)",
                "Compare OOF error to naive mean baseline",
                "Report rank alignment (Spearman) for prioritisation narratives",
                "SHAP for exposure directionality (hypothesis generation)",
            ],
            "why_fold_r2_can_be_negative": (
                "Per-fold R² uses small held-out district sets; predicting unseen districts with "
                "groundwater-only features is intentionally strict. Pooled OOF metrics and baseline "
                "comparison are clearer summaries for this study design."
            ),
        },
        "n_districts": int(n_groups),
        "n_rows": int(len(df)),
        "spatial_cv_splits": splits,
        "best_model": best.name,
        "pooled_oof_metrics_best_model": {
            "rmse": pooled_oof_rmse,
            "r2": pooled_oof_r2,
            "spearman_r": pooled_spearman_r,
            "spearman_p_two_sided": pooled_spearman_p,
            "naive_mean_baseline_rmse": naive_rmse,
            "rmse_improvement_vs_naive_pct": rmse_gain_vs_naive_pct,
        },
        "cv_by_model": [
            {"model": r.name, "rmse_mean": r.rmse_mean, "mae_mean": r.mae_mean, "r2_mean": r.r2_mean}
            for r in results
        ],
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    oof_df = df[[DISTRICT_COL]].copy()
    if YEAR_COL in df.columns:
        oof_df[YEAR_COL] = df[YEAR_COL]
    oof_df[TARGET_COL] = y.values
    for r in results:
        oof_df[f"oof_pred_{r.name}"] = r.oof_predictions
    oof_df.to_csv(out_dir / "oof_predictions.csv", index=False)

    return {
        "metrics": metrics,
        "artifact_path": str(artifact_path),
        "best_cv": best,
        "oof_frame": oof_df,
        "training_df": df,
        "X": X,
        "y": y,
        "groups": groups,
        "fitted_pipeline": final_pipe,
    }
