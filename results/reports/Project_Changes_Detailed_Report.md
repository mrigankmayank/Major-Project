# Detailed Report: Current Project Changes & Outputs

**Generated for:** Bihar environmental exposure & HMIS integration (Major Project)  
**Report date:** 2026-05-09  
**Purpose:** Single document summarising **what changed in code and artefacts**, **why**, and **how to present** results without over-claiming predictive accuracy.

---

## 1. Executive summary

The codebase was updated in three connected strands:

1. **Evaluation & narrative reframing** — `metrics.json` now embeds explicit **project goals**, **success criteria**, and **pooled out-of-fold** statistics compared to a **naive mean baseline**, plus **Spearman rank correlation**. Fold-wise **R²** is intentionally demoted from being the only headline metric.

2. **Documentation** — `Official_ML_Project_Report.md` was rewritten around **data fusion + spatial generalisation audit**, not “accurate forecasting from groundwater alone.”

3. **Presentation-oriented outputs** — New module **`bihar_health_risk/susceptibility.py`** writes **`district_susceptibility_profile.csv`** and **`susceptibility_definitions.json`**: district–year **Yes/No–style** flags for **environmental stress** (CGWB-based, cohort-relative) and **observed HMIS high burden**, plus **top three groundwater drivers** per row and **explicit HMIS indicator lists**.

Smaller fixes: `predict.py` output column renamed to match the real target; `config.py` comment clarified for `TARGET_COL`; `run_training()` now returns **`training_df`** so the pipeline can export susceptibility on the **same rows** used for training.

---

## 2. Files modified (by area)

### 2.1 Training & metrics — `bihar_health_risk/train.py`

| Change | Description |
|--------|-------------|
| **`scipy.stats.spearmanr`** | Computes rank correlation between observed target and out-of-fold predictions for the **best** CV model (entire sample, valid OOF only). |
| **Pooled OOF block** | After selecting `best` by mean fold RMSE: pooled **RMSE**, **R²**, **Spearman ρ** and **two-sided p-value**, **RMSE of naive predictor** (always predict global mean of **y**), and **% RMSE improvement vs naive** (negative ⇒ model worse than naive mean on this metric). |
| **`metrics.json` structure** | New keys: **`project_framing`** (primary goal, success criteria, explanation of negative fold **R²**), **`pooled_oof_metrics_best_model`** (object with fields listed below). Existing **`cv_by_model`** retained for Ridge / RF / XGB comparison. |
| **Return value** | **`training_df`**: processed `DataFrame` after merges, target drop, sanitisation—aligned with rows in **`X`**, **`y`**, and OOF CSV. |

**`pooled_oof_metrics_best_model` fields**

| Field | Meaning |
|-------|---------|
| `rmse` | Root mean squared error on target, all OOF predictions from best model. |
| `r2` | Sklearn **R²** on pooled OOF vs global mean of **y** (can remain negative). |
| `spearman_r` | Spearman correlation (rank alignment). |
| `spearman_p_two_sided` | Two-sided p-value for Spearman (interpret with caution at small **n**). |
| `naive_mean_baseline_rmse` | RMSE if every point were predicted by **mean(y)**. |
| `rmse_improvement_vs_naive_pct` | `100 × (naive_rmse − model_rmse) / naive_rmse`; negative ⇒ model does not beat naive mean on RMSE under spatial CV. |

### 2.2 Pipeline entrypoint — `scripts/run_pipeline.py`

| Change | Description |
|--------|-------------|
| **`save_susceptibility_artifacts`** | After training and figure export, calls **`save_susceptibility_artifacts(out["training_df"], out_dir=MODELS_DIR)`**. |
| **Console output** | Prints paths to **`district_susceptibility_profile.csv`** and **`susceptibility_definitions.json`**. |

### 2.3 Susceptibility module — `bihar_health_risk/susceptibility.py` *(new)*

| Component | Description |
|-----------|-------------|
| **`GW_LABELS`** | Human-readable names for CGWB feature columns (for CSV/slides). |
| **`HMIS_COMPOSITE_SUMMARY`** | Short prose listing what the HMIS composite aggregates (aligned with ETL intent). |
| **`build_susceptibility_profiles`** | Builds z-scores per GW feature ( **`log1p`** for **`n_wells`** ); **`Environmental_exposure_index`** = mean z-score; **tercile bands** Low / Medium / High; **`Environmental_susceptibility_high_stress_YN`** = **Yes** iff band is **High**; **top three** drivers by **absolute** z on GW features; HMIS tertile / high burden **Yes/No/Unknown** from **`High_risk_tercile`** when present; repeats **`HMIS_indicator_list_reference`** from **`HMIS_VULNERABILITY_INDICATORS`**. |
| **`save_susceptibility_artifacts`** | Writes **`district_susceptibility_profile.csv`** and **`susceptibility_definitions.json`** under **`results/models/`**. |

**Important:** Environmental Yes/No is **not** derived from regression predictions; it is **cohort-relative groundwater / monitoring stress**. That avoids defending weak ML correlation when answering “which districts look stressed on official GW summaries?”

### 2.4 Configuration — `bihar_health_risk/config.py`

| Change | Description |
|--------|-------------|
| **`TARGET_COL` comment** | Clarifies that the target is an **associational / modelling referent**, not solely a product-style forecasting endpoint. |

### 2.5 Prediction CLI — `bihar_health_risk/predict.py`

