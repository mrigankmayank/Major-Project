"""Merge multiple CSV extracts on District into data/processed/district_master.csv."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bihar_health_risk.config import PROCESSED_DIR  # noqa: E402
from bihar_health_risk.etl_merge import build_master_from_paths  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csvs", nargs="+", type=Path, help="CSV paths in merge order (first is base)")
    p.add_argument("-o", "--out", type=Path, default=PROCESSED_DIR / "district_master.csv")
    args = p.parse_args()
    df = build_master_from_paths(args.csvs, out_path=args.out)
    print(f"Merged {len(df)} rows -> {args.out}")


if __name__ == "__main__":
    main()
