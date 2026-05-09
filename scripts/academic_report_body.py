"""
Long-form manuscript text for scripts/generate_academic_report_docx.py.
Separated for readability; edit here to adjust narrative depth.
"""

TITLE = (
    "Integrating Official Groundwater Quality Monitoring with District-Level Child Health "
    "Indicators in Bihar: A Spatially Honest Machine Learning Study with Explainability "
    "and Susceptibility Profiling"
)

SUBTITLE = (
    "Major Project Report — reproducible pipeline linking Central Ground Water Board "
    "(CGWB) chemistry medians, Health Management Information System (HMIS) burden metrics, "
    "and Census 2011 population denominators"
)

KEYWORDS = (
    "Bihar; groundwater quality; HMIS; district-level panel; spatial cross-validation; "
    "random forest; ridge regression; gradient boosting; explainable artificial intelligence "
    "(SHAP); environmental susceptibility; public health informatics"
)


def split_blocks(big_text: str) -> list[str]:
    return [p.strip() for p in big_text.strip().split("\n\n") if p.strip()]


ABSTRACT = split_blocks(
    """
This report presents a complete account of a reproducible research pipeline that combines official environmental monitoring data with routine health information system statistics at the district level in the state of Bihar, India. The scientific motivation is straightforward yet ambitious: groundwater chemistry is a plausible environmental stressor that may coincide with patterns of child morbidity and mortality burden, but proving causation from observational district-year panels is not feasible without experimental designs or detailed individual-level exposure histories. Therefore, the project is deliberately framed as an associational and prioritisation-oriented study rather than a clinical forecasting system.

The dataset is built by merging three trusted public sources. First, district-by-year summaries of groundwater quality are derived from Central Ground Water Board (CGWB) well measurements, summarised as medians (or means where appropriate) for key ions and physicochemical indicators together with the count of monitored wells, which reflects monitoring intensity. Second, child-health burden is operationalised using a transparent composite constructed from selected HMIS indicators that capture severe acute malnutrition, common childhood illnesses, infant and child deaths attributed to diarrhoea and pneumonia, very early neonatal deaths, and stillbirths, aggregated under consistent facility roll-up rules to avoid double counting. Third, Census 2011 district populations provide denominators so that burden can be expressed as events per one hundred thousand population before stabilisation with a logarithmic transform for modelling.

Machine learning models — ridge regression (an interpretable linear baseline with regularisation), random forest (an ensemble of decision trees), and extreme gradient boosting — are trained under grouped cross-validation that holds out entire districts during validation folds. This spatial honesty reduces optimism that arises when neighbouring geographic units leak correlated information across train and test splits. Performance is summarised using familiar regression metrics, but special emphasis is placed on comparing model error to a naive mean baseline and on rank agreement measured by Spearman correlation, because decision-makers often care about relative ordering for resource targeting rather than perfect point prediction.

Explainability analysis applies SHAP (SHapley Additive exPlanations) values compatible with tree models and linear models to summarise how each groundwater-related feature contributes to predictions at the cohort level. Separately, a rule-based susceptibility layer constructs cohort-relative standardised exposure indices and categorical environmental stress bands without requiring a trained regressor, yielding interpretable “high environmental stress” flags suitable for communication alongside model outputs.

The empirical results in the accompanying artefact files indicate that groundwater-only features do not produce strong predictive accuracy for the chosen HMIS-derived outcome under strict spatial validation; pooled out-of-fold scores show negative R-squared relative to the variance of the held-out merged predictions when interpreted in the standard way for ordinary cross-validation, and error can exceed a naive baseline. These findings are scientifically meaningful: they caution against overstating predictive power while still permitting cautious hypothesis generation through directional attribution plots and transparent environmental profiles. The present document explains every step — data harmonisation, variable definitions, algorithms, validation philosophy, outputs, and limitations — in plain English suitable for academic submission.
"""
)


