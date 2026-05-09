# Bihar official environmental–health data integration (spatial generalisation audit)

**Updated:** 2026-05-09  
**Core positioning:** This work is a **reproducible analytics pipeline** that joins **CGWB groundwater**, **HMIS child-health burden**, and **Census 2011** population into one district–year table, then runs **spatially blocked** ML with full transparency (metrics, out-of-fold predictions, SHAP). It is **not** positioned as a high-precision forecaster of HMIS outcomes from chemistry alone.

---

## 1. Project objective (what we claim)

| Claim | What we deliver |
|--------|------------------|
| **Official data fusion** | Scripted path from raw inputs → `data/processed/official_district_year_master.csv` |
| **Spatial honesty** | **GroupKFold by district**: models never see test districts during training—appropriate for “would this pattern hold elsewhere in Bihar?” |
| **Associational validation** | HMIS-derived **`Target_log_burden_per100k`** is a **referent** to ask whether groundwater covaries with burden at district scale—not a clinical prediction endpoint |
| **Interpretability** | SHAP + residual plots + saved OOF predictions for audit |

**What we do *not* claim:** That groundwater features alone should yield high **R²** when extrapolating to unseen districts. That bar is inappropriate for sparse ecological panels and thin \(X\).

---

## 2. Why weak correlation is expected—not a flaw

1. **Held-out districts** stress-test whether associations **transfer across space**. Local confounding (facilities, reporting, geography) often dominates; **negative per-fold R²** can appear even when the pipeline is correct.  
2. **Ecological units:** District–year aggregates mix many causal pathways; marginal correlation with one exposure layer is typically **small**.  
3. **HMIS noise:** Reporting and coverage vary; composite burden adds variance.  
4. **Thin predictors:** Models use **groundwater + monitoring intensity** only. Burden is multi-factorial by construction.

The evaluation therefore emphasises **naive baselines**, **pooled out-of-fold error**, and **rank alignment** (Spearman), not textbook **R²** on tiny folds.

See **`results/models/metrics.json`** → `project_framing` and `pooled_oof_metrics_best_model`.

---

## 3. Target and features (unchanged technically)

- **Target:** `Target_log_burden_per100k` = log(1 + HMIS composite burden per 100k), denominator Census 2011 district population (static across years until projections are added).  
- **Features:** CGWB district–year medians (`GW_*`, `n_wells`).  
- **Also in table for analysis:** `HMIS_vulnerability_z`, `High_risk_tercile` (where supported).

---

## 4. Data sources

| Layer | Role | Location |
|--------|------|----------|
| CGWB groundwater | Exposure features | `data/raw_groundwater/cgwb_bihar_wells_*.csv` |
| HMIS Bihar | Burden + vulnerability fields | Extract → `official data/extracted/hmis_child_burden_vulnerability_district_year.csv` |
| Census 2011 | Population for rates | `CENSUS 2011-A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.xlsx` |
| **Master table** | Panel for ML | `data/processed/official_district_year_master.csv` |

---

## 5. How to run

```text
python scripts/extract_cgwb_bihar_csvs.py    # if rebuilding GW extracts
python scripts/build_official_master_dataset.py
python scripts/run_pipeline.py
```

Artifacts: `results/models/*`, `results/figures/*`.

---

## 6. Reading the metrics file

- **`project_framing`:** Study intent and why fold-wise **R²** is secondary.  
- **`pooled_oof_metrics_best_model`:** Single summary on **all** out-of-fold predictions for the selected model—**RMSE**, **R²**, **Spearman ρ**, **RMSE vs predicting the global mean** (`naive_mean_baseline_rmse`, `rmse_improvement_vs_naive_pct`).  
  If **`rmse_improvement_vs_naive_pct`** is **negative**, the spatially blocked model does **not** beat “always predict the training-set mean”—that is an **honest finding** for groundwater-only features and strengthens the message that this is **not** a forecasting product.  
- **`cv_by_model`:** Fold-averaged RMSE/MAE/R² for method comparison (R² here is a **strict diagnostic**, not the headline).

---

## 7. Recommended extensions (if you want stronger associational signal)

1. Add district/year covariates (rainfall, sanitation, literacy, WASH proxies).  
2. Replace static 2011 population with projected populations by year.  
3. Poisson / Negative Binomial on counts with **log(population) offset**.  
4. Classification on `High_risk_tercile` with ROC-AUC under the same spatial CV.

