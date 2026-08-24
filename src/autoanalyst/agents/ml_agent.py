"""Autonomous Machine Learning Agent for AutoAnalyst AI."""

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
from autoanalyst.tools.ml_tools import (
    BenchmarkModelsInput,
    BenchmarkModelsTool,
    InferMLTaskInput,
    InferMLTaskTool,
)


class MachineLearningAgent(BaseAutonomousAgent):
    """Specialized agent responsible for problem formulation, model zoo benchmarking, and champion model selection."""

    name = "ml_agent"
    description = "Formulates predictive ML tasks, benchmarks candidate model zoo, and optimizes champion models."
    capabilities = ["infer_task", "benchmark_models", "train_champion"]

    def __init__(self, llm_service: Any | None = None) -> None:
        super().__init__(llm_service=llm_service)
        self.task_tool = InferMLTaskTool()
        self.bench_tool = BenchmarkModelsTool()

    def _execute(self, state: dict[str, Any]) -> AgentResult:
        if state.get("model_ready_df") is not None:
            df = state.get("model_ready_df")
        elif state.get("cleaned_df") is not None:
            df = state.get("cleaned_df")
        else:
            df = state.get("df")
        target_col = state.get("target_column")

        if df is None or not isinstance(df, pd.DataFrame) or not target_col or target_col not in df.columns:
            return AgentResult(
                agent_name=self.name,
                status="skipped",
                objective="Benchmark predictive models and select champion estimator",
                errors=["No target column configured or target not present in dataset."],
                next_action=AgentDecision(
                    decision="SKIP_MODELING",
                    reason="No target column configured.",
                    recommended_agent="reporting_agent",
                ),
            )

        actions: list[AgentAction] = []
        findings: list[AgentFinding] = []
        recommendations: list[str] = []
        artifacts: dict[str, Any] = {}

        y = df[target_col]
        X = df.drop(columns=[target_col])

        # 1. Infer Task Type
        configured_task = state.get("model_task", "auto")
        task_res = self.task_tool.execute(InferMLTaskInput(y=y, configured_task=configured_task))
        actions.append(
            AgentAction(
                tool_name=self.task_tool.metadata.name,
                action_type="task_inference",
                status="ok" if task_res.is_success else "error",
                duration_ms=task_res.duration_ms,
                summary=f"Inferred task: '{task_res.data.task if task_res.data else 'unknown'}'.",
            )
        )

        task = task_res.data.task if task_res.is_success and task_res.data else "classification"
        artifacts["task"] = task

        # 2. Benchmark Model Zoo
        cv_folds = state.get("cv_folds", 3)
        bench_res = self.bench_tool.execute(
            BenchmarkModelsInput(
                X=X,
                y=y,
                task=task,
                cv=cv_folds,
            )
        )
        actions.append(
            AgentAction(
                tool_name=self.bench_tool.metadata.name,
                action_type="model_benchmarking",
                status="ok" if bench_res.is_success else "error",
                duration_ms=bench_res.duration_ms,
                summary=f"Benchmarked candidate zoo; selected '{bench_res.data.champion_model_name if bench_res.data else 'none'}' as champion.",
            )
        )

        if not bench_res.is_success or bench_res.data is None:
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective="Benchmark models and select champion",
                actions_taken=actions,
                errors=[bench_res.error or "Model benchmarking failed"],
            )

        champion_data = bench_res.data
        champion = champion_data.champion_estimator

        # 3. Train Champion & Produce Validation Predictions
        test_size = state.get("test_size", 0.2)
        X_train, X_test, y_train, y_test = champion.train(X, y, test_size=test_size)
        y_pred = champion.predict(X_test)

        proba = None
        if task == "classification":
            try:
                proba = champion.predict_proba(X_test)
            except Exception:
                proba = None

        artifacts["leaderboard"] = champion_data.leaderboard
        artifacts["champion_model_name"] = champion_data.champion_model_name
        artifacts["champion_score"] = champion_data.champion_score
        artifacts["champion_metric"] = champion_data.champion_metric
        artifacts["model_results"] = {
            "champion_model_name": champion_data.champion_model_name,
            "champion_score": champion_data.champion_score,
            "champion_metric": champion_data.champion_metric,
            "leaderboard": champion_data.leaderboard,
        }
        artifacts["champion_estimator"] = champion
        artifacts["y_test"] = list(y_test)
        artifacts["y_pred"] = list(y_pred)
        artifacts["y_proba"] = proba.tolist() if proba is not None else None
        artifacts["X_test"] = X_test

        findings.append(
            AgentFinding(
                category="Model Zoo Benchmark",
                fact=f"Evaluated multiple algorithms. '{champion_data.champion_model_name}' won with CV {champion_data.champion_metric} = {champion_data.champion_score:.4f}.",
                evidence=f"Leaderboard summary: {champion_data.leaderboard[:3]}",
                interpretation="The champion algorithm demonstrated the strongest cross-validation generalization.",
                recommendation="Proceed with granular holdout validation, confusion matrix analysis, and explainability diagnostics.",
                confidence=0.95,
            )
        )

        next_decision = AgentDecision(
            decision="TRIGGER_EVALUATION",
            reason="Champion model trained; ready for diagnostics and business impact analysis.",
            recommended_agent="evaluation_agent",
            priority="HIGH",
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            objective="Benchmark predictive models and select champion estimator",
            actions_taken=actions,
            tools_used=[a.tool_name for a in actions],
            findings=findings,
            recommendations=recommendations,
            artifacts=artifacts,
            confidence=0.96,
            next_action=next_decision,
        )
