"""
Build `data/processed/official_district_year_master.csv` from:
  - CGWB Bihar well CSVs (district × year groundwater medians)
  - HMIS multi-indicator child-health burden + vulnerability score
  - Census 2011 district population (denominator for rates)

Target for ML: log1p(burden per 100k population), not raw SAM counts.

Run after: `python scripts/extract_cgwb_bihar_csvs.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bihar_health_risk.config import PROCESSED_DIR, RAW_GW, ensure_directories  # noqa: E402
from bihar_health_risk.etl_census_population import load_bihar_district_population_2011  # noqa: E402
from bihar_health_risk.etl_cgwb import aggregate_cgwb_by_district_year  # noqa: E402
from bihar_health_risk.etl_hmis_vulnerability import build_hmis_vulnerability_panel  # noqa: E402
from bihar_health_risk.etl_merge import standardize_district_names  # noqa: E402

HMIS_PATH = str(
    ROOT
    / "14277- Dataful"
    / "district-and-year-wise-data-related-to-all-health-indicators-under-health-management-information-system-hmis-for-bihar.xlsx"
)
CENSUS_PATH = ROOT / "CENSUS 2011-A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.xlsx"
MASTER_OUT = PROCESSED_DIR / "official_district_year_master.csv"
HMIS_EXPORT = ROOT / "official data" / "extracted" / "hmis_child_burden_vulnerability_district_year.csv"


def load_all_cgwb_district_year() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for p in sorted(RAW_GW.glob("cgwb_bihar_wells_*.csv")):
        wells = pd.read_csv(p)
        if wells.empty:
            continue
        frames.append(aggregate_cgwb_by_district_year(wells))
    if not frames:
        raise FileNotFoundError(
            f"No cgwb_bihar_wells_*.csv in {RAW_GW}. Run scripts/extract_cgwb_bihar_csvs.py first."
        )
    all_gw = pd.concat(frames, ignore_index=True)
    return (
        all_gw.groupby(["District", "Year"], as_index=False)
        .agg(
            n_wells=("n_wells", "sum"),
            pH_mean=("pH_mean", "mean"),
            EC_median=("EC_median", "median"),
            HCO3_median=("HCO3_median", "median"),
            Cl_median=("Cl_median", "median"),
            SO4_median=("SO4_median", "median"),
            NO3_median=("NO3_median", "median"),
            F_median=("F_median", "median"),
            TDS_median=("TDS_median", "median"),
        )
    )


def main() -> None:
    ensure_directories()
    gw = load_all_cgwb_district_year()
    gw["District"] = standardize_district_names(gw["District"])

    hmis, ind_found = build_hmis_vulnerability_panel(HMIS_PATH)
    HMIS_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    hmis.to_csv(HMIS_EXPORT, index=False)
    print("HMIS vulnerability indicators matched:", ind_found)

    pop = load_bihar_district_population_2011(CENSUS_PATH)
    hmis = hmis.merge(pop, on="District", how="left")
    hmis["HMIS_burden_per_100k"] = hmis["HMIS_burden_raw"] / hmis["Population_2011"] * 100_000.0
    hmis["Target_log_burden_per100k"] = np.log1p(hmis["HMIS_burden_per_100k"].clip(lower=0))

    merged = gw.merge(hmis, on=["District", "Year"], how="inner")
    merged = merged.rename(
        columns={
            "pH_mean": "GW_pH_median",
            "EC_median": "GW_EC_uScm_median",
            "HCO3_median": "GW_HCO3_median",
            "Cl_median": "GW_Cl_median",
            "SO4_median": "GW_SO4_median",
            "NO3_median": "GW_NO3_median",
            "F_median": "GW_F_mgL_median",
            "TDS_median": "GW_TDS_median",
        }
    )
    try:
        merged["High_risk_tercile"] = pd.qcut(
            merged["HMIS_burden_per_100k"],
            q=3,
            labels=["low", "mid", "high"],
            duplicates="drop",
        )
    except ValueError:
        merged["High_risk_tercile"] = pd.NA

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    merged.to_csv(MASTER_OUT, index=False)
    print(f"Wrote {MASTER_OUT} ({len(merged)} rows).")
    print("Districts:", merged["District"].nunique(), "Year range:", merged["Year"].min(), "-", merged["Year"].max())
    if merged.empty:
        raise SystemExit("Merged table is empty — check district/year alignment.")


if __name__ == "__main__":
    main()
