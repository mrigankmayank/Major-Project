"""Imputation and simple transforms for mixed missingness."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def build_numeric_preprocessor(strategy: str = "median") -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy=strategy, add_indicator=False)),
        ]
    )


def add_exposure_interactions(df: pd.DataFrame) -> pd.DataFrame:
    """Optional interaction: monsoon × open defecation (flood + sanitation stress)."""
    out = df.copy()
    if "Monsoon_Rainfall_mm" in out.columns and "OpenDefec_pct" in out.columns:
        out["Rain_x_OpenDefec"] = (
            pd.to_numeric(out["Monsoon_Rainfall_mm"], errors="coerce")
            * pd.to_numeric(out["OpenDefec_pct"], errors="coerce")
            / 100.0
        )
    return out


def sanitize_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def clip_nonnegative(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c not in out.columns:
            continue
        s = pd.to_numeric(out[c], errors="coerce")
        out[c] = s.where(s.isna() | (s >= 0), np.nan)
    return out