INTRODUCTION = split_blocks(
    """
Child health outcomes in low- and middle-income settings arise from an intertwined mixture of biological susceptibility, household behaviour, health-service readiness, nutrition, infection exposure, and broader environmental conditions including water quality and sanitation. Among environmental pathways, groundwater chemistry matters because millions of people rely on tubewells and hand pumps that draw from aquifers whose quality varies across geology, agricultural intensity, seasonal recharge, and anthropogenic contamination. Elevated salinity, nitrate, fluoride, or extreme pH patterns may signal hazards or stressors that coincide geographically with districts reporting heavier burdens in routine facility-based statistics.

Bihar is a populous state where districts differ markedly in hydrogeology, flood vulnerability, and health-system reporting volumes. Official programmes publish groundwater observations through CGWB monitoring networks, while the national Health Management Information System aggregates facility-reported counts across indicators and years. Census enumerations provide stable population denominators that convert raw counts into interpretable rates for comparisons across districts of different sizes.

The central challenge for evidence synthesis is methodological. District-year panels are coarse: they average across villages and households, mix multiple causal pathways, and embed reporting artefacts such as variable facility completeness or diagnostic practices. Any statistical association between aggregated groundwater summaries and aggregated burden metrics therefore reflects ecological correlation rather than individual-level causal effects. Recognising this limitation is not a weakness of the study but a prerequisite for honest inference.

Machine learning offers flexible function approximation for nonlinear relationships and interactions among chemistry variables, yet flexible models can easily appear accurate when validation is optimistic. Standard random splitting of rows often lets geographically adjacent districts appear in both training and evaluation, effectively allowing the model to interpolate local clusters rather than generalise to unseen administrative units. To align evaluation with the practical question — “Would patterns learned from some districts help prioritise others?” — this project adopts grouped cross-validation by district identifiers.

Beyond prediction, stakeholders benefit from interpretability. Tree ensembles can be opaque when presented only as black-box scores. SHAP explanations summarise contributions of each input feature to model output for tree-based and linear models in a unified additive framework grounded in cooperative game theory intuition. Meanwhile, not every communication setting requires a predictive model: the pipeline therefore includes a parallel susceptibility construct based on cohort-relative standardisation of groundwater variables and transparent labelling of environmental stress tertiles.

This report documents the entire workflow end-to-end so that reviewers can trace claims from raw inputs to figures and saved metrics. It uses careful language throughout: “association,” “referent outcome,” “prioritisation,” and “hypothesis generation” replace overstated claims of causal forecasting. The intent is an academic-grade narrative that matches the code artefacts already maintained in the repository.
"""
)


LITERATURE_REVIEW = split_blocks(
    """
Environmental epidemiology has long studied drinking-water contaminants and health endpoints at varied scales. Classical examples include investigations of arsenic exposure in groundwater and adverse outcomes, nitrate and methemoglobinemia risk in infants, and fluoride and skeletal or dental effects. Such links are often established through cohort studies, case-control designs, or intervention trials where exposure can be characterised more finely than in aggregate panels. At ecological scales, analyses must contend with the ecological fallacy: relationships observed for groups do not automatically transfer to individuals within those groups.

Hydrochemical datasets from national monitoring programmes provide spatially extensive measurements but uneven temporal density at the district-year resolution when wells are sparse in some units. Aggregation to medians reduces sensitivity to outliers yet discards distributional tails that may matter for vulnerable subpopulations. Monitoring intensity — how many wells contribute — can correlate with administrative attention or accessibility, introducing subtle structural factors unrelated to true average chemistry.

Routine health information systems such as HMIS offer timely coverage but depend on reporting completeness and definitions that evolve as programmes change. Composite indicators aggregate multiple clinical burdens to summarise vulnerability, yet composites embed normative choices about which conditions enter the sum and how missing indicators are treated. Transparency in indicator lists and aggregation logic is therefore as important as statistical sophistication.

Machine learning in public health has expanded rapidly. Ensemble tree methods — random forests introduced by Breiman and boosting families popularised through implementations such as XGBoost — often perform strongly on tabular data with nonlinearities and heterogeneity. Regularised linear models remain valuable baselines because coefficients are directly interpretable under linearity assumptions and scaling choices. Regardless of algorithm, rigorous validation design determines whether reported accuracy reflects genuine generalisation.

Explainable artificial intelligence bridges predictive modelling and domain interpretation. SHAP methods attribute predictions to features using Shapley-value-inspired allocations that satisfy desirable additive properties for many model classes. For tree ensembles, TreeExplainer enables efficient exact calculations under specified assumptions; for linear models, LinearExplainer corresponds closely to coefficient-driven explanations after preprocessing. Researchers caution that explanations summarise model behaviour rather than ground-truth causal mechanisms; they remain indispensable for auditing bias directions and communicating uncertainty-aware narratives.

Spatial and grouped validation appears across geospatial machine learning literature under headings such as spatial cross-validation and block holdouts. The principle is consistent: autocorrelation violates independence assumptions that naive splitting assumes. Holding out groups defined by administrative boundaries is a conservative approach aligned with policy questions about transferring insights across districts.

Susceptibility mapping in environmental sciences often denotes graded categories of hazard or vulnerability using transparent indices. The present project borrows that communication style by constructing environmental stress bands from cohort-relative z-scores rather than implying validated clinical risk from chemistry alone.

Together, these strands motivate a study design that combines credible official data fusion, conservative spatial validation, interpretable baselines and ensembles, explanation layers, and parallel rule-based profiles suitable for mixed audiences including academics and programme analysts.

Recent syntheses in environmental health increasingly emphasise open data pipelines rather than only polished headline coefficients. Reviewers ask how denominators were formed, how duplicate facilities were excluded, and whether spatial autocorrelation was respected — questions this thesis anticipates by documenting merges explicitly and adopting grouped folds. Machine-learning critiques also warn against “accuracy theatre,” wherein impressive-looking scores arise from information leakage rather than genuine transportability; spatial grouping operationalises a substantive response.

Indian administrative datasets possess uneven temporal harmonisation: groundwater sampling calendars may not align with HMIS fiscal-year reporting windows. Scholars therefore differentiate predictive modelling for interpolation within observed geo-time neighbourhoods from extrapolation to unseen districts or future epidemic regimes. Our framing adopts conservative language aligned with extrapolation stress-testing via held-out districts.

Interpretability research stresses separating model-internal explanations from causal attribution. SHAP values describe how a fitted model allocates responsibility among inputs — helpful for debugging unwanted reliance on artefacts such as well-count proxies — but they cannot prove that modifying chloride in the field would reduce pneumonia counts at population scale without experimental or quasi-experimental designs.

Finally, susceptibility-style indices echo vulnerability literature mapping compound stresses without implying predictive certainty. Presenting them beside regressions allows policymakers to see parallel narratives: one emphasises learned nonlinear mappings with uncertainty; another emphasises transparent standardisation relative to cohort norms without optimisation objectives beyond descriptive scaling.
"""
)


