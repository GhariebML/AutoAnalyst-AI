"""Data profiling and quality health scoring tools for AutoAnalyst AI."""

from __future__ import annotations

from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from autoanalyst.data_profiling.profiler import (
    get_missing_values_report,
    profile_dataframe,
)
from autoanalyst.tools.base import BaseAnalyticalTool, ToolMetadata


# ---------------------------------------------------------------------------
# 1. ProfileDatasetTool
# ---------------------------------------------------------------------------
class ProfileDatasetInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to profile")
    include_distributions: bool = Field(True, description="Whether to include numeric distribution metrics")


class ProfileDatasetOutput(BaseModel):
    rows: int
    columns: int
    missing_cells_total: int
    missing_percentage: float
    duplicate_rows: int
    duplicate_percentage: float
    health_score: float
    quality_grade: str
    column_profiles: dict[str, Any]
    memory_footprint: str


class ProfileDatasetTool(BaseAnalyticalTool[ProfileDatasetInput, ProfileDatasetOutput]):
    metadata = ToolMetadata(
        name="profile_dataset",
        description="Comprehensive dataset profiling, schema metrics, and quality health scoring.",
        category="profiling",
        tags=["profiling", "quality", "health_score"],
    )

    def _run(self, params: ProfileDatasetInput) -> ProfileDatasetOutput:
        if not isinstance(params.df, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame for profiling.")
        profile = profile_dataframe(params.df)
        col_dict = {
            name: (p.to_dict() if hasattr(p, "to_dict") else p)
            for name, p in profile.column_profiles.items()
        }
        return ProfileDatasetOutput(
            rows=profile.rows,
            columns=profile.columns,
            missing_cells_total=profile.missing_values_total,
            missing_percentage=profile.missing_cells_percentage,
            duplicate_rows=profile.duplicate_rows,
            duplicate_percentage=profile.duplicate_rows_percentage,
            health_score=profile.quality_report.health_score,
            quality_grade=profile.quality_report.grade,
            column_profiles=col_dict,
            memory_footprint=profile.memory_footprint_formatted,
        )


# ---------------------------------------------------------------------------
# 2. MissingnessReportTool
# ---------------------------------------------------------------------------
class MissingnessReportInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to analyze for missing values")


class MissingnessReportOutput(BaseModel):
    total_missing: int
    has_missing_values: bool
    columns_with_missing: list[dict[str, Any]]


class MissingnessReportTool(BaseAnalyticalTool[MissingnessReportInput, MissingnessReportOutput]):
    metadata = ToolMetadata(
        name="calculate_missingness",
        description="Calculate column-by-column missing value counts and percentages sorted by severity.",
        category="profiling",
        tags=["missingness", "nulls", "audit"],
    )

    def _run(self, params: MissingnessReportInput) -> MissingnessReportOutput:
        if not isinstance(params.df, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame for missingness report.")
        report_df = get_missing_values_report(params.df)
        total_missing = int(params.df.isna().sum().sum())
        cols = report_df.to_dict(orient="records") if not report_df.empty else []
        return MissingnessReportOutput(
            total_missing=total_missing,
            has_missing_values=total_missing > 0,
            columns_with_missing=cols,
        )
