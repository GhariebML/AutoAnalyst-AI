"""LangChain-compatible tools wrapping the deterministic AutoAnalyst modules.

This is layer L1 of the multiagent architecture (see
``docs/multiagent_completion_plan.md``). Each tool delegates to an existing
module function so agent workflows stay reproducible and fully testable
without any LLM configured.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from langchain_core.tools import BaseTool, tool

from autoanalyst.data_profiling.profiler import generate_basic_profile, get_missing_values_report
from autoanalyst.eda.analyzer import get_correlation_matrix, get_numeric_summary
from autoanalyst.feature_engineering.feature_builder import (
    detect_high_cardinality_columns,
    encode_categorical_columns,
)
from autoanalyst.insights.insight_generator import generate_dataset_insights
from autoanalyst.pipeline import load_dataset
from autoanalyst.preprocessing.cleaner import handle_missing_values, remove_duplicates
from autoanalyst.reporting.report_generator import create_full_report, create_markdown_report


@tool
def load_dataset_tool(file_path: str) -> pd.DataFrame:
    """Load a tabular dataset from a CSV or Excel file path."""
    return load_dataset(file_path)


@tool
def profile_dataset_tool(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a compact profile: shape, dtypes, missing values, duplicate rows."""
    return generate_basic_profile(df)


@tool
def missing_values_report_tool(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-column missing value counts and percentages, sorted by severity."""
    return get_missing_values_report(df)


@tool
def numeric_summary_tool(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics (count, mean, std, quartiles) for numeric columns."""
    return get_numeric_summary(df)


@tool
def correlation_matrix_tool(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Return the correlation matrix for numeric columns (pearson, kendall, spearman)."""
    return get_correlation_matrix(df, method=method)


@tool
def detect_high_cardinality_tool(df: pd.DataFrame) -> list[dict[str, int | float | str]]:
    """Detect categorical columns with unusually high cardinality before encoding."""
    return detect_high_cardinality_columns(df)


@tool
def clean_missing_values_tool(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Remove duplicate rows, then impute missing values (median, mean, mode, or drop)."""
    return handle_missing_values(remove_duplicates(df), strategy=strategy)


@tool
def encode_categoricals_tool(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode all categorical columns, warning on high-cardinality ones."""
    selected = list(df.select_dtypes(include=["object", "category", "string"]).columns)
    return encode_categorical_columns(df, columns=selected)


@tool
def generate_insights_tool(df: pd.DataFrame) -> list[str]:
    """Generate rule-based, human-readable insights from a cleaned dataset."""
    return generate_dataset_insights(df)


@tool
def create_report_tool(insights: list[str], output_path: str, title: str = "AutoAnalyst AI Report") -> str:
    """Write a Markdown insights report to output_path and return the path as a string."""
    return str(create_markdown_report(title, insights, output_path))


@tool
def create_full_report_tool(
    profile: dict[str, Any],
    insights: list[str],
    output_path: str,
    title: str = "AutoAnalyst AI Report",
    missing_report: pd.DataFrame | None = None,
    eda_results: dict[str, Any] | None = None,
    cleaning_log: list[str] | None = None,
    model_results: dict[str, Any] | None = None,
    evaluation_results: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
) -> str:
    """Write a complete Markdown analysis report (overview, EDA, metrics, insights) to output_path."""
    return str(
        create_full_report(
            output_path=output_path,
            title=title,
            profile=profile,
            insights=insights,
            missing_report=missing_report,
            eda_results=eda_results,
            cleaning_log=cleaning_log,
            model_results=model_results,
            evaluation_results=evaluation_results,
            warnings=warnings,
        )
    )


ALL_TOOLS: list[BaseTool] = [
    load_dataset_tool,
    profile_dataset_tool,
    missing_values_report_tool,
    numeric_summary_tool,
    correlation_matrix_tool,
    detect_high_cardinality_tool,
    clean_missing_values_tool,
    encode_categoricals_tool,
    generate_insights_tool,
    create_report_tool,
    create_full_report_tool,
]

__all__ = [
    "ALL_TOOLS",
    "clean_missing_values_tool",
    "correlation_matrix_tool",
    "create_full_report_tool",
    "create_report_tool",
    "detect_high_cardinality_tool",
    "encode_categoricals_tool",
    "generate_insights_tool",
    "load_dataset_tool",
    "missing_values_report_tool",
    "numeric_summary_tool",
    "profile_dataset_tool",
]