EXTRA_LITERATURE_BRIDGE = split_blocks(
    """
Bridging hydrology and health informatics requires multidisciplinary literacy. Hydrogeologists scrutinise ion ratios, recharge pathways, and sampling depth stratification; epidemiologists scrutinise case definitions, numerator stability, and denominator appropriateness; data scientists scrutinise pipeline leakage and metric selection. Few single-authored papers span all competences fluently, motivating modular codebases where domain specialists can audit segments independently.

Transparency norms increasingly resemble registry-style documentation: pre-specifying indicator lists and aggregation rules prevents post-hoc tuning narratives that erode trust. While this academic report cannot substitute for a clinical trial registry, it adopts the spirit by enumerating HMIS labels verbatim and freezing preprocessing transforms saved alongside susceptibility references.

Equity considerations intersect technical choices: districts with sparse monitoring receive chemistry estimates built from fewer wells; models might inadvertently associate uncertainty patterns with burden unless analysts consciously audit residuals stratified by well-count quartiles. Such audits belong in mature extensions but merit mention because fairness-aware machine learning is maturing rapidly in public-sector deployments.

Educational accounts of negative predictive results remain under-published compared with positive benchmarks, yet they anchor realistic expectations for undergraduate and postgraduate training. Students learn that rigorous spatial validation often collapses apparent accuracy — a lesson transferable beyond groundwater contexts to any geo-referenced social or environmental outcome.
"""
)


OBJECTIVES = split_blocks(
    """
The primary objective is to construct a reproducible district-year analytical dataset linking CGWB-derived groundwater summaries, HMIS-derived child burden summaries with Census denominators, and to document every transformation with sufficient clarity for independent replication.

A secondary objective is to evaluate associational models that predict a stabilised log burden outcome using groundwater-centred predictors under grouped cross-validation by district, comparing multiple algorithms and reporting error relative to naive baselines alongside rank-correlation diagnostics relevant to prioritisation.

An explanatory objective is to quantify feature contributions using SHAP for the selected best-performing model under cross-validated error, treating attributions as hypothesis-generating summaries rather than causal effects.

A communication objective is to produce interpretable environmental susceptibility profiles — including categorical stress bands and ranked chemical drivers — that do not depend on predictive accuracy yet support structured discussion of districts experiencing shifted groundwater chemistry relative to the cohort.

Finally, a dissemination objective is to package outputs — metrics tables, diagnostic figures, saved models, and an interactive Streamlit exploration interface — so that results can be inspected without rerunning the entire pipeline unless raw inputs change.
"""
)


STUDY_AREA = split_blocks(
    """
Bihar is situated in eastern India with dense agrarian settlement patterns and substantial reliance on groundwater for domestic and irrigation purposes. Districts serve as administratively meaningful units for planning and for aligning CGWB summaries with HMIS reporting geography. District-year observations capture slow-moving shifts in monitored chemistry alongside year-to-year fluctuations in reported burdens influenced by epidemics, seasonal diarrhoea peaks, programme intensification, and changes in facility reporting.

The analytical frame intentionally stays at district-year resolution because it matches publicly released monitoring roll-ups and HMIS fiscal-year alignment after harmonisation. Finer spatial modelling would require geocoded wells linked to populations at risk and granular outcome data beyond what this pipeline consumes.
"""
)


