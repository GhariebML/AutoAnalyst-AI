"""Autonomous Exploratory Data Analysis (EDA) Agent for AutoAnalyst AI."""

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
from autoanalyst.tools.eda_tools import (
    CorrelationAnalysisTool,
    CorrelationInput,
    DistributionAnalysisTool,
    DistributionInput,
    OutlierDetectionInput,
    OutlierDetectionTool,
)


class EDAAgent(BaseAutonomousAgent):
    """Specialized agent responsible for statistical exploration, correlation analysis, and anomaly discovery."""

    name = "eda_agent"
    description = "Investigates statistical distributions, discovers correlation patterns, and quantifies anomalies."
    capabilities = ["correlation_analysis", "distribution_analysis", "outlier_detection"]

    def __init__(self, llm_service: Any | None = None) -> None:
        super().__init__(llm_service=llm_service)
        self.corr_tool = CorrelationAnalysisTool()
        self.dist_tool = DistributionAnalysisTool()
        self.outlier_tool = OutlierDetectionTool()

    def _execute(self, state: dict[str, Any]) -> AgentResult:
        if state.get("cleaned_df") is not None:
            df = state.get("cleaned_df")
        elif state.get("raw_df") is not None:
            df = state.get("raw_df")
        else:
            df = state.get("df")

        if df is None or not isinstance(df, pd.DataFrame):
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective="Explore statistical patterns, feature interactions, and outliers",
                errors=["No valid pandas DataFrame found in state."],
            )

        actions: list[AgentAction] = []
        findings: list[AgentFinding] = []
        recommendations: list[str] = []
        artifacts: dict[str, Any] = {}

        # 1. Distribution Analysis
        dist_res = self.dist_tool.execute(DistributionInput(df=df))
        actions.append(
            AgentAction(
                tool_name=self.dist_tool.metadata.name,
                action_type="distribution_analysis",
                status="ok" if dist_res.is_success else "error",
                duration_ms=dist_res.duration_ms,
                summary=f"Analyzed distributions for {len(df.select_dtypes(include='number').columns)} numeric columns.",
            )
        )
        if dist_res.is_success and dist_res.data:
            artifacts["distributions"] = dist_res.data.distributions
            skewed_cols = [d["column"] for d in dist_res.data.distributions if abs(d.get("skewness", 0)) > 1.5]
            if skewed_cols:
                findings.append(
                    AgentFinding(
                        category="Distribution Skewness",
                        fact=f"High skewness detected in {len(skewed_cols)} feature(s): {', '.join(skewed_cols[:3])}.",
                        evidence=f"Columns with |skewness| > 1.5: {skewed_cols}",
                        interpretation="Asymmetric distributions can bias linear estimators and sensitive distance metrics.",
                        recommendation="Apply robust scaling or log-transformation during preprocessing.",
                        confidence=0.92,
                    )
                )

        # 2. Correlation Analysis
        corr_res = self.corr_tool.execute(CorrelationInput(df=df, method="pearson", threshold=0.5))
        actions.append(
            AgentAction(
                tool_name=self.corr_tool.metadata.name,
                action_type="correlation_analysis",
                status="ok" if corr_res.is_success else "error",
                duration_ms=corr_res.duration_ms,
                summary=f"Found {len(corr_res.data.strong_relationships) if corr_res.data else 0} strong feature pairs.",
            )
        )
        if corr_res.is_success and corr_res.data:
            artifacts["correlation_matrix"] = corr_res.data.matrix
            artifacts["strong_relationships"] = corr_res.data.strong_relationships
            if corr_res.data.strong_relationships:
                top = corr_res.data.strong_relationships[0]
                findings.append(
                    AgentFinding(
                        category="Feature Relationships",
                        fact=f"Strong correlation between '{top['feature_a']}' and '{top['feature_b']}' (r = {top['correlation']:.2f}).",
                        evidence=f"{len(corr_res.data.strong_relationships)} pairs exhibited |r| >= 0.50.",
                        interpretation="Key linear associations exist that can provide predictive signal or collinearity risk.",
                        recommendation="Consider both features as candidate predictors while monitoring collinearity.",
                        confidence=0.95,
                    )
                )

        # 3. Outlier Detection
        out_res = self.outlier_tool.execute(OutlierDetectionInput(df=df, method="iqr"))
        actions.append(
            AgentAction(
                tool_name=self.outlier_tool.metadata.name,
                action_type="outlier_detection",
                status="ok" if out_res.is_success else "error",
                duration_ms=out_res.duration_ms,
                summary=f"Detected {out_res.data.total_outliers_detected if out_res.data else 0} outlier entries.",
            )
        )
        if out_res.is_success and out_res.data:
            artifacts["outliers_summary"] = out_res.data.outlier_summary
            if out_res.data.total_outliers_detected > 0:
                findings.append(
                    AgentFinding(
                        category="Anomalies & Outliers",
                        fact=f"{out_res.data.total_outliers_detected:,} outlier values identified across numeric attributes.",
                        evidence=f"IQR summary: {out_res.data.outlier_summary[:3]}",
                        interpretation="Outliers may represent high-leverage points or extreme natural variability.",
                        recommendation="Apply percentile Winsorization to cap extreme tails without data loss.",
                        confidence=0.90,
                    )
                )

        target_col = state.get("target_column")
        if target_col and target_col in df.columns:
            next_decision = AgentDecision(
                decision="TRIGGER_PREPROCESSING_OR_ML",
                reason=f"Target column '{target_col}' identified with exploratory patterns mapped.",
                recommended_agent="preprocessing_agent",
                priority="HIGH",
            )
            recommendations.append(f"Prepare model-ready feature transformations for target '{target_col}'.")
        else:
            next_decision = AgentDecision(
                decision="COMPLETE_EXPLORATION",
                reason="Statistical exploratory analysis completed across all features.",
                recommended_agent="reporting_agent",
                priority="NORMAL",
            )
            recommendations.append("Synthesize exploratory findings into executive dashboard report.")

        return AgentResult(
            agent_name=self.name,
            status="success",
            objective="Explore statistical distributions, feature interactions, and anomalies",
            actions_taken=actions,
            tools_used=[a.tool_name for a in actions],
            findings=findings,
            recommendations=recommendations,
            artifacts=artifacts,
            confidence=0.96,
            next_action=next_decision,
        )
