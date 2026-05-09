# Bihar environmental exposure & child-health vulnerability (official data)

**Updated:** 2026-05-02 (reframed target and HMIS layer)  
**Framing:** Explainable **district–year vulnerability** linked to **groundwater exposure**, not “predict raw SAM counts.”

---

## 1. Why the model was reframed

Earlier runs used **raw HMIS SAM counts** as the target. Counts are dominated by **district population**, so models mostly track size, not vulnerability. With **~63 district–year rows**, sparse signal, and **groundwater-only** predictors, spatial CV **R²** was negative.

**Changes made:**

1. **Target** is now **`Target_log_burden_per100k`** = **log(1 + HMIS burden rate per 100,000 population)**.  
   - **Burden** = sum of several official HMIS child-health indicators (same district–year, same HMIS rollup rule).  
   - **Denominator** = **Census 2011 district population** (`CENSUS 2011-A-1_...xlsx`), static across years (approximation until projected pops are added).

2. **Vulnerability score** **`HMIS_vulnerability_z`**: mean of **z-scores of log1p(count)** across those indicators (for ranking and interpretation; the primary supervised target is still the log-rate above).

3. **Optional label** **`High_risk_tercile`**: tertiles of `HMIS_burden_per_100k` when the distribution supports it (for future classification work).

4. Models remain **Ridge / Random Forest / XGBoost** on the **log-rate** (continuous, well-behaved). **Poisson / Negative Binomial** on raw counts with a population **offset** is a natural next step if you add `statsmodels` or sklearn pipelines with offsets.

---

## 2. Data sources

| Layer | Role | Location |
|--------|------|----------|
| CGWB groundwater | Exposure features (district × year medians, `n_wells`) | `official data/cgwb*.pdf` → `data/raw_groundwater/cgwb_bihar_wells_*.csv` |
| HMIS Bihar | Multi-indicator burden + `HMIS_vulnerability_z` | `14277- Dataful/...hmis...xlsx` → `official data/extracted/hmis_child_burden_vulnerability_district_year.csv` |
| Census 2011 | District population (Bihar, “Total” row) | `CENSUS 2011-A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.xlsx` |
| **Master table** | Training CSV | `data/processed/official_district_year_master.csv` |

**HMIS indicators currently summed into `HMIS_burden_raw`** (each with facility rollup `Public and Private Facilities OR Rural and Urban Facilities`, category `Total`):

- Childhood Diseases — SAM, Diarrhoea, Pneumonia, Measles  
- Infant deaths (1–12 months) due to Diarrhoea / Pneumonia  
- Child deaths (1–5 years) due to Diarrhoea / Pneumonia  
- Number of cases of Infant deaths within 24 hrs of birth  
- Number of still births  

*(Other labels you mentioned—e.g. maternal anemia, LBW—can be appended in `bihar_health_risk/etl_hmis_vulnerability.py` once exact HMIS strings are verified in your file.)*

---

## 3. Modeling setup

| Item | Detail |
|------|--------|
| Unit | District × Year |
| **y** | `Target_log_burden_per100k` |
| **X** | `GW_pH_median`, `GW_EC_uScm_median`, `GW_HCO3_median`, `GW_Cl_median`, `GW_SO4_median`, `GW_NO3_median`, `GW_F_mgL_median`, `GW_TDS_median`, `n_wells` |
| Validation | GroupKFold by **District** (5 folds) |
| Scripts | `scripts/extract_cgwb_bihar_csvs.py` → `scripts/build_official_master_dataset.py` → `scripts/run_pipeline.py` |

---

## 4. Latest CV metrics (after reframe)

From `results/models/metrics.json` (out-of-fold, spatial CV):

| Model | Mean RMSE | Mean MAE | Mean R² |
|--------|-----------|----------|---------|
| ridge | 1.496 | 1.229 | −0.424 |
| **rf (selected)** | **1.494** | **1.252** | **−0.450** |
| xgb | 1.668 | 1.400 | −0.797 |

RMSE/MAE are on **log(1 + burden per 100k)** scale, not case counts. **R²** can still be modest with few units and weak exposure-only signal; use outputs mainly for **relative ranking**, SHAP direction, and **hypothesis generation**, not point forecasting claims.

---

## 5. Recommended next steps

1. **Add covariates:** rainfall, sanitation, literacy, WASH (Census/NFHS/IMD) to strengthen signal.  
2. **Population over time:** replace static 2011 pop with projected district population by year for more accurate rates.  
3. **Count models:** Poisson / Negative Binomial with **log(population) offset** on `HMIS_burden_raw` or component counts.  
4. **Classification:** train on `High_risk_tercile` or top-quantile SAM rate with **recall-focused** metrics.  
5. **Arsenic / TDS:** extend CGWB 2023 parsing to expose **As** and consistent **TDS** in the feature block.

---

## 6. Artifacts

| Output | Path |
|--------|------|
| Master CSV | `data/processed/official_district_year_master.csv` |
| Metrics & OOF | `results/models/metrics.json`, `oof_predictions.csv` |
| Fitted model | `results/models/best_model.joblib` |
| Figures | `results/figures/*.png` |

---

*This report supersedes the “raw SAM count only” description. The scientific story is now **environmental exposure and district-level child-health vulnerability in Bihar**, using official HMIS + CGWB + Census.*
