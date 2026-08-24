"""AutoAnalyst AI — Enterprise Autonomous Data Intelligence Platform & Multi-Agent Studio."""

from __future__ import annotations

import io
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from autoanalyst.agents.graph import AutoAnalystConfig  # noqa: E402
from autoanalyst.agents.llm import load_llm_settings  # noqa: E402
from autoanalyst.agents.qa import answer_question  # noqa: E402
from autoanalyst.agents.supervisor import SupervisedRun  # noqa: E402
from autoanalyst.dashboard.helpers import save_upload_to_temp, trace_to_dataframe  # noqa: E402
from autoanalyst.data_loading.loader import load_dataset  # noqa: E402
from autoanalyst.eda.analyzer import (  # noqa: E402
    get_categorical_frequencies,
    get_correlation_matrix,
    get_outliers_summary,
)
from autoanalyst.memory.run_store import RunStore  # noqa: E402
from autoanalyst.pipeline import PipelineConfig, PipelineResult, run_analysis_pipeline  # noqa: E402
from autoanalyst.reporting.report_generator import (  # noqa: E402
    create_full_report,
    create_html_report,
)

# Page configuration
st.set_page_config(
    page_title="AutoAnalyst AI | Autonomous Data Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise Styling
st.markdown(
    """
    <style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1E293B; margin-bottom: 0px; }
    .main-subtitle { font-size: 1.05rem; color: #64748B; margin-bottom: 24px; }
    .kpi-container {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 0.82rem; font-weight: 600; color: #64748B;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    .kpi-value { font-size: 1.7rem; font-weight: 700; color: #0F172A; margin-top: 4px; }
    .step-badge-ok {
        background: #DCFCE7; color: #15803D; padding: 4px 8px;
        border-radius: 4px; font-weight: 600; font-size: 0.8rem;
    }
    .step-badge-skipped {
        background: #F1F5F9; color: #64748B; padding: 4px 8px;
        border-radius: 4px; font-weight: 600; font-size: 0.8rem;
    }
    .step-badge-error {
        background: #FEE2E2; color: #B91C1C; padding: 4px 8px;
        border-radius: 4px; font-weight: 600; font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "supervised_run" not in st.session_state:
    st.session_state.supervised_run = None
if "run_store" not in st.session_state:
    st.session_state.run_store = RunStore()

# ---------------------------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------------------------
st.sidebar.image("docs/Assets/autoanalyst_banner.png", use_container_width=True)
st.sidebar.markdown("### ⚙️ Pipeline Control")

uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset",
    type=["csv", "xlsx", "xls", "parquet", "json", "sqlite", "db"],
    help="Supports CSV, Excel, Parquet, JSON, and SQLite files.",
)

# Execution Mode
mode = st.sidebar.radio(
    "Execution Architecture",
    ["Fast Autonomous Pipeline", "Multi-Agent Studio (HITL)"],
    index=0,
    help=(
        "Fast Mode executes the full pipeline instantly. "
        "Agent Studio provides step-by-step approvals and live state tracing."
    ),
)

agent_mode = mode == "Multi-Agent Studio (HITL)"
llm_settings = load_llm_settings()

if agent_mode:
    llm_status = f"Enabled ({llm_settings.provider.upper()})" if llm_settings.enabled else "Disabled (Rule Heuristics)"
    st.sidebar.caption(f"🤖 LLM Narration: **{llm_status}**")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Target & Task")

target_col = ""
model_task = "auto"
missing_strategy = "median"

if uploaded_file is not None:
    try:
        suffix = Path(uploaded_file.name).suffix.lower()
        temp_path = save_upload_to_temp(uploaded_file, suffix=suffix)
        df_preview = load_dataset(temp_path)
        col_options = [""] + list(df_preview.columns)
        target_col = st.sidebar.selectbox("Target Column (Optional)", col_options, index=0)
        model_task = st.sidebar.selectbox("Task Type", ["auto", "classification", "regression"], index=0)
        missing_strategy = st.sidebar.selectbox(
            "Imputation Strategy",
            ["median", "mean", "mode", "knn", "forward_fill", "drop"],
            index=0,
        )
    except Exception as exc:
        st.sidebar.error(f"Error reading file preview: {exc}")

require_approval = False
fail_fast = False
if agent_mode:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ Agent Supervisor")
    require_approval = st.sidebar.checkbox("Human-in-the-Loop Approvals", value=True)
    fail_fast = st.sidebar.checkbox("Fail-Fast Circuit Breaker", value=False)

st.sidebar.markdown("---")
run_btn = st.sidebar.button("🚀 Execute Analysis", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Main Content Header
# ---------------------------------------------------------------------------
st.title("AutoAnalyst AI")
st.markdown(
    '<div class="main-subtitle">Enterprise-Grade Autonomous Data Analyst & Multi-Agent Machine Learning Platform</div>',
    unsafe_allow_html=True,
)

if uploaded_file is None:
    st.info(
        "👋 Welcome! Please upload a dataset (CSV, Excel, Parquet, JSON, SQLite) "
        "in the sidebar to begin autonomous analysis."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Execution Logic
# ---------------------------------------------------------------------------
if run_btn:
    with st.spinner("Processing dataset through analytical engine..."):
        try:
            if not agent_mode:
                config = PipelineConfig(
                    target_column=target_col if target_col else None,
                    model_task=model_task,
                    missing_strategy=missing_strategy,
                )
                result = run_analysis_pipeline(temp_path, config=config)
                st.session_state.pipeline_result = result
                st.session_state.supervised_run = None
            else:
                agent_config = AutoAnalystConfig(
                    dataset_path=temp_path,
                    target_column=target_col if target_col else None,
                    require_approval=require_approval,
                    fail_fast=fail_fast,
                    missing_strategy=missing_strategy,
                )
                sup_run = SupervisedRun(agent_config)
                sup_run.start()
                st.session_state.supervised_run = sup_run
                st.session_state.pipeline_result = sup_run.final_result()
        except Exception as exc:
            st.error(f"Execution failed: {exc}")
            st.stop()

# Human In The Loop Modal / Controls if Paused
if agent_mode and st.session_state.supervised_run is not None:
    sup_run = st.session_state.supervised_run
    pending = sup_run.pending_approval()
    if pending:
        st.warning(f"⏸️ **Human-in-the-Loop Gate:** Workflow paused before `{pending}` stage for your review.")
        col_app, col_mod, col_res = st.columns([1, 1, 2])
        if col_app.button(f"✅ Approve {pending.capitalize()}", key=f"app_{pending}"):
            sup_run.approve(pending, True)
            sup_run.resume()
            st.session_state.pipeline_result = sup_run.final_result()
            st.rerun()
        if col_mod.button(f"❌ Skip {pending.capitalize()}", key=f"skip_{pending}"):
            sup_run.approve(pending, False)
            sup_run.resume()
            st.session_state.pipeline_result = sup_run.final_result()
            st.rerun()

result: PipelineResult | None = st.session_state.pipeline_result
if result is None:
    st.info("Dataset uploaded. Click **Execute Analysis** in the sidebar to run the autonomous pipeline.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI Summary Header Cards
# ---------------------------------------------------------------------------
profile = result.profile or {}
health_score = profile.get("health_score", 100.0)
grade = profile.get("quality_grade", "A")
total_rows = result.raw_df.shape[0]
total_cols = result.raw_df.shape[1]
missing_total = int(result.raw_df.isna().sum().sum())
mem_str = profile.get("memory_footprint_formatted", "N/A")

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(
        f'<div class="kpi-container"><div class="kpi-title">Data Quality</div>'
        f'<div class="kpi-value">{health_score:.1f}% ({grade})</div></div>',
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f'<div class="kpi-container"><div class="kpi-title">Total Rows</div>'
        f'<div class="kpi-value">{total_rows:,}</div></div>',
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f'<div class="kpi-container"><div class="kpi-title">Columns</div>'
        f'<div class="kpi-value">{total_cols}</div></div>',
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f'<div class="kpi-container"><div class="kpi-title">Missing Values</div>'
        f'<div class="kpi-value">{missing_total:,}</div></div>',
        unsafe_allow_html=True,
    )
with k5:
    st.markdown(
        f'<div class="kpi-container"><div class="kpi-title">Memory</div><div class="kpi-value">{mem_str}</div></div>',
        unsafe_allow_html=True,
    )
with k6:
    score_label = "N/A"
    if result.evaluation_results:
        if "accuracy" in result.evaluation_results:
            score_label = f"{result.evaluation_results['accuracy'] * 100:.1f}% Acc"
        elif "rmse" in result.evaluation_results:
            score_label = f"{result.evaluation_results['rmse']:.2f} RMSE"
    st.markdown(
        f'<div class="kpi-container"><div class="kpi-title">Model Score</div>'
        f'<div class="kpi-value">{score_label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabbed Workspace
# ---------------------------------------------------------------------------
tabs = st.tabs(
    [
        "📊 Data Profile & Quality",
        "📈 Exploratory Visuals",
        "🤖 ML Models & Diagnostics",
        "💡 Insights & Strategy",
        "🔍 Agent Studio Flow",
        "💬 Conversational Assistant",
        "🕒 Historical Runs",
        "📥 Export Center",
    ]
)

# ---------------------------------------------------------------------------
# Tab 1: Profile & Data Quality
# ---------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Dataset Preview")
    st.dataframe(result.raw_df.head(25), use_container_width=True)

    c_p1, c_p2 = st.columns([1, 1])
    with c_p1:
        st.subheader("Data Quality Dimensions")
        qr = profile.get("quality_report")
        if qr:
            st.metric("Completeness Score", f"{qr.get('completeness_score', 100):.1f}%")
            st.metric("Uniqueness Score", f"{qr.get('uniqueness_score', 100):.1f}%")
            st.metric("Uniformity Score", f"{qr.get('uniformity_score', 100):.1f}%")
            st.metric("Validity Score", f"{qr.get('validity_score', 100):.1f}%")
        else:
            st.info("Standard profile generated.")

    with c_p2:
        st.subheader("Missing Values Report")
        if not result.missing_values_report.empty:
            st.dataframe(result.missing_values_report, use_container_width=True)
        else:
            st.success("Zero missing values detected across all columns.")

# ---------------------------------------------------------------------------
# Tab 2: Exploratory Visuals (Plotly)
# ---------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Interactive Statistical Visualizations")

    num_cols = list(result.raw_df.select_dtypes(include="number").columns)
    if len(num_cols) >= 2:
        st.markdown("#### Correlation Matrix")
        corr_method = st.radio("Correlation Method", ["pearson", "spearman"], horizontal=True)
        corr_matrix = get_correlation_matrix(result.raw_df, method=corr_method)
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="Blues",
            title=f"{corr_method.capitalize()} Correlation Heatmap",
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    if num_cols:
        col_dist1, col_dist2 = st.columns(2)
        with col_dist1:
            selected_num = st.selectbox("Select Numeric Feature for Distribution", num_cols)
            fig_hist = px.histogram(
                result.raw_df,
                x=selected_num,
                marginal="box",
                nbins=30,
                title=f"Distribution & Outlier Boxplot for '{selected_num}'",
                color_discrete_sequence=["#3B82F6"],
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_dist2:
            st.markdown("#### Outlier Summary")
            outlier_df = get_outliers_summary(result.raw_df)
            if not outlier_df.empty:
                st.dataframe(outlier_df, use_container_width=True)

    cat_cols = list(result.raw_df.select_dtypes(include=["object", "category", "string"]).columns)
    if cat_cols:
        st.markdown("#### Categorical Frequency Distributions")
        selected_cat = st.selectbox("Select Categorical Feature", cat_cols)
        freq_df = get_categorical_frequencies(result.raw_df, selected_cat, top_n=10)
        fig_bar = px.bar(
            freq_df,
            x="value",
            y="count",
            text="percent",
            title=f"Top Categories in '{selected_cat}'",
            color_discrete_sequence=["#10B981"],
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------------------------
# Tab 3: ML Models & Diagnostics
# ---------------------------------------------------------------------------
with tabs[2]:
    if result.model_results and result.evaluation_results:
        task = result.model_results.get("task", "classification")
        st.subheader(f"Machine Learning Benchmark — {task.capitalize()}")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### Model Specifications")
            st.json(result.model_results)

        with col_m2:
            st.markdown("#### Core Evaluation Metrics")
            eval_clean = {k: v for k, v in result.evaluation_results.items() if isinstance(v, (int, float))}
            st.json(eval_clean)

        # Classification Specific Visualizations
        if task == "classification":
            cm = result.evaluation_results.get("confusion_matrix")
            if cm:
                st.markdown("#### Confusion Matrix")
                labels = result.evaluation_results.get("classification_report", {}).keys()
                clean_labels = [str(lbl) for lbl in labels if lbl not in {"accuracy", "macro avg", "weighted avg"}][
                    : len(cm)
                ]
                if not clean_labels:
                    clean_labels = [str(i) for i in range(len(cm))]

                fig_cm = px.imshow(
                    cm,
                    text_auto=True,
                    x=clean_labels,
                    y=clean_labels,
                    labels=dict(x="Predicted Class", y="Actual Class"),
                    color_continuous_scale="Viridis",
                )
                st.plotly_chart(fig_cm, use_container_width=True)

        elif task == "regression":
            res_summary = result.evaluation_results.get("residuals_summary")
            if res_summary:
                st.markdown("#### Residuals Diagnostics")
                st.json(res_summary)
    else:
        st.info(
            "No model was trained because no target column was configured. "
            "Configure a target in the sidebar to train models."
        )

# ---------------------------------------------------------------------------
# Tab 4: Insights & Strategy
# ---------------------------------------------------------------------------
with tabs[3]:
    st.subheader("💡 Autonomous Insights & Strategy")
    if result.executive_summary:
        st.markdown("#### Executive Summary")
        st.info(result.executive_summary)

    st.markdown("#### Key Data Findings & Recommendations")
    for insight in result.insights:
        st.markdown(f"- {insight}")

    if result.warnings:
        st.markdown("#### ⚠️ Pipeline Warnings & Non-Fatal Alerts")
        for w in result.warnings:
            st.warning(w)

# ---------------------------------------------------------------------------
# Tab 5: Agent Studio Flow
# ---------------------------------------------------------------------------
with tabs[4]:
    st.subheader("🔍 LangGraph Agent Execution Trace")
    if agent_mode and st.session_state.supervised_run is not None:
        trace_data = st.session_state.supervised_run.trace()
        if trace_data:
            trace_df = trace_to_dataframe(trace_data)
            st.dataframe(trace_df, use_container_width=True)
        else:
            st.info("Workflow initialized; awaiting execution.")
    else:
        st.info(
            "Run in **Multi-Agent Studio (HITL)** mode to observe live "
            "agent transitions, node durations, and supervisor retries."
        )

# ---------------------------------------------------------------------------
# Tab 6: Conversational Assistant
# ---------------------------------------------------------------------------
with tabs[5]:
    st.subheader("💬 Dataset & Model Intelligence Assistant")
    st.caption("Ask questions about feature distributions, missingness, model performance, or business impact.")

    # Quick prompt shortcuts
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_q = None
    if q_col1.button("📊 Explain Dataset Shape"):
        quick_q = "What is the dataset shape and composition?"
    if q_col2.button("⚠️ Check Missing Values"):
        quick_q = "Which columns have missing values?"
    if q_col3.button("🤖 Summarize Model Score"):
        quick_q = "How well did the model perform?"
    if q_col4.button("💡 Top Business Insights"):
        quick_q = "What are the top insights?"

    user_query = st.chat_input("Ask a question about the dataset or model results...")
    active_query = user_query or quick_q

    if active_query:
        answer_obj = answer_question(result, active_query, llm=None)
        st.session_state.chat_history.append((active_query, answer_obj.text, answer_obj.source))

    for q, ans, src in st.session_state.chat_history[-8:]:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.write(ans)
            st.caption(f"Source: {src}")

# ---------------------------------------------------------------------------
# Tab 7: Historical Runs
# ---------------------------------------------------------------------------
with tabs[6]:
    st.subheader("🕒 Historical Runs & Experiment Tracking")
    recent_runs = st.session_state.run_store.list_recent(limit=10)
    if recent_runs:
        records_data = [
            {
                "Run ID": r.run_id[:8],
                "Timestamp": r.created_at,
                "Rows": r.rows,
                "Columns": r.columns,
                "Target": r.target_column or "None",
                "Metrics": json.dumps(r.scalar_metrics),
            }
            for r in recent_runs
        ]
        st.dataframe(pd.DataFrame(records_data), use_container_width=True)
    else:
        st.info("No historical runs recorded yet in `.autoanalyst/runs.jsonl`.")

# ---------------------------------------------------------------------------
# Tab 8: Export Center
# ---------------------------------------------------------------------------
with tabs[7]:
    st.subheader("📥 Export Center — Artifact Downloads")
    st.markdown("Download reports and cleaned artifacts compiled from the current run.")

    e_col1, e_col2, e_col3 = st.columns(3)

    # HTML Report Download
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_html:
        create_html_report(
            tmp_html.name,
            title="AutoAnalyst AI Analysis Report",
            profile=result.profile or {},
            insights=result.insights,
            missing_report=result.missing_values_report,
            eda_results=result.eda_results,
            model_results=result.model_results,
            evaluation_results=result.evaluation_results,
            warnings=result.warnings,
            executive_summary=result.executive_summary,
        )
        html_bytes = Path(tmp_html.name).read_bytes()

    e_col1.download_button(
        label="📄 Download HTML Report",
        data=html_bytes,
        file_name="autoanalyst_report.html",
        mime="text/html",
        use_container_width=True,
    )

    # Markdown Report Download
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp_md:
        create_full_report(
            tmp_md.name,
            title="AutoAnalyst AI Analysis Report",
            profile=result.profile or {},
            insights=result.insights,
            missing_report=result.missing_values_report,
            eda_results=result.eda_results,
            model_results=result.model_results,
            evaluation_results=result.evaluation_results,
            warnings=result.warnings,
            executive_summary=result.executive_summary,
        )
        md_bytes = Path(tmp_md.name).read_bytes()

    e_col2.download_button(
        label="📝 Download Markdown Report",
        data=md_bytes,
        file_name="autoanalyst_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # Cleaned CSV Download
    csv_buffer = io.StringIO()
    result.cleaned_df.to_csv(csv_buffer, index=False)
    e_col3.download_button(
        label="📊 Download Cleaned CSV",
        data=csv_buffer.getvalue(),
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        use_container_width=True,
    )