DATA_SOURCES = split_blocks(
    """
Central Ground Water Board periodic district-wise chemistry extracts underpin the environmental arm of the dataset. Raw well-level tables are aggregated to district-year medians for major ions and conductivity-related quantities, along with counts of sampled wells. Medians resist extreme single-well spikes better than means for skewed constituents while remaining straightforward to explain in reports.

HMIS indicator extracts come from official spreadsheets cataloguing district-and-year values under stated facility categories. The pipeline restricts rows to a consistent facility rollup and category total so that composite sums remain comparable across districts and years. Indicator labels are matched exactly to catalogue strings; unmatched indicators are skipped with warnings to preserve transparency.

Census 2011 district populations convert summed HMIS counts into rates per hundred thousand people. Using Census denominators introduces a temporal mismatch — populations evolve after 2011 — which is an acknowledged limitation mitigated slightly by the relative stability of decadal population rankings at district scale within short HMIS windows.

Merged outputs retain both raw burden sums and transformed modelling targets. The modelling target applies a logarithmic stabilisation using the natural logarithm of one plus the rate to reduce leverage of rare districts with extremely high counts while preserving ordering for many practical comparisons.
"""
)


DATASET_DESCRIPTION = split_blocks(
    """
The master training table is stored as a comma-separated text file where each row corresponds to one district in one calendar-aligned year present in both groundwater summaries and HMIS summaries after inner joins. Inner joins exclude district-years lacking paired environmental and health aggregates, improving coherence at the cost of potentially omitting sparse observations.

Column completeness varies slightly because some chemical parameters may be missing when laboratories did not report them for every well batch; preprocessing uses median imputation within cross-validation folds through scikit-learn pipelines to reduce leakage from future validation rows into training statistics.

Row counts and distinct district counts are recorded automatically into metrics JSON files during training so that reports always reflect the executed configuration rather than manually typed approximations.

Duplicate naming inconsistencies across administrative spellings are reduced using standardisation utilities so that identical districts align across CGWB and HMIS extracts.

The dataset supports two parallel analytical products: supervised regression training for associational prediction under spatial validation, and unsupervised-style cohort-relative susceptibility scoring that only requires groundwater columns and identifiers.
"""
)


VARIABLE_EXPLANATIONS = split_blocks(
    """
District name fields identify administrative units and simultaneously serve as grouping keys for spatial folds. Year identifies temporal alignment between environmental summaries and HMIS fiscal conversions.

Groundwater pH measures whether water tends acidic or alkaline on the standard scale. Extreme values can indicate geogenic conditions or contamination signatures but must be interpreted with hydrogeochemical context.

Electrical conductivity (EC) proxies dissolved ionic content and salinity stress; higher values often accompany elevated total dissolved solids (TDS). Bicarbonate, chloride, sulphate, and nitrate ions capture distinct geochemical and anthropogenic pathways — for example nitrate associations with agricultural nitrogen loading in some settings. Fluoride is tracked because of known dental and skeletal concerns at elevated concentrations in parts of India.

Total dissolved solids summarise overall mineralisation. Well counts quantify how many observations contributed to district-year aggregates; after logarithmic stabilisation in susceptibility scoring it acts as a proxy for monitoring intensity rather than chemistry per se.

The HMIS composite burden sums selected paediatric indicators under transparent rules. The vulnerability z-score column summarises multi-indicator patterns after logarithmic stabilisation per indicator and cohort scaling. Population translates counts into rates. The modelling target column stores the stabilised log rate used as the regression response.

High-risk tertiles, when computable, divide districts into relative burden bands within the empirical distribution for descriptive stratification separate from model predictions.
"""
)


METHODOLOGY_ETL = split_blocks(
    """
Extract-transform-load steps begin at raw CGWB CSV exports. Scripts aggregate wells to district-year chemistry summaries using robust statistics where configured. District labels pass through string cleaning and canonicalisation routines so merges succeed despite minor spelling variants.

HMIS spreadsheets are read with constrained columns to reduce memory footprint. Fiscal year labels convert to starting calendar years consistent with groundwater tables. Pivot operations reshape long indicator lists into wide matrices suitable for summation and z-score constructions.

Population merges attach Census totals on district keys. Rates are computed explicitly so auditors can reproduce arithmetic outside the machine learning code path.

Quality assurance prints indicator lists successfully matched and warns about omissions. Empty merges halt with actionable messages directing users to regenerate prerequisites.

All artefacts write into deterministic folders — processed CSV under data hierarchy, extracted intermediates under official data mirrors — mirroring paths referenced by configuration modules consumed during training.
"""
)


