"""Load and validate the district-level master table."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from bihar_health_risk.config import DISTRICT_COL, TARGET_COL, YEAR_COL


def load_master_table(path: Path | str) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Master table not found: {path}")
    if path.suffix.lower() in {".parquet", ".pq"}:
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    return df


def validate_columns(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    *,
    require_target: bool = True,
) -> None:
    missing = {DISTRICT_COL} - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {sorted(missing)}")
    if require_target and TARGET_COL not in df.columns:
        raise ValueError(f"Missing target column: {TARGET_COL}")
    feats = list(feature_cols)
    absent = [c for c in feats if c not in df.columns]
    if absent:
        raise ValueError(f"Feature columns not in data: {absent}")


def drop_rows_missing_target(df: pd.DataFrame) -> pd.DataFrame:
    if TARGET_COL not in df.columns:
        return df
    return df.dropna(subset=[TARGET_COL]).copy()


def get_X_y(
    df: pd.DataFrame,
    feature_cols: list[str],
    *,
    groups: str | None = DISTRICT_COL,
) -> tuple[pd.DataFrame, pd.Series, pd.Series | None]:
    """Return X, y, and optional group labels (same length) for spatial CV."""
    X = df[feature_cols].copy()
    y = df[TARGET_COL].astype(float).copy()
    if groups and groups in df.columns:
        g = df[groups].astype(str)
        return X, y, g
    return X, y, None


def missingness_report(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    n = len(df)
    for c in cols:
        na = df[c].isna().sum()
        rows.append({"column": c, "missing_n": int(na), "missing_pct": 100.0 * na / n if n else 0.0})
    return pd.DataFrame(rows).sort_values("missing_pct", ascending=False)
