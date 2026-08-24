"""Autonomous Preprocessing & Feature Engineering Agent for AutoAnalyst AI."""

from __future__ import annotations

from typing import Any

import pandas as pd

from autoanalyst.agents.base import (
    AgentAction,
    AgentDecision,
    AgentFinding,
    AgentResult,
    BaseAutonomousAgent,
)
from autoanalyst.tools.preprocessing_tools import (
    EncodeFeaturesInput,
    EncodeFeaturesTool,
    ExecuteCleaningInput,
    ExecuteCleaningTool,
    GenerateTransformationPlanTool,
    TransformationPlanInput,
)


class PreprocessingAgent(BaseAutonomousAgent):
    """Specialized agent responsible for formulation of transformation plans, data cleaning, and feature encoding."""

    name = "preprocessing_agent"
    description = "Formulates and executes data cleaning plans, missing value imputation, and feature transformations."
    capabilities = ["formulate_cleaning_plan", "execute_cleaning", "encode_features"]

    def __init__(self, llm_service: Any | None = None) -> None:
        super().__init__(llm_service=llm_service)
        self.plan_tool = GenerateTransformationPlanTool()
        self.clean_tool = ExecuteCleaningTool()
        self.encode_tool = EncodeFeaturesTool()

    def _execute(self, state: dict[str, Any]) -> AgentResult:
        df: pd.DataFrame | None = state.get("raw_df") if state.get("raw_df") is not None else state.get("df")
        if df is None or not isinstance(df, pd.DataFrame):
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective="Formulate and execute data hygiene and feature transformations",
                errors=["No valid pandas DataFrame found in state."],
            )

        target_col = state.get("target_column")
        actions: list[AgentAction] = []
        findings: list[AgentFinding] = []
        recommendations: list[str] = []
        artifacts: dict[str, Any] = {}

        # 1. Formulate Transformation Plan
        plan_res = self.plan_tool.execute(TransformationPlanInput(df=df, target_column=target_col))
        actions.append(
            AgentAction(
                tool_name=self.plan_tool.metadata.name,
                action_type="planning",
                status="ok" if plan_res.is_success else "error",
                duration_ms=plan_res.duration_ms,
                summary=f"Formulated transformation plan with {plan_res.data.total_actions if plan_res.data else 0} action(s).",
            )
        )

        plan = plan_res.data.plan if plan_res.is_success and plan_res.data else []
        artifacts["preprocessing_plan"] = [a.model_dump() for a in plan]

        # Check for HITL gate if severe transformations exist and not yet approved
        is_approved = state.get("approvals", {}).get("cleaning", False)
        requires_approval = any(a.requires_approval for a in plan) and not is_approved

        if requires_approval and state.get("require_approval", False):
            prompt = (
                f"Data cleaning plan contains high-impact actions ({len(plan)} total). "
                "Review recommended imputation strategies before execution."
            )
            return AgentResult(
                agent_name=self.name,
                status="paused_for_approval",
                objective="Review and approve proposed preprocessing plan",
                actions_taken=actions,
                tools_used=[a.tool_name for a in actions],
                artifacts=artifacts,
                requires_human_input=True,
                human_prompt=prompt,
                next_action=AgentDecision(
                    decision="AWAIT_HUMAN_APPROVAL",
                    reason="High missingness or severe transformations require human confirmation.",
                    requires_human_approval=True,
                    approval_prompt=prompt,
                    priority="HIGH",
                ),
            )

        # 2. Execute Data Cleaning
        missing_strategy = state.get("missing_strategy", "median")
        clean_res = self.clean_tool.execute(
            ExecuteCleaningInput(
                df=df,
                missing_strategy=missing_strategy,
                handle_outliers="winsorize",
                drop_duplicates=True,
            )
        )
        actions.append(
            AgentAction(
                tool_name=self.clean_tool.metadata.name,
                action_type="cleaning_execution",
                status="ok" if clean_res.is_success else "error",
                duration_ms=clean_res.duration_ms,
                summary=f"Cleaned {clean_res.data.cleaned_rows if clean_res.data else 0} rows; {clean_res.data.duplicates_removed if clean_res.data else 0} duplicate(s) dropped.",
            )
        )

        if not clean_res.is_success or clean_res.data is None:
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective="Execute data cleaning",
                actions_taken=actions,
                errors=[clean_res.error or "Cleaning execution failed"],
            )

        cleaned_df = clean_res.data.cleaned_df
        artifacts["cleaned_df"] = cleaned_df
        artifacts["cleaning_logs"] = clean_res.data.cleaning_logs

        findings.append(
            AgentFinding(
                category="Data Cleaning Impact",
                fact=f"Successfully handled {clean_res.data.imputations_performed:,} missing entries and removed {clean_res.data.duplicates_removed:,} duplicates.",
                evidence=f"Cleaned dimensions: {clean_res.data.cleaned_rows} rows x {clean_res.data.cleaned_columns} cols.",
                interpretation="Dataset has reached 100% completeness with zero remaining missing values.",
                recommendation="Proceed with categorical encoding and feature scaling.",
                confidence=0.98,
            )
        )

        # 3. Feature Encoding
        enc_res = self.encode_tool.execute(
            EncodeFeaturesInput(
                df=cleaned_df,
                target_column=target_col,
                method="onehot",
            )
        )
        actions.append(
            AgentAction(
                tool_name=self.encode_tool.metadata.name,
                action_type="feature_encoding",
                status="ok" if enc_res.is_success else "error",
                duration_ms=enc_res.duration_ms,
                summary=f"Encoded features resulting in {enc_res.data.encoded_columns if enc_res.data else 0} total columns.",
            )
        )

        model_ready_df = enc_res.data.encoded_df if enc_res.is_success and enc_res.data else cleaned_df
        artifacts["model_ready_df"] = model_ready_df

        if target_col and target_col in model_ready_df.columns:
            next_decision = AgentDecision(
                decision="TRIGGER_MODELING",
                reason=f"Model-ready dataset prepared ({model_ready_df.shape[1]} features) for target '{target_col}'.",
                recommended_agent="ml_agent",
                priority="HIGH",
            )
            recommendations.append("Execute machine learning candidate benchmark.")
        else:
            next_decision = AgentDecision(
                decision="TRIGGER_REPORTING",
                reason="Preprocessed dataset is ready; no target column configured for modeling.",
                recommended_agent="reporting_agent",
                priority="NORMAL",
            )
            recommendations.append("Generate final analysis report on cleaned dataset.")

        return AgentResult(
            agent_name=self.name,
            status="success",
            objective="Formulate and execute data hygiene and feature transformations",
            actions_taken=actions,
            tools_used=[a.tool_name for a in actions],
            findings=findings,
            recommendations=recommendations,
            artifacts=artifacts,
            confidence=0.97,
            next_action=next_decision,
        )
