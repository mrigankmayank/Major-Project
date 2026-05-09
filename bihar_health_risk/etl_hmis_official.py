"""HMIS (Bihar) extracts for merging with environmental features."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Official HMIS indicator used as child nutrition / morbidity burden proxy (absolute counts).
HMIS_SAM_INDICATOR = "Childhood Diseases - Severe Acute Malnutrition (SAM)"

# One row per district–year–indicator (avoids summing Rural+Urban+Public duplicates).
HMIS_FACILITY_ROLLUP = "Public and Private Facilities OR Rural and Urban Facilities"
HMIS_CATEGORY_TOTAL = "Total"


def fiscal_year_to_start_year(series: pd.Series) -> pd.Series:
    return series.astype(str).str.split("-").str[0].astype(int)


def load_hmis_sam_district_year(xlsx_path: Path) -> pd.DataFrame:
    """Return District, Year (fiscal start), HMIS_SAM_cases."""
    path = Path(xlsx_path)
    df = pd.read_excel(path, sheet_name=0)
    need = {
        "fiscal_year",
        "district_as_per_lgd",
        "indicator",
        "facility_category",
        "category",
        "value",
    }
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"HMIS file missing columns: {sorted(missing)}")
    sub = df[
        (df["indicator"] == HMIS_SAM_INDICATOR)
        & (df["facility_category"] == HMIS_FACILITY_ROLLUP)
        & (df["category"] == HMIS_CATEGORY_TOTAL)
    ].copy()
    sub["District"] = sub["district_as_per_lgd"].astype(str).str.strip().str.title()
    sub["Year"] = fiscal_year_to_start_year(sub["fiscal_year"])
    sub["HMIS_SAM_cases"] = pd.to_numeric(sub["value"], errors="coerce").fillna(0.0)
    out = sub[["District", "Year", "HMIS_SAM_cases", "fiscal_year"]].drop_duplicates()
    dup = out.duplicated(subset=["District", "Year"], keep=False)
    if dup.any():
        out = out.groupby(["District", "Year"], as_index=False).agg(
            HMIS_SAM_cases=("HMIS_SAM_cases", "sum"),
            fiscal_year=("fiscal_year", "first"),
        )
    return out
