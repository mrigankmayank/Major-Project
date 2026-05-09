"""Load a saved pipeline and predict on a feature CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True, help="best_model.joblib from results/models")
    p.add_argument("--data", type=Path, required=True, help="CSV with same feature columns as training")
    p.add_argument("-o", "--out", type=Path, default=Path("predictions.csv"))
    args = p.parse_args()

    bundle = joblib.load(args.model)
    pipe = bundle["pipeline"]
    feats: list[str] = bundle["feature_cols"]
    df = pd.read_csv(args.data)
    missing = [c for c in feats if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns: {missing}")
    pred = pipe.predict(df[feats])
    out = df.copy()
    out["predicted_Stunting_pct"] = pred
    out.to_csv(args.out, index=False)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
