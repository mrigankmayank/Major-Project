"""Merge auxiliary CSV extracts into a single district master table."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from bihar_health_risk.config import DISTRICT_COL, PROCESSED_DIR


def standardize_district_names(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.replace("West Champaran", "Pashchim Champaran", regex=False)
        .str.replace("East Champaran", "Purbi Champaran", regex=False)
    )


def merge_on_district(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    how: str = "outer",
    suffixes: tuple[str, str] = ("", "_r"),
) -> pd.DataFrame:
    """Merge two frames that each contain DISTRICT_COL."""
    if DISTRICT_COL not in left.columns or DISTRICT_COL not in right.columns:
        raise ValueError(f"Both inputs need '{DISTRICT_COL}'.")
    L = left.copy()
    R = right.copy()
    L[DISTRICT_COL] = standardize_district_names(L[DISTRICT_COL])
    R[DISTRICT_COL] = standardize_district_names(R[DISTRICT_COL])
    return pd.merge(L, R, on=DISTRICT_COL, how=how, suffixes=suffixes)


def build_master_from_paths(paths: list[Path], out_path: Path | None = None) -> pd.DataFrame:
    """Sequentially outer-merge CSVs on district (first file is the base)."""
    if not paths:
        raise ValueError("paths must be non-empty")
    out_path = out_path or (PROCESSED_DIR / "district_master.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(paths[0])
    base[DISTRICT_COL] = standardize_district_names(base[DISTRICT_COL])
    for p in paths[1:]:
        nxt = pd.read_csv(p)
        nxt[DISTRICT_COL] = standardize_district_names(nxt[DISTRICT_COL])
        base = merge_on_district(base, nxt, how="outer")
    base.to_csv(out_path, index=False)
    return base
