"""
Local web UI: enter new district-year groundwater data, run susceptibility (frozen reference)
and optional ML regression prediction.

Run from project root:
  streamlit run streamlit_app.py

Or:
  .venv\\Scripts\\python.exe -m streamlit run streamlit_app.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bihar_health_risk.config import DISTRICT_COL, MODELS_DIR, YEAR_COL  # noqa: E402
from bihar_health_risk.preprocess import add_exposure_interactions  # noqa: E402
from bihar_health_risk.susceptibility import apply_frozen_reference_susceptibility  # noqa: E402

REF_PATH = MODELS_DIR / "susceptibility_reference.json"
MODEL_PATH = MODELS_DIR / "best_model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"
@st.cache_data
def load_reference_bytes(path_str: str) -> dict | None:
    p = Path(path_str)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


@st.cache_data
def load_metrics_bytes(path_str: str) -> dict | None:
    p = Path(path_str)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    st.set_page_config(page_title="Bihar GW · Susceptibility & ML", layout="wide")
    st.title("Bihar groundwater — susceptibility & burden prediction")
    st.caption(
        "Susceptibility uses **frozen reference** from your last pipeline run. "
        "ML prediction uses **best_model.joblib** (spatial CV caveats apply)."
    )

    ref = load_reference_bytes(str(REF_PATH))
    metrics = load_metrics_bytes(str(METRICS_PATH))

    with st.sidebar:
        st.header("Setup")
        if ref is None:
            st.error(f"Missing `{REF_PATH.name}`. Run: `python scripts/run_pipeline.py`")
        else:
            st.success(f"Reference OK ({ref.get('reference_n_rows', '?')} reference rows)")
        custom_ref = st.file_uploader("Optional: upload custom reference JSON", type=["json"])
        if custom_ref is not None:
            st.session_state["ref_override"] = json.loads(custom_ref.getvalue().decode("utf-8"))
        if st.session_state.get("ref_override") is not None:
            ref = st.session_state["ref_override"]
        if st.button("Reset reference to default file"):
            st.session_state.pop("ref_override", None)
            st.rerun()

        st.divider()
        st.markdown(
            "**Run app:** `streamlit run streamlit_app.py`  \n"
            "**Project:** `Major Project` root"
        )

    tab_sus, tab_ml, tab_about = st.tabs(["Susceptibility (Yes/No)", "ML model prediction", "About / metrics"])

    # ----- Susceptibility -----
    with tab_sus:
        if ref is None:
            st.stop()

        st.subheader("1) Load new rows")
        c1, c2 = st.columns(2)
        with c1:
            up = st.file_uploader("Upload CSV (District, Year + GW columns)", type=["csv"])
        with c2:
            template_cols = [DISTRICT_COL, YEAR_COL] + ref["gw_cols"]
            template_cols_opt = template_cols + ["HMIS_burden_per_100k"]
            tpl = pd.DataFrame(columns=template_cols_opt)
            buf = io.StringIO()
            tpl.to_csv(buf, index=False)
            st.download_button(
                "Download empty CSV template",
                buf.getvalue().encode("utf-8"),
                file_name="susceptibility_input_template.csv",
                mime="text/csv",
            )

        df_in: pd.DataFrame | None = None
        if up is not None:
            df_in = pd.read_csv(up)
            st.session_state.pop("manual_df", None)
            st.success(f"Loaded {len(df_in)} row(s) from file.")
        else:
            with st.expander("Or fill one row manually (then Submit)", expanded=False):
                stats = ref.get("feature_stats", {})
                with st.form("manual_one_row"):
                    d_name = st.text_input("District", value="Patna")
                    y_val = st.number_input("Year", min_value=2000, max_value=2100, value=2025)
                    row_vals: dict = {DISTRICT_COL: d_name, YEAR_COL: int(y_val)}
                    for c in ref["gw_cols"]:
                        default = float(stats.get(c, {}).get("mean", 0.0))
                        if c == "n_wells":
                            default = float(max(1.0, np.expm1(default)))
                        row_vals[c] = float(
                            st.number_input(c, value=default, format="%g", key=f"form_{c}")
                        )
                    hmis_on = st.checkbox("Include HMIS_burden_per_100k")
                    hmis_v = st.number_input("HMIS_burden_per_100k", value=40.0)
                    submitted = st.form_submit_button("Submit row for scoring")
                    if submitted:
                        if hmis_on:
                            row_vals["HMIS_burden_per_100k"] = hmis_v
                        st.session_state["manual_df"] = pd.DataFrame([row_vals])

        if df_in is None and "manual_df" in st.session_state:
            df_in = st.session_state["manual_df"]
            st.caption(f"Using manual row: {df_in.iloc[0][DISTRICT_COL]}, {df_in.iloc[0][YEAR_COL]}")

        if df_in is None:
            st.info("Upload a CSV or submit the manual form above.")
        else:
            miss = [c for c in [DISTRICT_COL, YEAR_COL] + ref["gw_cols"] if c not in df_in.columns]
            if miss:
                st.error(f"Missing columns: {miss}")
            else:
                if st.button("Run susceptibility scoring", type="primary"):
                    try:
                        out = apply_frozen_reference_susceptibility(df_in, ref)
                        st.session_state["last_sus"] = out
                    except Exception as e:
                        st.exception(e)

                if "last_sus" in st.session_state:
                    out = st.session_state["last_sus"]
                    st.subheader("Results")

                    show_cols = [
                        DISTRICT_COL,
                        YEAR_COL,
                        "Environmental_stress_band",
                        "Environmental_susceptibility_high_stress_YN",
                        "Environmental_exposure_index",
                        "HMIS_observed_high_burden_YN",
                        "HMIS_observed_burden_tercile",
                        "HMIS_burden_per_100k",
                        "Top_GW_stress_1",
                        "Top_GW_stress_2",
                        "Top_GW_stress_3",
                        "Prediction_mode",
                    ]
                    show_cols = [c for c in show_cols if c in out.columns]
                    st.dataframe(out[show_cols], use_container_width=True)

                    csv_bytes = out.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download results CSV",
                        csv_bytes,
                        file_name="susceptibility_predictions.csv",
                        mime="text/csv",
                    )

                    env_y = (out["Environmental_susceptibility_high_stress_YN"] == "Yes").sum()
                    st.metric("Environmental high-stress (Yes)", f"{int(env_y)} / {len(out)}")

    # ----- ML -----
    with tab_ml:
        if not MODEL_PATH.exists():
            st.warning("Train first — `best_model.joblib` not found.")
            st.stop()

        bundle = joblib.load(MODEL_PATH)
        pipe = bundle["pipeline"]
        feats: list[str] = list(bundle["feature_cols"])
        st.write("Model:", bundle.get("model_name", "?"))
        st.write("Expected features:", feats)

        st.subheader("Input")
        ml_up = st.file_uploader("CSV with feature columns (same names as listed)", type=["csv"], key="ml_csv")
        if ml_up:
            df_ml = pd.read_csv(ml_up)
            df_ml = add_exposure_interactions(df_ml)
            miss_f = [c for c in feats if c not in df_ml.columns]
            if miss_f:
                st.error(f"Missing for ML: {miss_f}")
            else:
                X = df_ml[feats]
                pred = pipe.predict(X)
                res = df_ml[[DISTRICT_COL, YEAR_COL]].copy() if DISTRICT_COL in df_ml.columns else pd.DataFrame()
                if DISTRICT_COL not in df_ml.columns:
                    res = pd.DataFrame({"row": range(len(pred))})
                res["predicted_Target_log_burden_per100k"] = pred
                st.dataframe(res, use_container_width=True)
                st.download_button(
                    "Download ML predictions CSV",
                    res.to_csv(index=False).encode("utf-8"),
                    file_name="ml_predictions.csv",
                    mime="text/csv",
                )
        else:
            st.info("Upload a CSV that includes all **Expected features** columns (and District/Year if you want them in output).")

    # ----- About -----
    with tab_about:
        st.markdown(
            "- **Susceptibility:** frozen mean/std + tertile bins from `susceptibility_reference.json`.  \n"
            "- **ML:** trained pipeline; weak spatial CV is normal — use as exploratory output.  \n"
            "- **Figures:** see `results/figures/`"
        )
        if metrics:
            st.json(metrics)
        else:
            st.write("Run pipeline to create `metrics.json`.")


if __name__ == "__main__":
    main()
