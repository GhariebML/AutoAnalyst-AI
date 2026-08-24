"""Autonomous Reporting & Strategy Synthesis Agent for AutoAnalyst AI with OpenRouter LLM reasoning."""

from __future__ import annotations

import logging
from pathlib import Path
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
from autoanalyst.llm.prompts.agents import REPORTING_SYSTEM_PROMPT
from autoanalyst.llm.types import TaskCategory
from autoanalyst.tools.reporting_tools import (
    CompileReportInput,
    CompileReportTool,
    DetectDriftInput,
    DetectDriftTool,
)

logger = logging.getLogger(__name__)


class ReportingLLMSynthesis(BaseModel):
    """Structured LLM output for executive summary and business strategy."""

    executive_summary: str = Field(description="Comprehensive executive strategy narrative")
    key_takeaways: list[str] = Field(default_factory=list, description="Core analytical takeaways")
    business_recommendations: list[str] = Field(default_factory=list, description="Strategic next steps")


class ReportingAgent(BaseAutonomousAgent):
    """Specialized agent responsible for executive synthesis, report generation, and drift monitoring."""

    name = "reporting_agent"
    description = (
        "Synthesizes multi-agent analytical findings, generates executive summaries, and compiles export reports."
    )
    capabilities = ["synthesize_insights", "compile_reports", "monitor_drift"]

    def __init__(self, llm_service: Any | None = None) -> None:
        super().__init__(llm_service=llm_service)
        self.report_tool = CompileReportTool()
        self.drift_tool = DetectDriftTool()

    def _execute(self, state: dict[str, Any]) -> AgentResult:
        actions: list[AgentAction] = []
        findings: list[AgentFinding] = []
        recommendations: list[str] = []
        artifacts: dict[str, Any] = {}

        # 1. Synthesize Executive Insights from accumulated state
        accumulated_findings: list[AgentFinding] = state.get("all_findings", [])
        insights_bullets = [f"{f.category}: {f.fact} {f.recommendation}" for f in accumulated_findings]

        if not insights_bullets:
            insights_bullets = state.get("insights", ["Autonomous analysis successfully completed."])

        # Formulate Baseline Summary
        profile = state.get("profile", {})
        model_results = state.get("model_results")
        eval_results = state.get("evaluation_results")

        raw_df = state.get("raw_df")
        rows = profile.get("rows", raw_df.shape[0] if isinstance(raw_df, pd.DataFrame) else 0)
        cols = profile.get("columns", raw_df.shape[1] if isinstance(raw_df, pd.DataFrame) else 0)
        health = profile.get("health_score", 100.0)

        exec_summary = f"AutoAnalyst AI evaluated {rows:,} records across {cols} features with a data health score of {health:.1f}%. "
        if model_results:
            model_name = model_results.get("champion_model_name") or model_results.get("model_name", "Champion")
            if eval_results and "accuracy" in eval_results:
                exec_summary += f"The {model_name} champion classifier attained {eval_results['accuracy'] * 100:.1f}% accuracy on holdout data."
            elif eval_results and "rmse" in eval_results:
                exec_summary += f"The {model_name} champion regressor achieved RMSE of {eval_results['rmse']:.3f} with R² of {eval_results.get('r2', 0):.3f}."

        # 2. Optional LLM Executive Synthesis (Hybrid Mode)
        if self.llm and self.llm.is_available:
            try:
                state_summary = {
                    "rows": rows,
                    "columns": cols,
                    "health_score": health,
                    "target_column": state.get("target_column"),
                    "task": state.get("task"),
                    "champion_model_name": model_results.get("champion_model_name") if model_results else None,
                    "champion_score": model_results.get("champion_score") if model_results else None,
                }
                messages = ContextBuilder.build_agent_context(
                    system_instruction=REPORTING_SYSTEM_PROMPT,
                    task_objective="Synthesize the multi-agent findings into a cohesive executive strategy summary with strategic takeaways.",
                    state_summary=state_summary,
                    tool_results={
                        "evaluation_metrics": eval_results or {},
                        "model_zoo_leaderboard": model_results.get("leaderboard", []) if model_results else [],
                    },
                    recent_findings=accumulated_findings,
                )
                llm_res = self.llm.generate(
                    task=TaskCategory.REPORTING,
                    messages=messages,
                    response_model=ReportingLLMSynthesis,
                    run_id=state.get("run_id"),
                    agent_name=self.name,
                )
                if llm_res.parsed and isinstance(llm_res.parsed, ReportingLLMSynthesis):
                    synthesis = llm_res.parsed
                    exec_summary = synthesis.executive_summary
                    if synthesis.key_takeaways:
                        insights_bullets = synthesis.key_takeaways
                    if synthesis.business_recommendations:
                        recommendations.extend(synthesis.business_recommendations)
            except Exception as exc:
                logger.warning("LLM reasoning skipped in reporting_agent due to: %s", exc)

        artifacts["executive_summary"] = exec_summary
        artifacts["insights"] = insights_bullets

        # 3. Check Drift against Baseline Reference if present
        ref_record = state.get("reference_record")
        current_df = state.get("raw_df")
        if ref_record is not None and current_df is not None:
            drift_res = self.drift_tool.execute(
                DetectDriftInput(
                    current_df=current_df,
                    reference_record=ref_record,
                    reference_df=state.get("reference_df"),
                )
            )
            actions.append(
                AgentAction(
                    tool_name=self.drift_tool.metadata.name,
                    action_type="drift_detection",
                    status="ok" if drift_res.is_success else "error",
                    duration_ms=drift_res.duration_ms,
                    summary=f"Drift status: {'Clean' if drift_res.data and drift_res.data.is_clean else 'Drift detected'}.",
                )
            )
            if drift_res.is_success and drift_res.data:
                artifacts["drift_report"] = drift_res.data.model_dump()
                if not drift_res.data.is_clean:
                    findings.append(
                        AgentFinding(
                            category="Dataset Drift Alert",
                            fact=f"Distribution drift flagged in columns: {', '.join(drift_res.data.flagged_columns.keys())}.",
                            evidence=f"Warnings: {drift_res.data.warnings}",
                            interpretation="Incoming dataset characteristics deviate from historical baseline distributions.",
                            recommendation="Retrain models on current distribution to prevent performance decay.",
                            confidence=0.92,
                        )
                    )

        # 4. Compile Reports (HTML & Markdown)
        report_dir = Path("reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        html_target = state.get("report_path") or str(report_dir / "autoanalyst_report.html")

        rep_res = self.report_tool.execute(
            CompileReportInput(
                output_path=html_target,
                title="AutoAnalyst AI Autonomous Report",
                format="html",
                profile=profile,
                insights=insights_bullets,
                model_results=model_results,
                evaluation_results=eval_results,
                warnings=state.get("warnings", []),
                executive_summary=exec_summary,
            )
        )
        actions.append(
            AgentAction(
                tool_name=self.report_tool.metadata.name,
                action_type="report_compilation",
                status="ok" if rep_res.is_success else "error",
                duration_ms=rep_res.duration_ms,
                summary=f"Compiled standalone HTML report to '{html_target}'.",
            )
        )

        if rep_res.is_success and rep_res.data:
            artifacts["report_path"] = rep_res.data.file_path

        next_decision = AgentDecision(
            decision="WORKFLOW_COMPLETE",
            reason="All autonomous analytical stages and multi-format reports completed successfully.",
            priority="NORMAL",
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            objective="Synthesize multi-agent analytical findings and compile executive report",
            actions_taken=actions,
            tools_used=[a.tool_name for a in actions],
            findings=findings,
            recommendations=recommendations,
            artifacts=artifacts,
            confidence=0.98,
            next_action=next_decision,
        )