METHODOLOGY_ML = split_blocks(
    """
Supervised learning treats each district-year row as one sample with vector inputs drawn primarily from groundwater summaries and scalar output equal to the stabilised log burden rate. Groups derive from district identifiers so that GroupKFold assigns all years from a held-out district to validation during a fold whenever possible subject to split cardinality constraints.

Preprocessing pipelines median-impute missing numeric inputs inside folds. Tree models consume raw scaled-or-unscaled inputs depending on algorithm preferences; ridge regression pairs imputation with standardisation of numeric columns for penalised fitting stability.

Models compete by mean validation root mean squared error across folds. After selection, the winning estimator retrains on all rows to produce a deployment-ready pipeline serialised with joblib alongside metadata listing feature names.

Out-of-fold predictions concatenate validation predictions across folds into a full-length vector aligned with the training frame for diagnostic plotting and Spearman correlation against observed outcomes.

Missingness tables summarise column-wise fractions helping reviewers judge whether imputation dominates behaviour for particular ions.

Figures include predicted versus observed scatterplots to reveal systematic bias, residual histograms for error symmetry checks, bar summaries of mean absolute SHAP magnitudes, and charts highlighting districts with elevated predicted values under the trained model for prioritisation-style reading.

The naive baseline predicts every held-out point using the global mean training response, furnishing a sanity check: models should not be celebrated if they cannot outperform this rudimentary reference under honest validation.
"""
)


METHODOLOGY_SUSCEPTIBILITY = split_blocks(
    """
Susceptibility profiling begins by converting each groundwater column into cohort-relative z-scores measuring how far a district-year sits above or below the average pattern after numeric coercion. The well-count column uses logarithmic stabilisation before z-scoring to dampen heavy tails while preserving interpretability.

Averaging signed z-scores across available ions yields a scalar environmental exposure index summarising overall shifted chemistry relative to peers. Absolute z-scores rank which labelled constituents contribute most to deviation for narrative bullet lists.

Tercile cuts on the exposure index assign Low, Medium, and High environmental stress bands when quantile splitting succeeds; duplicates handling prevents failures on degenerate distributions.

A binary environmental stress flag marks High as “Yes” and other bands as “No” for simplified dashboards. Separately, HMIS burden tertiles remain available when researchers wish to contrast environmental stress labels against burden strata without assuming independence.

Reference statistics — means, standard deviations, and bin edges — can be frozen to JSON files so that future years score consistently against historical cohorts rather than redefining thresholds silently.

This layer deliberately avoids claiming predictive validity; it communicates transparent transforms suitable for stakeholder meetings alongside regression outputs.
"""
)


ALGORITHM_RIDGE = split_blocks(
    """
Ridge regression extends ordinary least squares linear regression by adding an L2 penalty proportional to the squared magnitude of coefficients. The penalty shrinks coefficients toward zero, reducing variance at the expense of introducing controlled bias — often beneficial when predictors correlate with each other, as ions jointly shift with mineralisation.

Hyperparameter alpha scales penalty strength; larger alpha yields smoother, smaller coefficients. Training selects fixed defaults documented in code for reproducibility rather than exhaustive tuning grids, reflecting the study’s emphasis on methodological transparency over leaderboard optimisation.

Because ridge is linear, predictions are weighted sums of inputs after preprocessing. Combined with SHAP LinearExplainer, attributions align closely with coefficient-direction intuition once scaling is accounted for, aiding teaching-style explanations.

Ridge serves as an interpretable baseline against which nonlinear ensembles must justify additional complexity through materially improved validation error — a benchmark this ecological dataset challenges under spatial splits.
"""
)


ALGORITHM_RF = split_blocks(
    """
Random forest regression aggregates predictions from many independent decision trees trained on bootstrap samples of rows and random subsets of features at each split. Averaging reduces variance relative to single deep trees prone to overfitting.

Depth limits and minimum leaf sample thresholds constrain tree complexity; ensemble size controls Monte Carlo averaging fidelity. Random forests capture nonlinear saturating relationships and modest interactions without manual specification.

Training runs efficiently on multicore CPUs given available implementations. Tree structures permit SHAP TreeExplainer analyses that distribute prediction differences across features for each observation and aggregate into global importance summaries.

Random forests often perform robustly on heterogeneous tabular scientific data, making them a natural candidate alongside simpler linear approaches when groundwater chemistry interacts with scaling and threshold effects.

Selection as the best model under mean cross-validated root mean squared error indicates empirical superiority among candidates for this dataset configuration, though superiority does not imply clinical predictive adequacy.
"""
)


