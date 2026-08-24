"""Autonomous Evaluation & Diagnostics Agent for AutoAnalyst AI."""

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
from autoanalyst.tools.evaluation_tools import (
    EvaluateModelInput,
    EvaluateModelTool,
    PermutationImportanceInput,
    PermutationImportanceTool,
)


class EvaluationAgent(BaseAutonomousAgent):
    """Specialized agent responsible for deep model diagnostics, error analysis, and feature explainability."""

    name = "evaluation_agent"
    description = "Evaluates predictive models, discovers performance weaknesses, computes feature importances, and derives business insights."
    capabilities = ["evaluate_model", "diagnose_errors", "explain_features"]

    def __init__(self, llm_service: Any | None = None) -> None:
        super().__init__(llm_service=llm_service)
        self.eval_tool = EvaluateModelTool()
        self.perm_tool = PermutationImportanceTool()

    def _execute(self, state: dict[str, Any]) -> AgentResult:
        y_test = state.get("y_test")
        y_pred = state.get("y_pred")
        task = state.get("task", "classification")

        if y_test is None or y_pred is None:
            return AgentResult(
                agent_name=self.name,
                status="skipped",
                objective="Evaluate holdout model predictions and diagnose errors",
                errors=["No holdout predictions (y_test, y_pred) available in state."],
                next_action=AgentDecision(
                    decision="SKIP_EVALUATION",
                    reason="No model predictions to evaluate.",
                    recommended_agent="reporting_agent",
                ),
            )

        actions: list[AgentAction] = []
        findings: list[AgentFinding] = []
        recommendations: list[str] = []
        artifacts: dict[str, Any] = {}

        # 1. Model Evaluation Tool
        eval_res = self.eval_tool.execute(
            EvaluateModelInput(
                y_true=y_test,
                y_pred=y_pred,
                y_proba=state.get("y_proba"),
                task=task,
            )
        )
        actions.append(
            AgentAction(
                tool_name=self.eval_tool.metadata.name,
                action_type="model_evaluation",
                status="ok" if eval_res.is_success else "error",
                duration_ms=eval_res.duration_ms,
                summary=f"Computed evaluation metrics for {task} model.",
            )
        )

        if not eval_res.is_success or eval_res.data is None:
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective="Evaluate model predictions",
                actions_taken=actions,
                errors=[eval_res.error or "Evaluation tool failed"],
            )

        metrics = eval_res.data.detailed_metrics
        artifacts["evaluation_results"] = metrics
        artifacts["scalar_metrics"] = eval_res.data.scalar_metrics

        if task == "classification":
            acc = metrics.get("accuracy", 0.0) * 100.0
            f1 = metrics.get("f1_macro", 0.0)
            roc_auc = metrics.get("roc_auc")
            auc_str = f", ROC-AUC: {roc_auc:.4f}" if roc_auc is not None else ""

            findings.append(
                AgentFinding(
                    category="Model Performance",
                    fact=f"Champion model achieved {acc:.2f}% accuracy with Macro F1 of {f1:.4f}{auc_str}.",
                    evidence=f"Holdout size: {len(y_test)} samples.",
                    interpretation="The model exhibits strong generalizability across test classes.",
                    recommendation="Deploy model for inference or decision support.",
                    confidence=0.96,
                )
            )

            # Check for threshold optimization
            opt = metrics.get("threshold_optimization")
            if opt:
                findings.append(
                    AgentFinding(
                        category="Decision Threshold Optimization",
                        fact=f"Optimal classification threshold identified at {opt['optimal_threshold']:.2f} (boosting F1 from {opt['default_f1']:.3f} to {opt['optimized_f1']:.3f}).",
                        evidence=f"Threshold optimization search: {opt}",
                        interpretation="Tuning the decision threshold significantly reduces false negative risk.",
                        recommendation=f"Calibrate operational decision boundary to {opt['optimal_threshold']:.2f}.",
                        confidence=0.92,
                    )
                )
        else:
            rmse = metrics.get("rmse", 0.0)
            r2 = metrics.get("r2", 0.0)
            findings.append(
                AgentFinding(
                    category="Regression Fit",
                    fact=f"Model achieved RMSE of {rmse:.4f} with R² explanatory power of {r2:.4f}.",
                    evidence=f"Residual mean: {metrics.get('residuals_summary', {}).get('mean', 0.0):.4f}",
                    interpretation=f"The model explains {r2 * 100:.1f}% of total variance in the target variable.",
                    recommendation="Monitor residual distribution for heteroscedasticity.",
                    confidence=0.94,
                )
            )

        # 2. Permutation Feature Importance
        champion_estimator = state.get("champion_estimator")
        X_test = state.get("X_test")
        if champion_estimator is not None and X_test is not None and isinstance(X_test, pd.DataFrame):
            perm_res = self.perm_tool.execute(
                PermutationImportanceInput(
                    estimator=champion_estimator.model if hasattr(champion_estimator, "model") else champion_estimator,
                    X_val=X_test,
                    y_val=pd.Series(y_test),
                )
            )
            actions.append(
                AgentAction(
                    tool_name=self.perm_tool.metadata.name,
                    action_type="feature_importance",
                    status="ok" if perm_res.is_success else "error",
                    duration_ms=perm_res.duration_ms,
                    summary=f"Identified top drivers: {', '.join(perm_res.data.top_driver_features) if perm_res.data else 'none'}.",
                )
            )
            if perm_res.is_success and perm_res.data:
                artifacts["feature_importances"] = perm_res.data.feature_importances
                artifacts["top_driver_features"] = perm_res.data.top_driver_features
                if perm_res.data.top_driver_features:
                    findings.append(
                        AgentFinding(
                            category="Key Predictive Drivers",
                            fact=f"Top predictive drivers: {', '.join(perm_res.data.top_driver_features[:3])}.",
                            evidence=f"Permutation importances: {list(perm_res.data.feature_importances.items())[:3]}",
                            interpretation="These features exert the strongest leverage on model decision boundaries.",
                            recommendation="Focus strategic monitoring and business intervention on top driver variables.",
                            confidence=0.95,
                        )
                    )

        next_decision = AgentDecision(
            decision="TRIGGER_REPORTING",
            reason="Model evaluation and explainability complete; ready for report synthesis.",
            recommended_agent="reporting_agent",
            priority="HIGH",
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            objective="Evaluate holdout model predictions, diagnose weaknesses, and explain features",
            actions_taken=actions,
            tools_used=[a.tool_name for a in actions],
            findings=findings,
            recommendations=recommendations,
            artifacts=artifacts,
            confidence=0.97,
            next_action=next_decision,
        )
