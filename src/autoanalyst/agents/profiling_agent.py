"""Autonomous Data Profiling Agent for AutoAnalyst AI with centralized OpenRouter LLM reasoning."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from autoanalyst.agents.base import (
    AgentAction,
    AgentDecision,
    AgentFinding,
    AgentResult,
    BaseAutonomousAgent,
)
from autoanalyst.llm.context import ContextBuilder
from autoanalyst.llm.prompts.agents import PROFILING_SYSTEM_PROMPT
from autoanalyst.llm.types import TaskCategory
from autoanalyst.tools.profiling_tools import (
    MissingnessReportTool,
    ProfileDatasetInput,
    ProfileDatasetTool,
)

logger = logging.getLogger(__name__)


class ProfilingLLMAnalysis(BaseModel):
    """Structured LLM output for Data Profiling diagnosis."""

    executive_diagnosis: str = Field(description="Summary of overall data health and scale")
    key_risks: list[str] = Field(default_factory=list, description="Critical data anomalies and risks")
    recommended_target: str | None = Field(default=None, description="Suggested target column if detectable")
    interpretations: list[str] = Field(default_factory=list, description="Qualitative implications")
    recommendations: list[str] = Field(default_factory=list, description="Actionable downstream steps")


class DataProfilingAgent(BaseAutonomousAgent):
    """Specialized agent responsible for dataset understanding, schema auditing, and data quality scoring."""

    name = "profiling_agent"
    description = (
        "Inspects dataset structure, audits data health dimensions, detects missingness, and scores data quality."
    )
    capabilities = ["profile_dataset", "audit_data_quality", "detect_missingness"]

    def __init__(self, llm_service: Any | None = None) -> None:
        super().__init__(llm_service=llm_service)
        self.profile_tool = ProfileDatasetTool()
        self.missing_tool = MissingnessReportTool()

    def _execute(self, state: dict[str, Any]) -> AgentResult:
        df: pd.DataFrame | None = state.get("raw_df") if state.get("raw_df") is not None else state.get("df")
        if df is None or not isinstance(df, pd.DataFrame):
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective="Understand dataset structure and assess data quality health",
                errors=["No valid pandas DataFrame found in state."],
            )

        actions: list[AgentAction] = []
        findings: list[AgentFinding] = []
        recommendations: list[str] = []

        # 1. Deterministic Tool Execution (Immutable Ground Truth)
        prof_res = self.profile_tool.execute(ProfileDatasetInput(df=df))
        actions.append(
            AgentAction(
                tool_name=self.profile_tool.metadata.name,
                action_type="profiling",
                status="ok" if prof_res.is_success else "error",
                duration_ms=prof_res.duration_ms,
                summary=f"Profiled {df.shape[0]:,} rows and {df.shape[1]} columns.",
            )
        )

        if not prof_res.is_success or prof_res.data is None:
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective="Profile dataset",
                actions_taken=actions,
                errors=[prof_res.error or "Profiling failed"],
            )

        p_data = prof_res.data
        health_score = p_data.health_score

        # 2. Baseline Deterministic Findings
        findings.append(
            AgentFinding(
                category="Dataset Structure",
                fact=f"{p_data.rows:,} rows across {p_data.columns} columns ({p_data.memory_footprint} in memory).",
                evidence=f"Shape: ({p_data.rows}, {p_data.columns})",
                interpretation="Dataset scale is suitable for automated statistical analysis and modeling.",
                recommendation="Proceed with exploratory distribution analysis.",
                confidence=1.0,
            )
        )

        findings.append(
            AgentFinding(
                category="Data Quality Health",
                fact=f"Composite quality health score is {health_score:.1f}% (Grade: {p_data.quality_grade}).",
                evidence=(
                    f"{p_data.missing_cells_total:,} missing cells ({p_data.missing_percentage:.1f}%), "
                    f"{p_data.duplicate_rows:,} duplicate rows."
                ),
                interpretation=(
                    "Data quality is excellent."
                    if health_score >= 85
                    else "Data quality issues detected that require preprocessing."
                ),
                recommendation=(
                    "Route to Preprocessing Agent for targeted imputation and deduplication."
                    if health_score < 90 or p_data.missing_cells_total > 0
                    else "Data is clean; proceed directly to feature exploration."
                ),
                confidence=0.95,
            )
        )

        # 3. Optional LLM Reasoning Layer (Hybrid Mode)
        if self.llm and self.llm.is_available:
            try:
                state_summary = {
                    "rows": p_data.rows,
                    "columns": p_data.columns,
                    "health_score": health_score,
                    "quality_grade": p_data.quality_grade,
                    "missing_percentage": p_data.missing_percentage,
                    "duplicate_rows": p_data.duplicate_rows,
                }
                messages = ContextBuilder.build_agent_context(
                    system_instruction=PROFILING_SYSTEM_PROMPT,
                    task_objective="Evaluate data quality, diagnose critical scale anomalies, and recommend downstream routing.",
                    state_summary=state_summary,
                    tool_results={"profile_dataset": p_data.model_dump()},
                    recent_findings=findings,
                )
                llm_res = self.llm.generate(
                    task=TaskCategory.DATA_PROFILING,
                    messages=messages,
                    response_model=ProfilingLLMAnalysis,
                    run_id=state.get("run_id"),
                    agent_name=self.name,
                )
                if llm_res.parsed and isinstance(llm_res.parsed, ProfilingLLMAnalysis):
                    analysis = llm_res.parsed
                    if analysis.key_risks:
                        findings.append(
                            AgentFinding(
                                category="Schema & Risk Diagnosis",
                                fact=f"Identified {len(analysis.key_risks)} key data risk factors: {', '.join(analysis.key_risks[:2])}.",
                                evidence=analysis.executive_diagnosis,
                                interpretation="; ".join(analysis.interpretations) if analysis.interpretations else "Requires targeted preprocessing.",
                                recommendation="; ".join(analysis.recommendations) if analysis.recommendations else "Proceed with care.",
                                confidence=0.92,
                            )
                        )
                    recommendations.extend(analysis.recommendations)
            except Exception as exc:
                logger.warning("LLM reasoning skipped in profiling_agent due to: %s", exc)

        # 4. Determine Next Pipeline Action
        if p_data.missing_percentage > 5.0 or p_data.duplicate_rows > 0:
            next_decision = AgentDecision(
                decision="TRIGGER_PREPROCESSING",
                reason=(
                    f"Significant data hygiene tasks ({p_data.missing_percentage:.1f}% missingness, "
                    f"{p_data.duplicate_rows} duplicates)."
                ),
                recommended_agent="preprocessing_agent",
                priority="HIGH",
            )
            recommendations.append("Formulate and execute a data cleaning plan before downstream modeling.")
        else:
            next_decision = AgentDecision(
                decision="TRIGGER_EDA",
                reason="Dataset is structurally sound and ready for deep exploratory analysis.",
                recommended_agent="eda_agent",
                priority="NORMAL",
            )
            recommendations.append("Perform correlation, distribution, and outlier exploration.")

        return AgentResult(
            agent_name=self.name,
            status="success",
            objective="Understand dataset structure and assess data quality health",
            actions_taken=actions,
            tools_used=[a.tool_name for a in actions],
            findings=findings,
            recommendations=recommendations,
            artifacts={
                "profile": p_data.model_dump(),
                "health_score": health_score,
                "columns": list(df.columns),
                "rows": len(df),
            },
            confidence=0.98,
            next_action=next_decision,
        )