ALGORITHM_XGB = split_blocks(
    """
Extreme gradient boosting constructs an additive sequence of shallow trees where each new tree fits pseudo-residuals from the current composite prediction. Regularisation terms penalise leaf weights and tree complexity; stochastic subsampling introduces randomness improving generalisation.

Learning rate scales incremental updates; deeper trees capture richer interactions but risk overfitting when data are sparse at district-year granularity. Configured hyperparameters balance capacity against conservative fitting.

Boosting sometimes excels on structured prediction competitions; here spatial validation stringency may limit gains when signal-to-noise ratios remain low at aggregated scales.

When installed, XGBoost participates in model comparison; if unavailable, the pipeline gracefully omits it without halting core analyses — an engineering detail aiding reproducibility across environments.

SHAP TreeExplainer likewise applies when boosting models are selected, preserving a unified explanation pathway across tree ensembles.
"""
)


METHODOLOGY_ETHICS = split_blocks(
    """
Ethical reasoning for observational environmental-health modelling begins with harm avoidance in communication. Misleading certainty could divert limited public funds toward chemically flagged districts when socio-behavioural determinants dominate burdens. Therefore reports must foreground uncertainty, distinguish correlation from causation, and pair algorithmic outputs with domain expert review before operational intervention.

Data stewardship responsibilities include using official statistics respectfully: acknowledging HMIS as a management tool rather than a complete epidemiological census; crediting Census denominators while noting temporal staleness; citing CGWB monitoring without implying blanket coverage of every aquifer tapped by households.

Privacy risks remain limited at aggregate district-year scales relative to individual records, yet secondary disclosure concerns still arise if rare events could theoretically identify small populations when merged with other sources. Here composites sum multiple indicators to reduce focus on single ultra-rare counts; nonetheless analysts exporting subsets should apply suppression rules consistent with institutional policies when publishing granular tables.

Explainability interfaces such as SHAP plots can unintentionally oversimplify if coloured bars become rhetorical shortcuts replacing contextual chemistry interpretation. Training audiences to read contributions as model-facing attributions mitigates misuse.

Susceptibility flags labelled “Yes” for high environmental stress communicate cohort-relative deviation without asserting clinical diagnoses for residents; accompanying documentation must repeat this caveat for ethical clarity.

Replication artefacts empower independent critique — an ethical positive-sum practice accelerating collective learning over proprietary black boxes.

Future institutional review for derivative studies incorporating human subjects or facility-identifiable extracts would require separate approvals beyond this aggregate pipeline.
"""
)


METRICS_AND_VALIDATION = split_blocks(
    """
Root mean squared error punishes large errors more heavily than mean absolute error, highlighting outliers — relevant when a few district-years dominate perceived fit. Mean absolute error summarises typical absolute deviation in original target units after inverse transforms if applied.

Coefficient of determination R-squared compares explained variance to total variance within evaluation subsets. Under grouped spatial folds with small held-out district sets, R-squared can swing negative when predictions deviate more than simply predicting the mean of those held-out points — an outcome that signals weak explanatory power but should not be mistaken for a coding error without context.

Pooled out-of-fold metrics aggregate all validation predictions after stitching folds, offering a single summary across rows while still respecting that each prediction came from a model that never trained on its district group during its originating fold.

Spearman rank correlation assesses monotonic agreement between predicted and observed orders — valuable when rankings drive resource targeting even if absolute calibration remains imperfect.

SHAP mean absolute values summarise global feature impact magnitudes for tree models; ordering indicates relative importance though not causal priority.

Together these diagnostics resist single-number hype by juxtaposing multiple complementary perspectives aligned with honest ecological modelling practice.
"""
)


DISCUSSION = split_blocks(
    """
Findings must be interpreted within the ecological fallacy constraint: district aggregates smooth heterogeneity and cannot certify individual exposures or biological mechanisms. Negative validation metrics under strict spatial holdouts signal that groundwater summaries alone lack sufficient information to forecast HMIS burden shifts reliably across unseen districts — an instructive negative result discouraging overclaim.

Nevertheless, structured data fusion remains valuable for situational awareness. Environmental susceptibility profiles transparently describe chemistry deviations relative to peers. SHAP plots hint which ions dominate model reasoning even when overall accuracy is modest, guiding prioritised laboratory follow-up or hydrogeological investigation rather than clinical diagnosis.

Temporal mismatch between Census denominators and later HMIS years, reporting artefacts, and sparse well counts in some districts each bias conclusions in partially known directions. Future extensions could incorporate rainfall remotely sensed indices, sanitation proxies, anaemia programmes, vaccination coverage, or mobility-adjusted exposure models if such columns become harmonised at compatible geography.

The ethical posture privileges transparency: models should not replace epidemiological investigation or clinical judgement; they contextualise official statistics for exploratory planning when limitations are prominently disclosed.

Replication packages — code, pinned dependencies where feasible, saved metrics, figures — embody open science norms enabling supervisors and reviewers to rerun analyses and compare sensitivity choices like interaction term inclusion or fold counts.

Overall, the project demonstrates rigorous methodology even when predictive signal remains weak, aligning scientific integrity with educational objectives of a major academic submission.
"""
)


