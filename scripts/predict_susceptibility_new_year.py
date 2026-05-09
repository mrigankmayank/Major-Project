"""
Score NEW district-years for environmental (and optional HMIS) susceptibility using the
FROZEN reference cohort from training (results/models/susceptibility_reference.json).

Environmental Yes/No uses the same mean/std and tertile bin edges as the last pipeline run,
so results stay comparable to District_Susceptibility_YesNo_Report.

Usage:
  python scripts/predict_susceptibility_new_year.py \\
    --reference results/models/susceptibility_reference.json \\
    --input path/to/new_district_year_gw.csv \\
    -o results/models/susceptibility_prediction_output.csv

Input CSV must include: District, Year, and every GW column listed in the reference JSON.
Optional column: HMIS_burden_per_100k (if present and reference HMIS bins exist, HMIS Yes/No is filled).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bihar_health_risk.dataio import load_master_table  # noqa: E402
from bihar_health_risk.susceptibility import apply_frozen_reference_susceptibility  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Susceptibility Yes/No for new district-years (frozen reference)")
    p.add_argument(
        "--reference",
        type=Path,
        default=ROOT / "results" / "models" / "susceptibility_reference.json",
        help="JSON written by run_pipeline (frozen stats + bin edges)",
    )
    p.add_argument("--input", type=Path, required=True, help="CSV with District, Year, GW_* columns")
    p.add_argument("-o", "--out", type=Path, required=True, help="Output CSV path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not args.reference.exists():
        raise SystemExit(f"Reference not found: {args.reference}. Run scripts/run_pipeline.py first.")
    ref = json.loads(args.reference.read_text(encoding="utf-8"))
    df = load_master_table(args.input)
    out = apply_frozen_reference_susceptibility(df, ref)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"Wrote {args.out} ({len(out)} rows).")


if __name__ == "__main__":
    main()
