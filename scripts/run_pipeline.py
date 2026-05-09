"""Generate sample data (if missing), train with spatial CV, SHAP, and figures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bihar_health_risk.config import (  # noqa: E402
    DEFAULT_FEATURE_COLS,
    DEFAULT_MERGED_CSV,
    DEFAULT_SAMPLE_CSV,
    DISTRICT_COL,
    FIGURES_DIR,
    MODELS_DIR,
    OFFICIAL_MASTER_CSV,
    TARGET_COL,
    ensure_directories,
)
from bihar_health_risk.dataio import load_master_table, missingness_report  # noqa: E402
from bihar_health_risk.explain import save_shap_summary, shap_importance_table  # noqa: E402
from bihar_health_risk.susceptibility import save_susceptibility_artifacts  # noqa: E402
from bihar_health_risk.train import run_training  # noqa: E402
from bihar_health_risk.viz import plot_actual_vs_predicted, plot_residuals, plot_top_district_risk  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bihar district health risk ML pipeline")
    p.add_argument(
        "--data",
        type=Path,
        default=None,
        help="CSV or Parquet master table (defaults to processed merge or sample)",
    )
    p.add_argument("--n-splits", type=int, default=5, help="GroupKFold splits (capped by #districts)")
    p.add_argument("--no-interactions", action="store_true", help="Disable rain × open defecation feature")
    p.add_argument(
        "--allow-sample",
        action="store_true",
        help="Fallback to synthetic sample only if official master is missing (not for research use)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ensure_directories()

    data_path = args.data
    if data_path is None:
        if OFFICIAL_MASTER_CSV.exists():
            data_path = OFFICIAL_MASTER_CSV
        elif args.allow_sample:
            data_path = DEFAULT_SAMPLE_CSV
        else:
            data_path = OFFICIAL_MASTER_CSV

    if not data_path.exists():
        import subprocess

        if args.allow_sample and data_path.resolve() == DEFAULT_SAMPLE_CSV.resolve():
            subprocess.run([sys.executable, str(ROOT / "scripts" / "create_sample_dataset.py")], check=True)
        else:
            print(
                "Official training data not found.\n"
                "  python scripts/extract_cgwb_bihar_csvs.py\n"
                "  python scripts/build_official_master_dataset.py\n"
                "Or pass --data path/to.csv  |  For demo only: --allow-sample"
            )
            sys.exit(1)

    df = load_master_table(data_path)
    miss = missingness_report(df, DEFAULT_FEATURE_COLS + [TARGET_COL])
    (MODELS_DIR / "missingness.csv").parent.mkdir(parents=True, exist_ok=True)
    miss.to_csv(MODELS_DIR / "missingness.csv", index=False)

    out = run_training(
        data_path,
        DEFAULT_FEATURE_COLS,
        n_splits=args.n_splits,
        use_interactions=not args.no_interactions,
        out_dir=MODELS_DIR,
    )

    pipe = out["fitted_pipeline"]
    X = out["X"]
    y = out["y"].values
    best_name = out["metrics"]["best_model"]
    oof_col = f"oof_pred_{best_name}"
    oof = out["oof_frame"][oof_col].values

    plot_actual_vs_predicted(
        y,
        oof,
        title=f"Spatial CV — {best_name} (out-of-fold)",
        out_path=FIGURES_DIR / "actual_vs_predicted.png",
    )
    plot_residuals(y, oof, out_path=FIGURES_DIR / "residuals.png")
    plot_top_district_risk(out["oof_frame"], oof_col, out_path=FIGURES_DIR / "top_districts_pred.png")

    save_shap_summary(pipe, X, best_name, out_path=FIGURES_DIR / "shap_summary.png")
    tbl = shap_importance_table(pipe, X, best_name)
    tbl.to_csv(MODELS_DIR / "shap_importance.csv", index=False)

    priority = (
        out["oof_frame"][[DISTRICT_COL, oof_col]]
        .dropna()
        .sort_values(oof_col, ascending=False)
        .head(15)
    )
    priority.to_csv(MODELS_DIR / "intervention_priority_top15.csv", index=False)

    prof_path, def_path, ref_path, yesno_pdf, yesno_md = save_susceptibility_artifacts(
        out["training_df"], out_dir=MODELS_DIR
    )

    print(json.dumps(out["metrics"], indent=2))
    print("Susceptibility profile (CSV):", prof_path)
    print("Susceptibility definitions (JSON):", def_path)
    print("Frozen reference for NEW years/rows (JSON):", ref_path)
    print("YES/NO report (PDF):", yesno_pdf)
    print("YES/NO report (Markdown):", yesno_md)
    print("Predict new GW rows:", "python scripts/predict_susceptibility_new_year.py --help")
    print("Artifacts:", MODELS_DIR, FIGURES_DIR)


if __name__ == "__main__":
    main()