LIMITATIONS = split_blocks(
    """
Limitations include reliance on administrative boundaries that mask intra-district variability; HMIS reporting completeness differences across facilities and years; chemical non-detect handling simplified through aggregation; inability to infer causality; potential misalignment between groundwater sampling seasons and diarrhoea seasonality; Census 2011 population static denominators; selection of HMIS indicators reflecting programmatic emphasis rather than exhaustive morbidity; and machine learning hyperparameter choices not exhaustively tuned via nested spatial searches due to small effective sample sizes.

Spatial cross-validation reduces leakage yet still evaluates transfer across districts within the same state — external validity to other states remains unknown without separate testing.

Missing mechanistic pathways — nutrition, maternal health, immunisation, health-worker density — mean residual confounding likely dominates observed associations.

These constraints do not invalidate the pipeline; they bound appropriate inference and motivate cautious language in policy-facing summaries.
"""
)


CONCLUSION = split_blocks(
    """
This report consolidated the conceptual, data, algorithmic, and interpretability foundations of a Bihar-focused district-year study linking CGWB groundwater summaries with HMIS-derived child burden metrics under spatially honest validation. The workflow foregrounds reproducibility, transparent indicator construction, and multi-algorithm comparison with explanation layers and parallel susceptibility profiling.

Empirical outcomes underscore humility about predictive claims while preserving analytical value for exploratory prioritisation and academic training in responsible machine learning for public health.

The completed artefacts — merged datasets, metrics JSON files, figures, trained pipelines, susceptibility exports, and interactive Streamlit exploration — collectively satisfy the brief for an integrated major project suitable for viva voce examination and manuscript-style submission pending supervisor formatting preferences.

Readers should treat numerical metrics as snapshots tied to specific pipeline runs; refreshing raw inputs or random seeds may yield slight variations though qualitative conclusions about strict-validation difficulty likely persist absent substantially richer covariates.
"""
)


FUTURE_SCOPE = split_blocks(
    """
Future work may extend spatial granularity using geostatistical exposure models linking wells to population raster surfaces; incorporate time-series dynamics with proper hierarchical models; add causal reasoning frameworks such as sensitivity analyses or instrumental variables only when credible instruments exist; enrich covariates with remotely sensed flooding indices and land use; evaluate fairness constraints across districts with differing reporting capacities; deploy continual validation dashboards tracking drift in chemistry reporting and HMIS definitions; explore probabilistic forecasts with uncertainty intervals rather than point estimates alone; and integrate water-supply scheme inventories where household connectivity modifies exposure relevance.

Educational extensions include interactive notebooks for classrooms translating SHAP outputs into simplified narratives for district officers.

Each direction should preserve the core ethical principle: transparency about limits rivals incremental accuracy gains.
"""
)


APPENDIX_SOFTWARE = split_blocks(
    """
The computational stack intentionally mixes mainstream scientific Python libraries for accessibility to examiners and future maintainers. NumPy supplies efficient dense numerical arrays underpinning matrix operations inside scikit-learn and gradient boosting implementations. Pandas provides labelled tabular data structures conducive to merge diagnostics, missingness summaries, and CSV interchange aligned with institutional open-data habits.

Scikit-learn furnishes composable preprocessing objects — median imputation inside pipelines, standard scaling for penalised linear models, grouped cross-validation iterators — emphasising modular reproducibility. Joblib serialises fitted estimator graphs for reuse in notebooks or lightweight web front-ends without rerunning training each session.

Random forests and ridge regression rely on mature CPU implementations with deterministic seeds where supported. XGBoost contributes an industrial-strength gradient boosting option when installed; the training driver gracefully degrades if optional dependencies are absent, preserving baseline analyses across constrained laboratory computers.

Matplotlib generates diagnostic scatter, residual, and ranking plots exported as raster images embedded into this report. SHAP integrates with Matplotlib backends to render summary bars translating high-dimensional attribution tensors into reviewable graphics.

Streamlit enables browser-based scenario exploration where users upload CSV rows or adjust hypothetical groundwater fields to view susceptibility scoring consistent with frozen reference statistics — helpful pedagogy though not a substitute for peer-reviewed inference.

Version discipline matters: dependency ranges appear in `requirements.txt`; pinned environments via virtual environments or containers reduce “works on my machine” friction during vivas. Runtime declarations on hosted platforms help binary wheels (for example PyArrow pulled indirectly by Streamlit) install cleanly.

Directory conventions separate raw inputs, processed merges, model artefacts, figures, and narrative exports so backups and archival deposits remain orderly.
"""
)


