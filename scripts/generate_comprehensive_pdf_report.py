"""
Generate a long-form PDF report: full project definition, all metrics, figures, FAQ.

Usage (from repo root):
  .venv\\Scripts\\python.exe scripts\\generate_comprehensive_pdf_report.py

Output:
  results/reports/Bihar_Major_Project_Comprehensive_Report.pdf
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import fpdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FIGURES_DIR = ROOT / "results" / "figures"
MODELS_DIR = ROOT / "results" / "models"
REPORTS_DIR = ROOT / "results" / "reports"
OUT_PDF = REPORTS_DIR / "Bihar_Major_Project_Comprehensive_Report.pdf"

def T(text: str) -> str:
    """ASCII-safe text for PDF core fonts (Helvetica)."""
    return (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u00b2", "^2")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u03c1", "rho")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


class PDF(fpdf.FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(left=18, top=18, right=18)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def multi(pdf: PDF, text: str, size: int = 10, bold: bool = False) -> None:
    pdf.set_font("Helvetica", "B" if bold else "", size)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.epw, 5, T(text))
    pdf.ln(1)


def heading(pdf: PDF, title: str, level: int = 1) -> None:
    pdf.ln(3 if level == 1 else 2)
    sz = {1: 15, 2: 13, 3: 11}[level]
    pdf.set_font("Helvetica", "B", sz)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.epw, 7, T(title))
    pdf.ln(1)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def susceptibility_summary(csv_path: Path) -> str:
    import pandas as pd

    if not csv_path.exists():
        return "district_susceptibility_profile.csv not found; run scripts/run_pipeline.py first."
    df = pd.read_csv(csv_path)
    n = len(df)
    env_y = (df.get("Environmental_susceptibility_high_stress_YN") == "Yes").sum()
    hmis_y = (df.get("HMIS_observed_high_burden_YN") == "Yes").sum()
    both = (
        (df.get("Environmental_susceptibility_high_stress_YN") == "Yes")
        & (df.get("HMIS_observed_high_burden_YN") == "Yes")
    ).sum()
    env_only = (
        (df.get("Environmental_susceptibility_high_stress_YN") == "Yes")
        & (df.get("HMIS_observed_high_burden_YN") != "Yes")
    ).sum()
    hmis_only = (
        (df.get("Environmental_susceptibility_high_stress_YN") != "Yes")
        & (df.get("HMIS_observed_high_burden_YN") == "Yes")
    ).sum()
    lines = [
        f"Rows (district-years): {n}",
        f"Environmental high-stress Yes: {int(env_y)} ({100 * env_y / max(n, 1):.1f}%)",
        f"HMIS observed high burden Yes: {int(hmis_y)} ({100 * hmis_y / max(n, 1):.1f}%)",
        f"Both Yes (stress + high HMIS tertile): {int(both)}",
        f"Environmental Yes only (HMIS not high): {int(env_only)}",
        f"HMIS high only (environmental not top tertile): {int(hmis_only)}",
    ]
    return "\n".join(lines)


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics_path = MODELS_DIR / "metrics.json"
    sus_csv = MODELS_DIR / "district_susceptibility_profile.csv"
    sus_def = MODELS_DIR / "susceptibility_definitions.json"

    metrics = load_json(metrics_path) if metrics_path.exists() else {}
    sus_defs = load_json(sus_def) if sus_def.exists() else {}

    pdf = PDF()
    pdf.set_title(T("Bihar Official Data Integration and Spatial ML Audit"))

    # ----- Cover -----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.ln(36)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        pdf.epw,
        9,
        T(
            "Bihar Groundwater (CGWB) and Child Health Burden (HMIS):\n"
            "Official Data Integration, Spatial Machine Learning, and District Susceptibility Profiles"
        ),
        align="C",
    )
    pdf.ln(14)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        pdf.epw,
        6,
        T(
            "Comprehensive technical report: methodology, quantitative results, figures, susceptibility outputs, FAQ."
        ),
        align="C",
    )
    pdf.ln(24)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        pdf.epw,
        5,
        T(f"Artefacts: data/processed/, results/models/, results/figures/, results/reports/\nPDF: {OUT_PDF}"),
        align="C",
    )

    # ----- TOC -----
    pdf.add_page()
    heading(pdf, "Table of contents", 1)
    toc = [
        "1. Purpose and claims",
        "2. Complete project definition",
        "3. Data sources and file locations",
        "4. End-to-end pipeline (how to reproduce)",
        "5. Variables: features, target, derived columns",
        "6. Statistical and ML methodology",
        "7. Quantitative results (metrics explained)",
        "8. SHAP and feature importance",
        "9. Missing data",
        "10. Susceptibility profiles (Yes/No outputs)",
        "11. Figures (all result plots)",
        "12. Anticipated questions and answers (FAQ)",
        "13. Limitations and ethical framing",
        "14. Appendix: artefact checklist",
    ]
    pdf.set_font("Helvetica", "", 11)
    for line in toc:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 6, T(line))
    pdf.ln(4)

    # ----- 1 Purpose -----
    pdf.add_page()
    heading(pdf, "1. Purpose and claims", 1)
    multi(
        pdf,
        "This project builds a reproducible pipeline that merges official Central Ground Water Board (CGWB) "
        "district-year groundwater summaries, HMIS Bihar child-health indicators, and Census 2011 district "
        "population into a single district-year table. Machine learning (Ridge, Random Forest, XGBoost) is "
        "trained with GroupKFold by district so test folds never contain districts seen during training "
        "(spatial generalisation stress test). Outputs include cross-validated metrics, out-of-fold predictions, "
        "SHAP-based explanations, publication-style figures, and district-year susceptibility profiles that "
        "separate environmental stress (CGWB-relative) from observed HMIS burden tiers.",
    )
    multi(
        pdf,
        "Primary claim: transparent integration and honest evaluation under spatial blocking. We do not claim "
        "that groundwater chemistry alone forecasts HMIS burden with high accuracy on unseen districts.",
        bold=True,
    )

    # ----- 2 Project definition -----
    pdf.add_page()
    heading(pdf, "2. Complete project definition", 1)
    multi(
        pdf,
        "Problem domain: ecological (district-year) association between environmental groundwater summaries "
        "and administrative health burden proxies in Bihar. Unit of analysis: one row per District x Year after "
        "inner merge of CGWB aggregates and HMIS panel.",
    )
    multi(
        pdf,
        "Software stack: Python 3; pandas; scikit-learn; optional XGBoost; SHAP; matplotlib; joblib; openpyxl "
        "for HMIS/Census reads; pymupdf used elsewhere for PDF extraction workflows.",
    )
    multi(
        pdf,
        "Core Python package: bihar_health_risk (config, dataio, preprocess, train, explain, viz, susceptibility). "
        "CLI entry: scripts/run_pipeline.py or python -m bihar_health_risk.",
    )

    # ----- 3 Data -----
    pdf.add_page()
    heading(pdf, "3. Data sources and file locations", 1)
    multi(
        pdf,
        "Groundwater: CGWB Bihar well extracts stored under data/raw_groundwater/cgwb_bihar_wells_YYYY.csv "
        "(built via scripts/extract_cgwb_bihar_csvs.py). Aggregated to district-year medians/means and merged.",
    )
    multi(
        pdf,
        "HMIS: district-year indicators from the official HMIS workbook (see repository path used in "
        "scripts/build_official_master_dataset.py). Burden composite sums selected child-health indicators "
        "under a fixed facility rollup (Total category).",
    )
    multi(
        pdf,
        "Census 2011: district population for Bihar used as denominator for burden per 100k (static across years "
        "until projected populations are added).",
    )
    multi(
        pdf,
        "Master training table: data/processed/official_district_year_master.csv (built by "
        "scripts/build_official_master_dataset.py).",
        bold=True,
    )

    # ----- 4 Pipeline -----
    pdf.add_page()
    heading(pdf, "4. End-to-end pipeline (reproduction)", 1)
    multi(
        pdf,
        "Typical order:\n"
        "(1) python scripts/extract_cgwb_bihar_csvs.py\n"
        "(2) python scripts/build_official_master_dataset.py\n"
        "(3) python scripts/run_pipeline.py\n\n"
        "run_pipeline.py loads the master CSV, writes missingness.csv, trains models with spatial CV, saves "
        "metrics.json, best_model.joblib, oof_predictions.csv, shap_importance.csv, intervention_priority_top15.csv, "
        "figures under results/figures/, and district-level susceptibility CSV/JSON.",
    )

    # ----- 5 Variables -----
    pdf.add_page()
    heading(pdf, "5. Variables", 1)
    heading(pdf, "5.1 Features (X)", 2)
    feats = sus_defs.get("gw_features_used", metrics.get("gw_features_used", []))
    if not feats:
        feats = [
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
    multi(pdf, "Groundwater / monitoring features:\n- " + "\n- ".join(feats))
    heading(pdf, "5.2 Target (y)", 2)
    multi(
        pdf,
        "Target_log_burden_per100k = log(1 + HMIS_burden_per_100k), where HMIS_burden_per_100k is the composite "
        "HMIS raw burden sum divided by Census 2011 district population times 100,000. Log stabilises skewed rates.",
    )
    heading(pdf, "5.3 Other columns used in susceptibility / reporting", 2)
    multi(
        pdf,
        "High_risk_tercile: tertiles of HMIS_burden_per_100k when computable. HMIS_vulnerability_z: mean z-score "
        "of log1p(indicator counts) across selected HMIS indicators.",
    )

    # ----- 6 Methods -----
    pdf.add_page()
    heading(pdf, "6. Methodology", 1)
    multi(
        pdf,
        "Preprocessing: numeric coercion, median imputation inside sklearn pipelines, optional clipping of "
        "non-negative GW constituents. Ridge uses scaled features; tree models use unscaled imputed features.",
    )
    multi(
        pdf,
        "Spatial cross-validation: GroupKFold grouped by District. Number of splits is capped by district count "
        "(requested 5 folds when possible). This prevents leaking geographic structure across train and test.",
    )
    multi(
        pdf,
        "Models compared: Ridge regression; Random Forest regressor; XGBoost regressor if installed. Best model "
        "chosen by lowest mean validation RMSE across folds; final pipeline refit on all rows for deployment artefacts.",
    )
    multi(
        pdf,
        "Explainability: SHAP TreeExplainer / LinearExplainer on transformed feature matrix; mean absolute SHAP "
        "exported to results/models/shap_importance.csv and summary bar plot saved as results/figures/shap_summary.png.",
    )

    # ----- 7 Results -----
    pdf.add_page()
    heading(pdf, "7. Quantitative results", 1)
    pf = metrics.get("project_framing", {})
    if pf:
        heading(pdf, "7.1 Project framing (embedded in metrics.json)", 2)
        multi(pdf, "Primary goal:\n" + pf.get("primary_goal", ""))
        multi(pdf, "Success criteria:\n- " + "\n- ".join(pf.get("success_criteria", [])))
        multi(pdf, "Why fold R2 can be negative:\n" + pf.get("why_fold_r2_can_be_negative", ""))

    heading(pdf, "7.2 Dataset scale", 2)
    multi(
        pdf,
        f"Districts: {metrics.get('n_districts', 'N/A')}\n"
        f"District-year rows used after target handling: {metrics.get('n_rows', 'N/A')}\n"
        f"Spatial CV folds: {metrics.get('spatial_cv_splits', 'N/A')}\n"
        f"Selected best model (by mean CV RMSE): {metrics.get('best_model', 'N/A')}",
    )

    heading(pdf, "7.3 Pooled out-of-fold metrics (best model)", 2)
    pm = metrics.get("pooled_oof_metrics_best_model", {})
    if pm:
        multi(
            pdf,
            "These summarise all rows using out-of-fold predictions from the selected model (RF in latest run).\n"
            f"- RMSE (pooled OOF): {pm.get('rmse')}\n"
            f"- R2 (pooled OOF vs global mean of y): {pm.get('r2')}\n"
            f"- Spearman rho (rank correlation): {pm.get('spearman_r')}\n"
            f"- Spearman two-sided p-value: {pm.get('spearman_p_two_sided')}\n"
            f"- Naive baseline RMSE (predict global mean y): {pm.get('naive_mean_baseline_rmse')}\n"
            f"- RMSE improvement vs naive (%): {pm.get('rmse_improvement_vs_naive_pct')}\n\n"
            "Interpretation: negative improvement vs naive means the model's OOF RMSE is worse than always "
            "predicting the training-set mean of the target. That is consistent with weak marginal predictive "
            "signal from groundwater-only features under strict spatial holdout; it is reported explicitly rather "
            "than hidden.",
        )

    heading(pdf, "7.4 Fold-averaged CV by model", 2)
    for row in metrics.get("cv_by_model", []):
        multi(
            pdf,
            f"Model {row.get('model')}: mean RMSE={row.get('rmse_mean')}, mean MAE={row.get('mae_mean')}, "
            f"mean fold R2={row.get('r2_mean')}",
        )

    # ----- 8 SHAP -----
    pdf.add_page()
    heading(pdf, "8. SHAP importance (mean absolute SHAP)", 1)
    shap_path = MODELS_DIR / "shap_importance.csv"
    if shap_path.exists():
        with shap_path.open(encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                multi(pdf, f"{row.get('feature')}: {row.get('mean_abs_shap')}")
    multi(
        pdf,
        "Reading guide: larger mean |SHAP| means the model relied more on that feature when explaining deviations "
        "from baseline prediction on the training distribution. This is not causal attribution.",
    )

    # ----- 9 Missing -----
    pdf.add_page()
    heading(pdf, "9. Missingness (training columns)", 1)
    miss_path = MODELS_DIR / "missingness.csv"
    if miss_path.exists():
        with miss_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                multi(pdf, f"{row['column']}: missing_n={row['missing_n']}, missing_pct={float(row['missing_pct']):.2f}%")
    multi(
        pdf,
        "Note: GW_TDS_median had notable missing share in the latest run; trees and imputers still run but "
        "interpretation should acknowledge reduced information on TDS for many rows.",
    )

    # ----- 10 Susceptibility -----
    pdf.add_page()
    heading(pdf, "10. Susceptibility profiles", 1)
    multi(
        pdf,
        "File: results/models/district_susceptibility_profile.csv\n"
        "Definitions JSON: results/models/susceptibility_definitions.json\n\n"
        + sus_defs.get("definition_environmental_yes", "")
        + "\n\n"
        + sus_defs.get("definition_hmis_high_yes", ""),
    )
    heading(pdf, "10.1 Summary counts from latest CSV", 2)
    multi(pdf, susceptibility_summary(sus_csv))
    heading(pdf, "10.2 HMIS indicators in composite", 2)
    for ind in sus_defs.get("hmis_indicators", []):
        pdf.set_font("Helvetica", "", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 4, T("- " + ind))
    pdf.ln(2)

    # ----- 11 Figures -----
    figures = sorted(FIGURES_DIR.glob("*.png"))
    captions = {
        "actual_vs_predicted.png": (
            "Figure: Actual vs predicted (spatial CV, out-of-fold). Each point is one district-year. "
            "x-axis: observed Target_log_burden_per100k; y-axis: model prediction when that row was in a "
            "held-out district fold. Scatter around the diagonal reflects weak out-of-sample skill."
        ),
        "residuals.png": (
            "Figure: Residuals vs predicted values for OOF predictions. Checks systematic bias; funnel shapes "
            "may indicate heteroscedasticity."
        ),
        "top_districts_pred.png": (
            "Figure: Districts with highest out-of-fold predicted target under the selected model. Useful for "
            "relative ranking discussion; not a clinical severity certificate."
        ),
        "shap_summary.png": (
            "Figure: SHAP summary (bar). Mean absolute SHAP value per groundwater/monitoring feature for the "
            "chosen model class."
        ),
    }
    for img_path in figures:
        pdf.add_page()
        heading(pdf, "11. Figure: " + img_path.name, 1)
        cap = captions.get(img_path.name, "Project figure output.")
        multi(pdf, cap)
        pdf.ln(2)
        try:
            pdf.image(str(img_path), x=12, w=186)
        except Exception as exc:
            multi(pdf, f"(Image render skipped: {exc})")

    # ----- 12 FAQ -----
    pdf.add_page()
    heading(pdf, "12. FAQ: anticipated examination questions", 1)
    faq: list[tuple[str, str]] = [
        (
            "What is the research question?",
            "Whether official groundwater summaries co-move with district-year HMIS child-health burden proxies "
            "when evaluated honestly at district scale, and whether we can produce transparent prioritisation "
            "artefacts from official data.",
        ),
        (
            "Why district-year units?",
            "CGWB reporting and HMIS reporting align naturally at district administrative resolution for Bihar; "
            "year allows temporal variation where both sides exist.",
        ),
        (
            "Why log burden target?",
            "Raw counts scale with population; rates per 100k reduce population dominance; log1p reduces skew "
            "from heavy-tailed rates.",
        ),
        (
            "What is spatial GroupKFold?",
            "Cross-validation where entire districts are held out together so the model cannot memorise district-specific "
            "patterns that do not generalise geographically.",
        ),
        (
            "Why is mean fold R2 negative?",
            "Small held-out sets and weak transferable signal make predictions worse than predicting the fold mean "
            "of y in some folds; averaging negative fold R2 stays negative.",
        ),
        (
            "What is pooled OOF R2?",
            "R2 computed once using all out-of-fold predictions together vs the global mean of y; often smoother "
            "than averaging per-fold R2 but can still be negative.",
        ),
        (
            "Why compare to naive mean RMSE?",
            "If a model cannot beat predicting the dataset mean under spatial holdout, it signals thin predictive "
            "marginal signal from X for that validation regime.",
        ),
        (
            "Is Spearman rho near zero a failure?",
            "It indicates no meaningful rank alignment between OOF predictions and observed burden in this panel; "
            "consistent with weak GW-only association under spatial blocking.",
        ),
        (
            "What does environmental susceptibility Yes mean?",
            "Top tertile of cohort-relative groundwater/monitoring stress index (z-score blend). Not a diagnosis.",
        ),
        (
            "What does HMIS observed high burden Yes mean?",
            "Top tertile of HMIS composite burden per 100k among rows in the merged table when tertiles exist.",
        ),
        (
            "Can environmental Yes and HMIS No happen together?",
            "Yes. Groundwater stress can be high while HMIS composite tertile is not high for many reasons "
            "(other drivers dominate, reporting effects, timing mismatch, ecological fallacy).",
        ),
        (
            "Does SHAP prove causality?",
            "No. SHAP explains model dependence on features within the trained associations; confounding remains.",
        ),
        (
            "Why is TDS sometimes missing?",
            "Well-level extraction and aggregation can leave TDS absent for some district-years; pipeline imputes.",
        ),
        (
            "Why Census 2011 population for all years?",
            "Current master uses static denominator as approximation; projected populations would refine rates.",
        ),
        (
            "Is this project meaningless?",
            "No if framed correctly: it delivers reproducible official-data fusion, strict validation, and explicit "
            "reporting of weakness. It is not meaningful as a sole groundwater-to-illness oracle.",
        ),
        (
            "What would strengthen conclusions?",
            "Add socio-environmental covariates; refine population over time; consider count models with offsets; "
            "expand indicators carefully with HMIS string verification.",
        ),
        (
            "How do I regenerate everything?",
            "Run scripts/run_pipeline.py after ensuring official_district_year_master.csv exists.",
        ),
        (
            "Where are district Yes/No outputs?",
            "results/models/district_susceptibility_profile.csv plus susceptibility_definitions.json.",
        ),
        (
            "Which model was finally saved?",
            "best_model.joblib contains the pipeline refit on all rows; model_name recorded inside bundle.",
        ),
        (
            "What is ecological bias?",
            "District aggregates cannot support individual-level causal claims; associations may reflect confounders.",
        ),
    ]
    for q, a in faq:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 5, T("Q: " + q))
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 5, T("A: " + a))
        pdf.ln(2)

    # ----- 13 Limitations -----
    pdf.add_page()
    heading(pdf, "13. Limitations and ethical framing", 1)
    multi(
        pdf,
        "- Thin predictor set (groundwater only) vs multifactorial burden.\n"
        "- Administrative data artefacts (HMIS completeness; CGWB sampling intensity).\n"
        "- Static population denominator.\n"
        "- Small effective sample for strict spatial extrapolation.\n"
        "- Composite HMIS sum mixes pathways; interpretation is coarse.\n"
        "Ethical stance: avoid stigmatising districts; use outputs for prioritisation dialogues and hypothesis "
        "generation tied to official programmes, not blame assignment.",
    )

    # ----- 14 Appendix -----
    pdf.add_page()
    heading(pdf, "14. Appendix: artefact checklist", 1)
    artefacts = [
        "data/processed/official_district_year_master.csv",
        "results/models/metrics.json",
        "results/models/best_model.joblib",
        "results/models/oof_predictions.csv",
        "results/models/shap_importance.csv",
        "results/models/missingness.csv",
        "results/models/intervention_priority_top15.csv",
        "results/models/district_susceptibility_profile.csv",
        "results/models/susceptibility_definitions.json",
        "results/reports/District_Susceptibility_YesNo_Report.pdf",
        "results/reports/District_Susceptibility_YesNo_Report.md",
        "results/figures/actual_vs_predicted.png",
        "results/figures/residuals.png",
        "results/figures/top_districts_pred.png",
        "results/figures/shap_summary.png",
        "results/reports/Official_ML_Project_Report.md",
        "results/reports/Project_Changes_Detailed_Report.md",
        "results/reports/Bihar_Major_Project_Comprehensive_Report.pdf (this document)",
    ]
    for p in artefacts:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 4, T("- " + p))

    pdf.output(str(OUT_PDF))
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
