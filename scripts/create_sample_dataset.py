"""
Create a small synthetic Bihar-style district panel for pipeline testing.

Values are NOT real survey measurements — replace with extracted official tables
(NFHS, CGWB, IMD, Census) before reporting results.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bihar_health_risk.config import (  # noqa: E402
    DEFAULT_FEATURE_COLS,
    SAMPLE_DIR,
    TARGET_COL,
    YEAR_COL,
    ensure_directories,
)
from bihar_health_risk.config import DISTRICT_COL  # noqa: E402

# 2011 Bihar district names (38) — for join testing with real extracts
DISTRICTS = [
    "Araria",
    "Arwal",
    "Aurangabad",
    "Banka",
    "Begusarai",
    "Bhagalpur",
    "Bhojpur",
    "Buxar",
    "Darbhanga",
    "Gaya",
    "Gopalganj",
    "Jamui",
    "Jehanabad",
    "Kaimur (Bhabua)",
    "Katihar",
    "Khagaria",
    "Kishanganj",
    "Lakhisarai",
    "Madhepura",
    "Madhubani",
    "Munger",
    "Muzaffarpur",
    "Nalanda",
    "Nawada",
    "Patna",
    "Purnia",
    "Rohtas",
    "Saharsa",
    "Samastipur",
    "Saran",
    "Sheikhpura",
    "Sheohar",
    "Sitamarhi",
    "Siwan",
    "Supaul",
    "Vaishali",
    "Pashchim Champaran",
    "Purbi Champaran",
]


def main() -> Path:
    ensure_directories()
    rng = np.random.default_rng(42)
    n = len(DISTRICTS)

    monsoon = rng.normal(950, 140, n).clip(500, 1400)
    arsenic = rng.lognormal(3.2, 0.85, n).clip(0, 500)
    fluoride = rng.gamma(1.2, 0.35, n).clip(0, 4)
    nitrate = rng.gamma(8, 3, n).clip(0, 150)
    od = rng.uniform(15, 65, n)
    toilet = 100 - od - rng.uniform(0, 15, n)
    toilet = np.clip(toilet, 5, 95)
    popd = rng.uniform(400, 1800, n)
    literacy = rng.uniform(48, 82, n)

    # Synthetic stunting: higher with arsenic + OD + low toilet; noise
    z = (
        22
        + 0.012 * arsenic
        + 0.15 * od
        - 0.12 * toilet
        + 0.0008 * monsoon
        - 0.08 * literacy
        + rng.normal(0, 4, n)
    )
    stunting = np.clip(z, 18, 55)

    df = pd.DataFrame(
        {
            DISTRICT_COL: DISTRICTS,
            YEAR_COL: 2020,
            "Monsoon_Rainfall_mm": monsoon,
            "Arsenic_ppb": arsenic,
            "Fluoride_mgL": fluoride,
            "Nitrate_mgL": nitrate,
            "OpenDefec_pct": od,
            "ToiletCoverage_pct": toilet,
            "PopDensity_perSqkm": popd,
            "Literacy_pct": literacy,
            TARGET_COL: stunting,
        }
    )
    out = SAMPLE_DIR / "bihar_district_panel.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {out} ({len(df)} rows). Columns: {list(df.columns)}")
    print("Replace this file with merged official extracts for real analysis.")
    return out


if __name__ == "__main__":
    main()