APPENDIX_HMIS_LIST = split_blocks(
    """
The HMIS composite employed in this repository sums the following official indicator labels when present in the source spreadsheet under the configured facility rollup and total category (exact string matching):

Childhood Diseases - Severe Acute Malnutrition (SAM); Childhood Diseases - Diarrhoea; Childhood Diseases - Pneumonia; Childhood Diseases - Measles; Number of Infant Deaths (1 -12 months) due to Diarrhoea; Number of Infant Deaths (1 -12 months) due to Pneumonia; Number of Child Deaths (1 -5 years) due to Diarrhoea; Number of Child Deaths (1 -5 years) due to Pneumonia; Number of cases of Infant deaths within 24 hrs of birth; Number of still births.

Summation treats each indicator as a non-negative count after coercion; zeros fill pivot gaps when an indicator lacks rows for a district-year combination. The vulnerability z-score summarises per-indicator log-stabilised values averaged after column-wise centring and scaling across the empirical matrix — a descriptive convenience capturing multi-morbidity emphasis rather than a clinical severity score.

Burden per one hundred thousand population divides the summed composite by Census 2011 district population (multiplied by one hundred thousand). The modelling target applies the natural logarithm of one plus that rate to dampen leverage while preserving interpretability checks via inverse transforms when needed.

Researchers wishing alternative composites should fork indicator lists transparently and rerun merges rather than silently editing figures downstream.
"""
)


APPENDIX_COMMANDS = split_blocks(
    """
Typical regeneration steps from a clean checkout proceed as follows after placing authoritative raw files in expected locations: extract CGWB CSV exports into `data/raw_groundwater/`; ensure the HMIS master spreadsheet path referenced by `scripts/build_official_master_dataset.py` exists; run the extraction helper if PDF archives must become structured CSVs; execute the official master builder to emit `data/processed/official_district_year_master.csv`; invoke `python scripts/run_pipeline.py` to refresh metrics, SHAP tables, figures, susceptibility profiles, and exported reports.

Optional demonstration mode using synthetic sample data is intentionally gated behind flags to prevent accidental substitution for research tables during submissions.

Susceptibility scoring for hypothetical future years can reuse frozen JSON references via `scripts/predict_susceptibility_new_year.py`, preserving historical cohort moments for z-score comparability.

Streamlit exploration launches locally with `streamlit run streamlit_app.py` from the repository root after ensuring trained artefacts reside under `results/models/`.

Archival deposits should bundle random seeds, dependency snapshots where feasible, and checksums of primary spreadsheets to prove lineage integrity for examination boards.
"""
)


REFERENCES_LIST = [
    "Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.",
    "Central Ground Water Board, Ministry of Jal Shakti, Government of India. Groundwater quality monitoring publications and district summaries (consulted for conceptual framing of chemistry indicators).",
    "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.",
    "Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased estimation for nonorthogonal problems. Technometrics, 12(1), 55–67.",
    "Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems (NeurIPS).",
    "Ministry of Health and Family Welfare, Government of India. Health Management Information System (HMIS) data dictionaries and reporting guidelines (indicator definitions and facility categories).",
    "Office of the Registrar General and Census Commissioner, India. Census of India 2011 — Primary Census Abstract and district population tables.",
    "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
    "Schwartz, J., & Campbell, L. M. (2009). Spatial ecological studies — foundational caution on ecological inference (conceptual reference class for aggregation issues).",
    "World Health Organization. Guidelines for drinking-water quality (framework for interpreting physicochemical parameters — contextual reference).",
    "Snowflake Inc. Streamlit open-source framework documentation (interactive deployment narrative).",
    "Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography, 40(8), 913–929.",
    "Moraga, P. (2019). Geospatial Health Data: Modeling and Visualization with R-INLA and Shiny. Chapman & Hall/CRC (conceptual perspective on spatial health data — methodological analogue).",
    "Wickham, H. (2014). Tidy data. Journal of Statistical Software, 59(10), 1–23 (philosophy aligned with transparent rectangular merges).",
]