---

## 8. District-level Yes/No style outputs (presentation-friendly)

These files **do not rely on regression accuracy**. They summarise **(A) cohort-relative groundwater stress** and **(B) observed HMIS burden tertiles** where available.

**Read these first for Yes/No answers for every district-year:**

| Output | Path |
|--------|------|
| **Full Yes/No report (PDF)** | **`results/reports/District_Susceptibility_YesNo_Report.pdf`** |
| **Full Yes/No report (Markdown table)** | **`results/reports/District_Susceptibility_YesNo_Report.md`** |
| Raw data table (CSV) | `results/models/district_susceptibility_profile.csv` |
| Plain-language definitions | `results/models/susceptibility_definitions.json` |
| **Frozen reference for future years** | **`results/models/susceptibility_reference.json`** |

Both reports are **regenerated automatically** when you run `python scripts/run_pipeline.py`.

### 8.1 Naya year / nayi rows — susceptibility kaise “predict” hoti hai?

Pehle wala PDF/CSV **reference cohort** (jo master training rows hain) par tertiles banata hai. **Naye saal** ke liye alag rule hai taaki tum purane data ke **same scale** par jawab pao:

1. **`run_pipeline.py`** chalao → **`susceptibility_reference.json`** save hota hai: har GW feature ka **frozen mean/std** + **`Environmental_exposure_index` ke tertile bin edges** (+ optional HMIS burden rate ke bin edges).
2. Naya CSV banao: **`District`**, **`Year`**, aur reference JSON mein jo **`gw_cols`** hain unke **same columns** (CGWB medians + `n_wells`).
3. Command:

```bash
python scripts/predict_susceptibility_new_year.py \
  --reference results/models/susceptibility_reference.json \
  --input path/to/your_new_district_year_rows.csv \
  -o results/models/susceptibility_new_predictions.csv
```

**Web UI (Streamlit):** project root se `streamlit run streamlit_app.py` — CSV upload / manual row se susceptibility + ML prediction browser mein.

- **Environmental Yes/No:** nayi row ke GW values → **purane cohort ke mean/std se z-score** → **purane cohort ke hi tertile cutoffs** par Low/Medium/**High** → **High = Yes**.
- **HMIS Yes/No:** sirf tab jab tum input mein **`HMIS_burden_per_100k`** doge *aur* reference mein HMIS bins ban paaye hon; warna output mein explicitly **`N/A (add HMIS_burden_per_100k …)`** likha aata hai. Sirf GW doge to **environmental jawab phir bhi milega**.

Reference ko update karna = master data badhakar **dobara pipeline** chalana (naya cohort → nayi thresholds).

**Environmental `Environmental_susceptibility_high_stress_YN`:** **Yes** if that district–year sits in the **top tertile** of `Environmental_exposure_index` (mean of z-scores vs all rows on CGWB medians + log well count). **Top_GW_stress_1..3** name the three chemistry/monitoring metrics most **shifted from the Bihar cohort** for that row (with z in brackets)—use this to say *“isolated high nitrate / TDS / … vs peers”*, not *“ML predicted illness”*.

**HMIS `HMIS_observed_high_burden_YN`:** **Yes** if `High_risk_tercile` is **high** (top third of observed composite burden per 100k). Indicator names summed into the composite are listed in `HMIS_indicator_list_reference` on each row and fully in `susceptibility_definitions.json`.

---

## 9. Artifacts

| Output | Path |
|--------|------|
| Master CSV | `data/processed/official_district_year_master.csv` |
| Metrics (incl. framing + pooled OOF) | `results/models/metrics.json` |
| OOF predictions | `results/models/oof_predictions.csv` |
| Fitted bundle | `results/models/best_model.joblib` |
| Figures | `results/figures/*.png` |
| Susceptibility CSV + defs | `results/models/district_susceptibility_profile.csv`, `susceptibility_definitions.json` |
| Frozen reference (new years) | `results/models/susceptibility_reference.json` |
| CLI new-year scoring | `scripts/predict_susceptibility_new_year.py` |
| **Yes/No reports** | **`results/reports/District_Susceptibility_YesNo_Report.pdf`**, **`District_Susceptibility_YesNo_Report.md`** |

---

*Framing summary: **integration + spatial audit + interpretability**; HMIS outcomes provide context, not a promise of accurate prediction from groundwater chemistry alone.*
