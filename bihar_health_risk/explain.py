"""SHAP explainability for the fitted preprocessing + model pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from bihar_health_risk.config import FIGURES_DIR


def _get_model_and_matrix(pipe: Any, X: pd.DataFrame) -> tuple[Any, np.ndarray, list[str]]:
    pre = pipe.named_steps["pre"]
    model = pipe.named_steps["model"]
    Xt = pre.transform(X)
    names = list(X.columns)
    return model, Xt, names


def compute_shap_values(pipe: Any, X: pd.DataFrame, model_name: str) -> tuple[np.ndarray, np.ndarray]:
    """Return shap_values array (n, n_features) and expected_value (scalar or per-output)."""
    model, Xt, feat_names = _get_model_and_matrix(pipe, X)
    if model_name in ("rf", "xgb"):
        explainer = shap.TreeExplainer(model, data=Xt)
        sv = explainer.shap_values(Xt)
        if isinstance(sv, list):
            sv = sv[0]
        ev = explainer.expected_value
        if isinstance(ev, np.ndarray) and ev.ndim > 0:
            ev = float(ev.ravel()[0])
        else:
            ev = float(ev)
        return np.asarray(sv), np.asarray(ev)

    linear = shap.LinearExplainer(model, Xt)
    sv = linear.shap_values(Xt)
    ev = float(linear.expected_value)
    return np.asarray(sv), ev


def save_shap_summary(
    pipe: Any,
    X: pd.DataFrame,
    model_name: str,
    out_path: Path | None = None,
) -> Path:
    out_path = out_path or (FIGURES_DIR / "shap_summary.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _, Xt, feat_names = _get_model_and_matrix(pipe, X)
    shap_values, _ = compute_shap_values(pipe, X, model_name)
    shap.summary_plot(
        shap_values,
        Xt,
        feature_names=feat_names,
        show=False,
        plot_type="bar",
    )
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return out_path


def shap_importance_table(pipe: Any, X: pd.DataFrame, model_name: str) -> pd.DataFrame:
    shap_values, _ = compute_shap_values(pipe, X, model_name)
    imp = np.mean(np.abs(shap_values), axis=0)
    return pd.DataFrame({"feature": list(X.columns), "mean_abs_shap": imp}).sort_values(
        "mean_abs_shap", ascending=False
    )
