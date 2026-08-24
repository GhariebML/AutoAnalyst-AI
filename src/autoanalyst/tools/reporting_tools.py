"""Reporting and drift detection tools for AutoAnalyst AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from autoanalyst.agents.drift import detect_drift, drift_warnings
from autoanalyst.reporting.report_generator import (
    create_full_report,
    create_html_report,
    create_json_report,
)
from autoanalyst.tools.base import BaseAnalyticalTool, ToolMetadata


# ---------------------------------------------------------------------------
# 1. CompileReportTool
# ---------------------------------------------------------------------------
class CompileReportInput(BaseModel):
    output_path: str = Field(..., description="Target file path for report")
    title: str = Field("AutoAnalyst AI Executive Report", description="Report title")
    format: Literal["html", "md", "json"] = Field("html", description="Report format")
    profile: dict[str, Any] = Field(default_factory=dict)
    insights: list[str] = Field(default_factory=list)
    model_results: dict[str, Any] | None = None
    evaluation_results: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
    executive_summary: str | None = None


class CompileReportOutput(BaseModel):
    file_path: str
    format: str
    file_size_bytes: int


class CompileReportTool(BaseAnalyticalTool[CompileReportInput, CompileReportOutput]):
    metadata = ToolMetadata(
        name="compile_report",
        description="Compile standalone multi-format analysis reports (HTML, Markdown, JSON).",
        category="reporting",
        tags=["reporting", "html", "export", "markdown"],
    )

    def _run(self, params: CompileReportInput) -> CompileReportOutput:
        out_path = Path(params.output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if params.format == "html" or out_path.suffix == ".html":
            created_path = create_html_report(
                output_path=str(out_path),
                title=params.title,
                profile=params.profile,
                insights=params.insights,
                model_results=params.model_results,
                evaluation_results=params.evaluation_results,
                warnings=params.warnings,
                executive_summary=params.executive_summary,
            )
        elif params.format == "json" or out_path.suffix == ".json":
            created_path = create_json_report(
                output_path=str(out_path),
                title=params.title,
                profile=params.profile,
                insights=params.insights,
                model_results=params.model_results,
                evaluation_results=params.evaluation_results,
                warnings=params.warnings,
                executive_summary=params.executive_summary,
            )
        else:
            created_path = create_full_report(
                output_path=str(out_path),
                title=params.title,
                profile=params.profile,
                insights=params.insights,
                model_results=params.model_results,
                evaluation_results=params.evaluation_results,
                warnings=params.warnings,
                executive_summary=params.executive_summary,
            )

        return CompileReportOutput(
            file_path=str(created_path.resolve()),
            format=params.format,
            file_size_bytes=created_path.stat().st_size,
        )


# ---------------------------------------------------------------------------
# 2. DetectDriftTool
# ---------------------------------------------------------------------------
class DetectDriftInput(BaseModel):
    current_df: Any = Field(..., description="Current dataset DataFrame")
    reference_record: Any = Field(..., description="RunRecord from baseline run")
    reference_df: Any = Field(None, description="Optional baseline dataset DataFrame")


class DetectDriftOutput(BaseModel):
    is_clean: bool
    added_columns: list[str]
    removed_columns: list[str]
    flagged_columns: dict[str, list[str]]
    warnings: list[str]


class DetectDriftTool(BaseAnalyticalTool[DetectDriftInput, DetectDriftOutput]):
    metadata = ToolMetadata(
        name="detect_drift",
        description="Detect schema, distribution, PSI, and Kolmogorov-Smirnov statistical drift against baseline run.",
        category="reporting",
        tags=["drift", "psi", "ks_test", "monitoring"],
    )

    def _run(self, params: DetectDriftInput) -> DetectDriftOutput:
        report = detect_drift(
            df=params.current_df,
            reference=params.reference_record,
            reference_df=params.reference_df,
        )
        warns = drift_warnings(report)
        return DetectDriftOutput(
            is_clean=bool(report.get("clean", True)),
            added_columns=list(report.get("added_columns", [])),
            removed_columns=list(report.get("removed_columns", [])),
            flagged_columns=dict(report.get("flagged_columns", {})),
            warnings=warns,
        )
