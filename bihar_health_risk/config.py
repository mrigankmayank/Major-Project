"""Paths and column names for the analysis pipeline."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_GW = DATA_DIR / "raw_groundwater"
RAW_CLIMATE = DATA_DIR / "raw_climate"
RAW_HEALTH = DATA_DIR / "raw_health"
RAW_CENSUS = DATA_DIR / "raw_census"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLE_DIR = DATA_DIR / "sample"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
MODELS_DIR = RESULTS_DIR / "models"

DEFAULT_SAMPLE_CSV = SAMPLE_DIR / "bihar_district_panel.csv"
# Official CGWB + HMIS merged training table (see scripts/build_official_master_dataset.py)
OFFICIAL_MASTER_CSV = PROCESSED_DIR / "official_district_year_master.csv"
DEFAULT_MERGED_CSV = OFFICIAL_MASTER_CSV

DISTRICT_COL = "District"
YEAR_COL = "Year"
# log1p(HMIS multi-indicator child burden / Census 2011 population * 1e5)
TARGET_COL = "Target_log_burden_per100k"

# CGWB district–year medians + monitoring intensity
DEFAULT_FEATURE_COLS = [
    "GW_pH_median",
    "GW_EC_uScm_median",
    "GW_HCO3_median",
    "GW_Cl_median",
    "GW_SO4_median",
    "GW_NO3_median",
    "GW_F_mgL_median",
    "GW_TDS_median",
    "n_wells",
]


def ensure_directories() -> None:
    for p in (
        RAW_GW,
        RAW_CLIMATE,
        RAW_HEALTH,
        RAW_CENSUS,
        PROCESSED_DIR,
        SAMPLE_DIR,
        FIGURES_DIR,
        MODELS_DIR,
    ):
        p.mkdir(parents=True, exist_ok=True)
