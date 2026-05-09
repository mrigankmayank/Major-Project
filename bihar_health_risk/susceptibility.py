"""District–year susceptibility profiles from official GW + HMIS columns (no regression required).

Environmental flags use cohort-relative z-scores on CGWB features (transparent, presentable).
HMIS tier uses existing tertiles / burden fields when present.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from bihar_health_risk.config import (
    DEFAULT_FEATURE_COLS,
    DISTRICT_COL,
    MODELS_DIR,
    RESULTS_DIR,
    TARGET_COL,
    YEAR_COL,
)
from bihar_health_risk.etl_hmis_vulnerability import HMIS_VULNERABILITY_INDICATORS

# Short labels for slides / CSV
GW_LABELS: dict[str, str] = {
    "GW_pH_median": "pH",
    "GW_EC_uScm_median": "Electrical conductivity (EC)",
    "GW_HCO3_median": "Bicarbonate (HCO3)",
    "GW_Cl_median": "Chloride (Cl)",
    "GW_SO4_median": "Sulphate (SO4)",
    "GW_NO3_median": "Nitrate (NO3)",
    "GW_F_mgL_median": "Fluoride (F)",
    "GW_TDS_median": "Total dissolved solids (TDS)",
    "n_wells": "Monitoring intensity (# wells sampled)",
}

HMIS_COMPOSITE_SUMMARY = (
    "HMIS composite burden sums official counts for: SAM; childhood diarrhoea, pneumonia, measles; "
    "infant deaths (1–12m) from diarrhoea/pneumonia; child deaths (1–5y) from diarrhoea/pneumonia; "
    "infant deaths within 24h of birth; still births (facility rollup Total, same HMIS rule as ETL)."
)


def _z_series(s: pd.Series, *, log1p: bool = False) -> pd.Series:
    v = pd.to_numeric(s, errors="coerce")
    if log1p:
        v = np.log1p(v.clip(lower=0))
    mu = v.mean()
    sig = v.std(ddof=0)
    if sig is None or sig < 1e-12:
        return pd.Series(0.0, index=s.index)
    return (v - mu) / sig


def build_susceptibility_profiles(df: pd.DataFrame, *, gw_cols: list[str] | None = None) -> pd.DataFrame:
    """Return one row per input row with environmental stress bands and top GW drivers."""
    gw_cols = gw_cols or [c for c in DEFAULT_FEATURE_COLS if c in df.columns]
    if not gw_cols:
        raise ValueError("No groundwater feature columns found for susceptibility.")

    out = df[[DISTRICT_COL, YEAR_COL]].copy() if YEAR_COL in df.columns else df[[DISTRICT_COL]].copy()

    zcols: dict[str, pd.Series] = {}
    for c in gw_cols:
        log1p = c == "n_wells"
        zcols[c] = _z_series(df[c], log1p=log1p)

    zdf = pd.DataFrame(zcols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    # Mean signed z as simple "above/below cohort" exposure index
    out["Environmental_exposure_index"] = zdf.mean(axis=1).round(4)
    # Driver ranking: magnitude of deviation from cohort (interpretable as "most shifted" chemistry)
    abs_z = zdf.abs()

    def top_names(row: pd.Series) -> tuple[str, str, str]:
        order = row.sort_values(ascending=False).index.tolist()
        names = []
        for j in range(min(3, len(order))):
            c = order[j]
            zval = float(zdf.loc[row.name, c]) if row.name in zdf.index else float("nan")
            names.append(f"{GW_LABELS.get(c, c)} (z={zval:+.2f})")
        while len(names) < 3:
            names.append("")
        return names[0], names[1], names[2]

    tops = abs_z.apply(lambda r: top_names(r), axis=1, result_type="expand")
    out["Top_GW_stress_1"] = tops[0]
    out["Top_GW_stress_2"] = tops[1]
    out["Top_GW_stress_3"] = tops[2]

    # Terciles on exposure index for Yes/No style bands
    idx = out["Environmental_exposure_index"]
    try:
        bands = pd.qcut(idx, q=3, labels=["Low", "Medium", "High"], duplicates="drop")
    except ValueError:
        bands = pd.Series(pd.NA, index=out.index)
    out["Environmental_stress_band"] = bands.astype(str)

    def yn_band(b: object) -> str:
        return "Yes" if str(b) == "High" else "No"

    out["Environmental_susceptibility_high_stress_YN"] = out["Environmental_stress_band"].map(yn_band)

    if "High_risk_tercile" in df.columns:
        ter = df["High_risk_tercile"]
        out["HMIS_observed_burden_tercile"] = ter.astype(str).replace({"nan": ""})

        def _hmis_high(val: object) -> str:
            if pd.isna(val):
                return "Unknown"
            t = str(val).strip().lower()
            if t == "high":
                return "Yes"
            if t in ("low", "mid", "medium"):
                return "No"
            return "Unknown"

        out["HMIS_observed_high_burden_YN"] = ter.map(_hmis_high)
    elif TARGET_COL in df.columns:
        out["HMIS_observed_burden_tercile"] = ""
        out["HMIS_observed_high_burden_YN"] = ""
    else:
        out["HMIS_observed_burden_tercile"] = ""
        out["HMIS_observed_high_burden_YN"] = ""

    if "HMIS_burden_per_100k" in df.columns:
        out["HMIS_burden_per_100k"] = pd.to_numeric(df["HMIS_burden_per_100k"], errors="coerce").round(2)

    out["HMIS_health_indicators_in_composite"] = HMIS_COMPOSITE_SUMMARY
    # Exact catalogue lines for appendix-style reference
    out["HMIS_indicator_list_reference"] = "; ".join(HMIS_VULNERABILITY_INDICATORS)

    note = (
        "Environmental Y/N = cohort-high exposure band from CGWB medians + monitoring intensity "
        "(not a clinical diagnosis). HMIS Y/N = observed composite burden in top tertile when available."
    )
    out["Interpretation_note"] = note

    return out


def _resolve_gw_cols(df: pd.DataFrame, gw_cols: list[str] | None) -> list[str]:
    cols = gw_cols or [c for c in DEFAULT_FEATURE_COLS if c in df.columns]
    return cols


def build_susceptibility_reference(
    df_master: pd.DataFrame,
    *,
    gw_cols: list[str] | None = None,
    exposure_index: pd.Series | None = None,
) -> dict:
    """Frozen stats + tertile bin edges from the reference panel (training cohort).

    New district-years must be scored with this JSON so Yes/No is comparable to the original report.
    """
    gw_cols = _resolve_gw_cols(df_master, gw_cols)
    if not gw_cols:
        raise ValueError("No GW columns for reference.")

    feature_stats: dict[str, dict[str, float]] = {}
    for c in gw_cols:
        v = pd.to_numeric(df_master[c], errors="coerce")
        if c == "n_wells":
            v = np.log1p(v.clip(lower=0))
        sig = float(v.std(ddof=0))
        if not np.isfinite(sig) or sig < 1e-12:
            sig = 1.0
        feature_stats[c] = {"mean": float(np.nanmean(v.values)), "std": sig}

    if exposure_index is None:
        exposure_index = build_susceptibility_profiles(df_master, gw_cols=gw_cols)["Environmental_exposure_index"]

    idx = pd.to_numeric(exposure_index, errors="coerce").dropna()
    exposure_edges: list[float] = []
    exposure_labels = ["Low", "Medium", "High"]
    try:
        if len(idx) >= 3:
            _, bin_edges = pd.qcut(idx, q=3, retbins=True, duplicates="drop")
            exposure_edges = [float(x) for x in bin_edges]
    except (ValueError, TypeError):
        exposure_edges = []

    hmis_edges: list[float] = []
    hmis_labels = ["low", "mid", "high"]
    if "HMIS_burden_per_100k" in df_master.columns:
        hb = pd.to_numeric(df_master["HMIS_burden_per_100k"], errors="coerce").dropna()
        try:
            if len(hb) >= 3:
                _, he = pd.qcut(hb, q=3, retbins=True, duplicates="drop")
                hmis_edges = [float(x) for x in he]
        except (ValueError, TypeError):
            hmis_edges = []

    return {
        "schema_version": 1,
        "gw_cols": gw_cols,
        "log1p_cols": ["n_wells"],
        "feature_stats": feature_stats,
        "reference_n_rows": int(len(df_master)),
        "exposure_bin_edges": exposure_edges,
        "exposure_band_labels": exposure_labels[: max(0, len(exposure_edges) - 1)],
        "hmis_burden_bin_edges": hmis_edges,
        "hmis_burden_band_labels": hmis_labels[: max(0, len(hmis_edges) - 1)],
        "how_to_predict_new_years": (
            "Save a CSV with columns District, Year, and the same GW_* / n_wells columns as training. "
            "Optional: HMIS_burden_per_100k if you want HMIS high/low tiers vs the same reference cohort. "
            "Run: python scripts/predict_susceptibility_new_year.py --reference results/models/susceptibility_reference.json --input your.csv -o out.csv"
        ),
    }


def apply_frozen_reference_susceptibility(df_new: pd.DataFrame, ref: dict) -> pd.DataFrame:
    """Environmental Yes/No + bands using frozen reference; HMIS tiers if rate column + reference HMIS bins exist."""
    gw_cols = ref.get("gw_cols") or []
    stats = ref.get("feature_stats") or {}
    log1p_cols = set(ref.get("log1p_cols") or ["n_wells"])

    missing = [c for c in gw_cols if c not in df_new.columns]
    if missing:
        raise ValueError(f"Input missing GW columns required by reference: {missing}")

    if DISTRICT_COL not in df_new.columns:
        raise ValueError(f"Input must include '{DISTRICT_COL}'.")

    rows = len(df_new)
    zcols: dict[str, pd.Series] = {}
    for c in gw_cols:
        v = pd.to_numeric(df_new[c], errors="coerce")
        if c in log1p_cols:
            v = np.log1p(v.clip(lower=0))
        mu = stats[c]["mean"]
        sig = stats[c]["std"]
        z = (v - mu) / sig if sig > 1e-12 else pd.Series(0.0, index=v.index)
        zcols[c] = z.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    zdf = pd.DataFrame(zcols)
    exposure_index = zdf.mean(axis=1).round(4)

    out = pd.DataFrame(index=df_new.index)
    out[DISTRICT_COL] = df_new[DISTRICT_COL].values
    out[YEAR_COL] = df_new[YEAR_COL].values if YEAR_COL in df_new.columns else pd.Series([pd.NA] * rows, index=df_new.index)

    abs_z = zdf.abs()

    def top_for_row(i: int) -> tuple[str, str, str]:
        row = abs_z.iloc[i]
        order = row.sort_values(ascending=False).index.tolist()
        names: list[str] = []
        for j in range(min(3, len(order))):
            c = order[j]
            zval = float(zdf.iloc[i][c])
            names.append(f"{GW_LABELS.get(c, c)} (z={zval:+.2f})")
        while len(names) < 3:
            names.append("")
        return names[0], names[1], names[2]

    tops = [top_for_row(i) for i in range(rows)]
    out["Environmental_exposure_index"] = exposure_index.values
    out["Top_GW_stress_1"] = [t[0] for t in tops]
    out["Top_GW_stress_2"] = [t[1] for t in tops]
    out["Top_GW_stress_3"] = [t[2] for t in tops]

    edges = ref.get("exposure_bin_edges") or []
    labels = ref.get("exposure_band_labels") or ["Low", "Medium", "High"]
    if len(edges) >= 2:
        n_bins = len(edges) - 1
        use_labels = labels[:n_bins]
        # Clip to reference training range so extreme new rows still get Low/Medium/High (no NaN band)
        e0, e_last = float(edges[0]), float(edges[-1])
        xc = exposure_index.astype(float).clip(lower=e0, upper=e_last)
        bands = pd.cut(
            xc,
            bins=edges,
            labels=use_labels,
            include_lowest=True,
        )
        out["Environmental_stress_band"] = bands.astype(str)
    else:
        out["Environmental_stress_band"] = ""

    def env_yn(b: object) -> str:
        s = str(b).strip()
        if s in ("nan", "NaN", "", "<NA>"):
            return "Unknown"
        return "Yes" if s == "High" else "No"

    out["Environmental_susceptibility_high_stress_YN"] = out["Environmental_stress_band"].map(env_yn)

    hmis_edges = ref.get("hmis_burden_bin_edges") or []
    hmis_labs = ref.get("hmis_burden_band_labels") or ["low", "mid", "high"]
    if "HMIS_burden_per_100k" in df_new.columns and len(hmis_edges) >= 2:
        hb = pd.to_numeric(df_new["HMIS_burden_per_100k"], errors="coerce")
        n_h = len(hmis_edges) - 1
        cats = pd.cut(hb.astype(float), bins=hmis_edges, labels=hmis_labs[:n_h], include_lowest=True)
        out["HMIS_burden_per_100k"] = hb.round(2)
        out["HMIS_observed_burden_tercile"] = cats.astype(str).replace({"nan": ""})

        def hmis_yn_cell(val: object) -> str:
            if pd.isna(val) or str(val).strip().lower() in ("", "nan", "<na>"):
                return "Unknown"
            t = str(val).strip().lower()
            if t == "high":
                return "Yes"
            if t in ("low", "mid", "medium"):
                return "No"
            return "Unknown"

        out["HMIS_observed_high_burden_YN"] = out["HMIS_observed_burden_tercile"].map(hmis_yn_cell)
    else:
        if "HMIS_burden_per_100k" in df_new.columns:
            out["HMIS_burden_per_100k"] = pd.to_numeric(df_new["HMIS_burden_per_100k"], errors="coerce").round(2)
            out["HMIS_observed_burden_tercile"] = ""
            out["HMIS_observed_high_burden_YN"] = (
                "N/A (reference has no HMIS tertile bins — rebuild reference from master with HMIS rates)"
                if len(hmis_edges) < 2
                else "Unknown"
            )
        else:
            out["HMIS_burden_per_100k"] = pd.NA
            out["HMIS_observed_burden_tercile"] = ""
            out["HMIS_observed_high_burden_YN"] = "N/A (add HMIS_burden_per_100k column for HMIS Yes/No)"

    out["HMIS_health_indicators_in_composite"] = HMIS_COMPOSITE_SUMMARY
    out["HMIS_indicator_list_reference"] = "; ".join(HMIS_VULNERABILITY_INDICATORS)
    out["Interpretation_note"] = (
        "Environmental Y/N uses frozen reference cohort stats from susceptibility_reference.json. "
        "HMIS Y/N only if you supplied HMIS_burden_per_100k and reference HMIS tertiles exist."
    )
    out["Prediction_mode"] = "frozen_reference_new_year_or_new_row"

    return out


def save_susceptibility_artifacts(
    df_master: pd.DataFrame,
    *,
    out_dir: Path | None = None,
    gw_cols: list[str] | None = None,
    write_yesno_reports: bool = True,
) -> tuple[Path, Path, Path, Path | None, Path | None]:
    out_dir = out_dir or MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    resolved_gw = _resolve_gw_cols(df_master, gw_cols)
    prof = build_susceptibility_profiles(df_master, gw_cols=resolved_gw)
    csv_path = out_dir / "district_susceptibility_profile.csv"
    prof.to_csv(csv_path, index=False)

    ref_dict = build_susceptibility_reference(
        df_master,
        gw_cols=resolved_gw,
        exposure_index=prof["Environmental_exposure_index"],
    )
    ref_path = out_dir / "susceptibility_reference.json"
    ref_path.write_text(json.dumps(ref_dict, indent=2), encoding="utf-8")

    summary = {
        "definition_environmental_yes": (
            "Yes if district–year is in top tertile of Environmental_exposure_index "
            "(mean z-score vs all district-years on CGWB features + log wells)."
        ),
        "definition_hmis_high_yes": (
            "Yes if High_risk_tercile == high from HMIS burden per 100k (when column exists)."
        ),
        "hmis_indicators": HMIS_VULNERABILITY_INDICATORS,
        "gw_features_used": resolved_gw,
        "frozen_reference_for_new_years": ref_path.name,
        "how_to_score_new_district_years": ref_dict["how_to_predict_new_years"],
    }
    json_path = out_dir / "susceptibility_definitions.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    pdf_path: Path | None = None
    md_path: Path | None = None
    if write_yesno_reports:
        from bihar_health_risk.susceptibility_report_export import export_all_yesno_reports

        pdf_path, md_path = export_all_yesno_reports(csv_path)

    return csv_path, json_path, ref_path, pdf_path, md_path