| Change | Description |
|--------|-------------|
| Output column | **`predicted_Stunting_pct`** renamed to **`predicted_Target_log_burden_per100k`** to match the actual supervised target used in training. |

### 2.6 Documentation — `results/reports/Official_ML_Project_Report.md`

| Change | Description |
|--------|-------------|
| **Repositioning** | Title and sections emphasise **official data integration**, **spatial honesty (GroupKFold by district)**, and limits of **GW-only** prediction. |
| **Metrics guidance** | Points readers to **`metrics.json`** → **`project_framing`** and **`pooled_oof_metrics_best_model`**; explains negative **% vs naive** as an **honest finding**, not a pipeline bug. |
| **Section 8–9** | New **district-level Yes/No outputs** section describing **`district_susceptibility_profile.csv`** and **`susceptibility_definitions.json`**; artefacts table updated. |

---

## 3. New / updated artefacts (after `python scripts/run_pipeline.py`)

| Artefact | Path | Role |
|----------|------|------|
| Metrics + framing | `results/models/metrics.json` | Full CV table + **project_framing** + **pooled_oof_metrics_best_model**. |
| Susceptibility table | `results/models/district_susceptibility_profile.csv` | District–year **environmental stress band**, **Yes/No**, **top 3 GW stresses**, **HMIS tertile / high burden Yes/No**, indicator text. |
| Definitions | `results/models/susceptibility_definitions.json` | Machine-readable definitions + HMIS indicator list + GW features used. |
| *(unchanged pipeline outputs)* | `best_model.joblib`, `oof_predictions.csv`, `shap_importance.csv`, `missingness.csv`, `intervention_priority_top15.csv`, `results/figures/*.png` | Same as before; regenerated each full run. |

---

## 4. Typical numeric snapshot (illustrative — re-run pipeline to refresh)

Current official panel scale (from last successful run): **33 districts**, **63 district–year rows**, **5** spatial folds; **best model by mean CV RMSE:** **Random Forest**.

**Pooled OOF (best model)** — interpret as “strict spatial honesty summarised on all held-out predictions”:

- Pooled **RMSE**, **R²**, **Spearman ρ** and **p-value** are stored in **`metrics.json`**.
- If **`rmse_improvement_vs_naive_pct`** is **negative**, the RF model’s OOF error is **larger** than predicting the **global mean** of the target — consistent with **thin predictors** and **held-out districts**.

**Susceptibility CSV** — use for slides:

- Rows show **`Environmental_susceptibility_high_stress_YN`** independent of ML fit quality.
- **`HMIS_observed_high_burden_YN`** reflects **observed** tertiles, not predicted illness.
- Examples may show **High** environmental stress with **No** high HMIS tertile (or the reverse), illustrating why **marginal GW→burden correlation** is not expected to be strong.

---

## 5. How to regenerate everything

From repository root (after activating your virtual environment and installing **`requirements.txt`**):

```bash
python scripts/run_pipeline.py
```

Equivalent:

```bash
python -m bihar_health_risk
```

Prerequisites: processed master table **`data/processed/official_district_year_master.csv`** (or pass **`--data`**). For rebuilding that table from raw extracts:

```bash
python scripts/extract_cgwb_bihar_csvs.py
python scripts/build_official_master_dataset.py
python scripts/run_pipeline.py
```

---

## 6. How to present this work (viva / report / slides)

**Suggested storyline**

1. **Problem:** Integrate **official** CGWB groundwater summaries with **HMIS** child-health burden and **Census** population into one auditable district–year dataset.

2. **Method:** Reproducible ETL → merged CSV → **spatial GroupKFold** (no leakage across districts) → Ridge / RF / XGB + SHAP.

3. **Honesty:** **Pooled OOF** metrics and **naive baseline** show that **GW-only** models **do not** necessarily outperform a trivial mean predictor under this validation — which is **informative**, not embarrassing.

4. **Stakeholder-friendly layer:** **`district_susceptibility_profile.csv`** gives **two lenses** — **environmental stress (CGWB)** and **observed burden tier (HMIS)** — with **top chemical/monitoring drivers** and **written HMIS composite contents**.

**Phrases to avoid**

- “AI predicts disease accurately from water.”  
- “High R² proves groundwater causes burden.”

**Phrases to use**

- “Official data fusion under spatial holdout.”  
- “Environmental screening vs cohort + HMIS observed tertiles for context.”  
- “Hypothesis generation and prioritisation, not clinical forecasting.”

---

## 7. Dependencies

No new packages were added beyond existing stack; **`scipy`** is used via **`spearmanr`** (already pulled in by **`scikit-learn`** in typical installs). **`requirements.txt`** unchanged as part of this workstream.

---

## 8. Summary table of source files touched

| File | Action |
|------|--------|
| `bihar_health_risk/train.py` | Extended metrics, `training_df` return, Spearman + pooled OOF + naive baseline. |
| `bihar_health_risk/susceptibility.py` | **New** — susceptibility profiles + JSON definitions. |
| `scripts/run_pipeline.py` | Calls susceptibility export after training. |
| `bihar_health_risk/config.py` | Comment on target. |
| `bihar_health_risk/predict.py` | Correct prediction column name. |
| `results/reports/Official_ML_Project_Report.md` | Major restructure + susceptibility section. |
| `results/reports/Project_Changes_Detailed_Report.md` | **This document.** |

---

*End of detailed change report.*
