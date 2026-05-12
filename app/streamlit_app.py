"""Streamlit dashboard starter for AutoAnalyst AI."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from autoanalyst.data_profiling.profiler import get_missing_values_report  # noqa: E402
from autoanalyst.insights.insight_generator import generate_dataset_insights  # noqa: E402

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

st.subheader("Dataset Preview")
st.dataframe(df.head(20), use_container_width=True)
col1, col2, col3 = st.columns(3)
col1.metric("Rows", df.shape[0])
col2.metric("Columns", df.shape[1])
col3.metric("Missing Values", int(df.isna().sum().sum()))
st.subheader("Missing Values Report")
st.dataframe(get_missing_values_report(df), use_container_width=True)
st.subheader("Basic Statistics")
st.dataframe(df.describe(include="all").T, use_container_width=True)
st.subheader("Starter Insights")
for insight in generate_dataset_insights(df):
    st.write(f"- {insight}")
