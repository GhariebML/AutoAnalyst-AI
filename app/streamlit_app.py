"""Streamlit dashboard for AutoAnalyst AI.

Two modes:
- Quick pipeline: single-shot ``run_analysis_pipeline`` (original behavior).
- Agent workflow: supervised LangGraph run with trace viewer, human-in-the-loop
  approvals, executive summary, and report/data downloads.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from autoanalyst.agents.graph import AutoAnalystConfig  # noqa: E402
from autoanalyst.agents.llm import create_llm, load_llm_settings  # noqa: E402
from autoanalyst.agents.supervisor import SupervisedRun  # noqa: E402
from autoanalyst.dashboard.helpers import (  # noqa: E402
    RunContext,
    answer_question,
    build_run_context,
    save_upload_to_temp,
    scalar_metrics,
    trace_to_dataframe,
)
from autoanalyst.pipeline import PipelineConfig, run_analysis_pipeline  # noqa: E402

st.set_page_config(page_title="AutoAnalyst AI", page_icon="📊", layout="wide")
st.title("📊 AutoAnalyst AI")
st.caption("Automated AI-Powered Data Analyst System — now with a supervised agent workflow")


def render_quick_mode(df: pd.DataFrame, target_options: list[str]) -> None:
    """Original single-shot pipeline experience."""
    st.sidebar.header("Pipeline Options")
    target_column = st.sidebar.selectbox("Optional target column", target_options)
    model_task = st.sidebar.selectbox("Model task", ["auto", "classification", "regression"])

    try:
        result = run_analysis_pipeline(
            df,
            PipelineConfig(target_column=target_column or None, model_task=model_task),
        )
    except Exception as exc:
        st.error(f"Pipeline failed: {exc}")
        st.stop()

    st.subheader("Dataset Preview")
    st.dataframe(result.raw_df.head(20), use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Raw Rows", result.raw_df.shape[0])
    col2.metric("Raw Columns", result.raw_df.shape[1])
    col3.metric("Cleaned Rows", result.cleaned_df.shape[0])
    col4.metric("Missing Values", int(result.raw_df.isna().sum().sum()))

    st.subheader("Data Profile")
    st.json(result.profile)

    st.subheader("Missing Values Report")
    st.dataframe(result.missing_values_report, use_container_width=True)

    st.subheader("Basic Statistics")
    if "numeric_summary" in result.eda_results:
        st.dataframe(result.eda_results["numeric_summary"], use_container_width=True)
    else:
        st.info("No numeric columns found for numeric summary.")

    if "correlation_matrix" in result.eda_results:
        st.subheader("Correlation Matrix")
        st.dataframe(result.eda_results["correlation_matrix"], use_container_width=True)

    if result.evaluation_results:
        st.subheader("Model Evaluation")
        st.json(result.evaluation_results)

    st.subheader("Starter Insights")
    for insight in result.insights:
        st.write(f"- {insight}")

    if result.warnings:
        st.subheader("Pipeline Warnings")
        for warning in result.warnings:
            st.warning(warning)


def render_agent_mode(uploaded_file: Any, target_options: list[str]) -> None:
    """Supervised agent run with trace, HITL gates, and downloads."""
    st.sidebar.header("Agent Options")
    target_column = st.sidebar.selectbox("Target column", target_options) or None
    require_approval = st.sidebar.checkbox("Human approval before cleaning/modeling", value=False)
    fail_fast = st.sidebar.checkbox("Fail fast on first error", value=False)
    max_retries = st.sidebar.slider("Retries per node", 0, 5, 2)

    try:
        dataset_path = save_upload_to_temp(uploaded_file)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    config = AutoAnalystConfig(
        dataset_path=dataset_path,
        target_column=target_column,
        require_approval=require_approval,
        fail_fast=fail_fast,
        max_retries=max_retries,
    )

    session_key = f"agent_run_{config.model_dump_json()}"
    run = st.session_state.get("agent_run")
    if run is None or st.session_state.get("agent_session_key") != session_key:
        try:
            run = SupervisedRun(config)
            run.start()
        except Exception as exc:
            st.error(f"Agent run failed to start: {exc}")
            st.stop()
        st.session_state["agent_run"] = run
        st.session_state["agent_session_key"] = session_key

    if not run.finished and _handle_approval_gate(run):
        st.rerun()

    if not run.finished:
        st.info("Agent workflow is running…")
        return

    _render_agent_results(run, target_column)


def _handle_approval_gate(run: SupervisedRun) -> bool:
    """Render approve/decline controls; True when the operator made a choice."""
    pending = run.pending_approval()
    if pending is None:
        return False

    st.warning(f"⏸ Awaiting your approval before the **{pending}** step.")
    col_approve, col_decline = st.columns(2)
    if col_approve.button(f"✅ Approve '{pending}'", type="primary"):
        run.approve(pending, approved=True)
        run.resume()
        return True
    if col_decline.button(f"🚫 Decline '{pending}'"):
        run.approve(pending, approved=False)
        run.resume()
        return True
    return False


def _render_agent_results(run: SupervisedRun, target_column: str | None) -> None:
    result = run.final_result()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", result.raw_df.shape[0])
    col2.metric("Columns", result.raw_df.shape[1])
    col3.metric("Cleaned Rows", result.cleaned_df.shape[0])
    col4.metric("Narration", "LLM" if _llm_enabled() else "Rules")

    if result.executive_summary:
        st.subheader("Executive Summary")
        st.write(result.executive_summary)

    left, right = st.columns([2, 3])

    with left:
        st.subheader("Run Trace")
        trace_df = trace_to_dataframe(run.trace())
        if not trace_df.empty:
            st.dataframe(trace_df, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Model Evaluation")
        metrics = scalar_metrics(result.evaluation_results)
        if metrics:
            metric_cols = st.columns(min(len(metrics), 4))
            for index, (key, value) in enumerate(metrics.items()):
                metric_cols[index % len(metric_cols)].metric(key.upper(), f"{value:.4f}")
        confusion = (result.evaluation_results or {}).get("confusion_matrix")
        if confusion:
            st.caption("Confusion matrix (rows = actual)")
            st.dataframe(pd.DataFrame(confusion), use_container_width=True)
        if not metrics:
            st.info("No modeling was performed for this run.")

    for warning in result.warnings:
        st.warning(warning)

    st.subheader("Key Findings")
    for insight in result.insights:
        st.write(f"- {insight}")

    _render_downloads(result)
    _render_qa_panel(build_run_context(result, target_column))


def _render_downloads(result: Any) -> None:
    st.subheader("Downloads")
    col_md, col_csv = st.columns(2)
    if result.report_path and Path(str(result.report_path)).exists():
        report_text = Path(str(result.report_path)).read_text(encoding="utf-8")
        col_md.download_button(
            "⬇️ Download analysis report (.md)",
            data=report_text,
            file_name="autoanalyst_report.md",
            mime="text/markdown",
        )
    else:
        col_md.caption("Report was not generated for this run.")
    col_csv.download_button(
        "⬇️ Download cleaned data (.csv)",
        data=result.cleaned_df.to_csv(index=False).encode("utf-8"),
        file_name="autoanalyst_cleaned.csv",
        mime="text/csv",
    )


def _render_qa_panel(context: RunContext) -> None:
    st.subheader("Ask about this run")
    llm = _resolve_llm_safe()
    question = st.text_input(
        "Your question",
        placeholder="e.g. How many rows? What is the F1 score? Summarize the findings.",
    )
    if st.button("Ask") and question.strip():
        with st.spinner("Thinking…" if llm else "Looking up facts…"):
            st.markdown(answer_question(context, question, llm=llm))


@st.cache_data(show_spinner=False)
def _llm_enabled() -> bool:
    return load_llm_settings().enabled


def _resolve_llm_safe() -> Any:
    try:
        return create_llm(load_llm_settings())
    except RuntimeError as exc:
        st.sidebar.caption(f"LLM narration off: {exc}")
        return None


mode = st.sidebar.radio("Mode", ["Quick pipeline", "Agent workflow"])
uploaded_file = st.file_uploader("Upload a CSV dataset", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file to start exploring your dataset.")
    st.stop()

try:
    df_preview = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"Could not read the uploaded file: {exc}")
    st.stop()

if mode == "Quick pipeline":
    render_quick_mode(df_preview, [""] + list(df_preview.columns))
else:
    render_agent_mode(uploaded_file, [""] + list(df_preview.columns))
