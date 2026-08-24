"""Exploratory data analysis (EDA) tools for AutoAnalyst AI."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from autoanalyst.eda.analyzer import (
    get_correlation_matrix,
    get_distribution_overview,
    get_numeric_summary,
    get_outliers_summary,
)
from autoanalyst.tools.base import BaseAnalyticalTool, ToolMetadata


# ---------------------------------------------------------------------------
# 1. CorrelationAnalysisTool
# ---------------------------------------------------------------------------
class CorrelationInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to analyze")
    method: Literal["pearson", "spearman", "kendall"] = Field("pearson", description="Correlation method")
    threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum absolute correlation to highlight strong pairs")


class CorrelationOutput(BaseModel):
    method: str
    matrix: dict[str, dict[str, float]]
    strong_relationships: list[dict[str, Any]]


class CorrelationAnalysisTool(BaseAnalyticalTool[CorrelationInput, CorrelationOutput]):
    metadata = ToolMetadata(
        name="correlation_analysis",
        description="Compute correlation matrix and highlight strong linear/monotonic relationships.",
        category="eda",
        tags=["correlation", "bivariate", "relationships"],
    )

    def _run(self, params: CorrelationInput) -> CorrelationOutput:
        corr_df = get_correlation_matrix(params.df, method=params.method)
        matrix_dict = corr_df.to_dict()

        strong: list[dict[str, Any]] = []
        cols = list(corr_df.columns)
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = float(corr_df.iloc[i, j])
                if abs(val) >= params.threshold:
                    strong.append(
                        {
                            "feature_a": str(cols[i]),
                            "feature_b": str(cols[j]),
                            "correlation": round(val, 4),
                            "direction": "positive" if val > 0 else "negative",
                        }
                    )

        strong.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        return CorrelationOutput(
            method=params.method,
            matrix=matrix_dict,
            strong_relationships=strong,
        )


# ---------------------------------------------------------------------------
# 2. DistributionAnalysisTool
# ---------------------------------------------------------------------------
class DistributionInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to analyze")


class DistributionOutput(BaseModel):
    numeric_summary: dict[str, dict[str, Any]]
    distributions: list[dict[str, Any]]


class DistributionAnalysisTool(BaseAnalyticalTool[DistributionInput, DistributionOutput]):
    metadata = ToolMetadata(
        name="distribution_analysis",
        description="Analyze feature distributions, skewness, kurtosis, and statistical normality tests.",
        category="eda",
        tags=["distribution", "normality", "skewness"],
    )

    def _run(self, params: DistributionInput) -> DistributionOutput:
        summary_df = get_numeric_summary(params.df)
        dist_df = get_distribution_overview(params.df).reset_index()
        return DistributionOutput(
            numeric_summary=summary_df.to_dict() if not summary_df.empty else {},
            distributions=dist_df.to_dict(orient="records") if not dist_df.empty else [],
        )


# ---------------------------------------------------------------------------
# 3. OutlierDetectionTool
# ---------------------------------------------------------------------------
class OutlierDetectionInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to check for outliers")
    method: Literal["iqr", "zscore"] = Field("iqr", description="Outlier detection method")
    columns: list[str] | None = Field(None, description="Optional specific columns to inspect")


class OutlierDetectionOutput(BaseModel):
    method: str
    outlier_summary: list[dict[str, Any]]
    total_outliers_detected: int


class OutlierDetectionTool(BaseAnalyticalTool[OutlierDetectionInput, OutlierDetectionOutput]):
    metadata = ToolMetadata(
        name="outlier_detection",
        description="Identify statistical anomalies using IQR interquartile range or Z-score thresholds.",
        category="eda",
        tags=["outliers", "anomalies", "iqr", "zscore"],
    )

    def _run(self, params: OutlierDetectionInput) -> OutlierDetectionOutput:
        target_df = params.df[params.columns] if params.columns else params.df
        outlier_df = get_outliers_summary(target_df, method=params.method)
        records = outlier_df.to_dict(orient="records") if not outlier_df.empty else []
        total = sum(r.get("count", r.get("outliers_count", 0)) for r in records)
        return OutlierDetectionOutput(
            method=params.method,
            outlier_summary=records,
            total_outliers_detected=total,
        )
