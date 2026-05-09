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


def save_susceptibility_artifacts(
    df_master: pd.DataFrame,
    *,
    out_dir: Path | None = None,
    gw_cols: list[str] | None = None,
    write_yesno_reports: bool = True,
) -> tuple[Path, Path, Path | None, Path | None]:
    out_dir = out_dir or MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    prof = build_susceptibility_profiles(df_master, gw_cols=gw_cols)
    csv_path = out_dir / "district_susceptibility_profile.csv"
    prof.to_csv(csv_path, index=False)

    summary = {
        "definition_environmental_yes": (
            "Yes if district–year is in top tertile of Environmental_exposure_index "
            "(mean z-score vs all district-years on CGWB features + log wells)."
        ),
        "definition_hmis_high_yes": (
            "Yes if High_risk_tercile == high from HMIS burden per 100k (when column exists)."
        ),
        "hmis_indicators": HMIS_VULNERABILITY_INDICATORS,
        "gw_features_used": gw_cols or DEFAULT_FEATURE_COLS,
    }
    json_path = out_dir / "susceptibility_definitions.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    pdf_path: Path | None = None
    md_path: Path | None = None
    if write_yesno_reports:
        from bihar_health_risk.susceptibility_report_export import export_all_yesno_reports

        pdf_path, md_path = export_all_yesno_reports(csv_path)

    return csv_path, json_path, pdf_path, md_path
