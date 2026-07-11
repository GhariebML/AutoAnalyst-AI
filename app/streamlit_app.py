"""Streamlit dashboard for AutoAnalyst AI."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from autoanalyst.pipeline import PipelineConfig, run_analysis_pipeline  # noqa: E402

st.set_page_config(page_title="AutoAnalyst AI", page_icon="📊", layout="wide")
st.title("📊 AutoAnalyst AI")
st.caption("Automated AI-Powered Data Analyst System")

uploaded_file = st.file_uploader("Upload a CSV dataset", type=["csv"])
if uploaded_file is None:
    st.info("Upload a CSV file to start exploring your dataset.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"Could not read the uploaded file: {exc}")
    st.stop()

st.sidebar.header("Pipeline Options")
target_options = [""] + list(df.columns)
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
