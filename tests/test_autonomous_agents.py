"""Unit tests for the specialized autonomous agents."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from autoanalyst.agents.eda_agent import EDAAgent
from autoanalyst.agents.evaluation_agent import EvaluationAgent
from autoanalyst.agents.ml_agent import MachineLearningAgent
from autoanalyst.agents.orchestrator import MasterOrchestrator
from autoanalyst.agents.preprocessing_agent import PreprocessingAgent
from autoanalyst.agents.profiling_agent import DataProfilingAgent
from autoanalyst.agents.reporting_agent import ReportingAgent


@pytest.fixture
def sample_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [20, 25, 30, 35, 40, 45, 50, 55, 60, 65],
            "income": [30000.0, 40000.0, 50000.0, None, 70000.0, 80000.0, 90000.0, 100000.0, 110000.0, 450000.0],
            "credit_score": [600, 650, 700, 720, 750, 620, 680, 710, 790, 800],
            "default": [0, 0, 0, 0, 0, 1, 1, 0, 1, 1],
        }
    )


class TestAutonomousAgents:
    def test_profiling_agent_execution(self, sample_dataset: pd.DataFrame) -> None:
        agent = DataProfilingAgent()
        result = agent.run({"raw_df": sample_dataset})
        assert result.is_success
        assert len(result.findings) >= 2
        assert result.artifacts["health_score"] > 0
        assert result.next_action is not None

    def test_eda_agent_execution(self, sample_dataset: pd.DataFrame) -> None:
        agent = EDAAgent()
        result = agent.run({"raw_df": sample_dataset, "target_column": "default"})
        assert result.is_success
        assert len(result.findings) > 0
        assert "correlation_matrix" in result.artifacts
        assert "distributions" in result.artifacts

    def test_preprocessing_agent_execution(self, sample_dataset: pd.DataFrame) -> None:
        agent = PreprocessingAgent()
        result = agent.run({"raw_df": sample_dataset, "target_column": "default", "require_approval": False})
        assert result.is_success
        assert result.artifacts["cleaned_df"] is not None
        assert result.artifacts["cleaned_df"].isna().sum().sum() == 0

    def test_ml_agent_execution(self, sample_dataset: pd.DataFrame) -> None:
        prep = PreprocessingAgent().run({"raw_df": sample_dataset, "target_column": "default"})
        ml_agent = MachineLearningAgent()
        result = ml_agent.run(
            {
                "model_ready_df": prep.artifacts["model_ready_df"],
                "target_column": "default",
                "cv_folds": 2,
            }
        )
        assert result.is_success
        assert result.artifacts["champion_model_name"] != ""
        assert len(result.artifacts["leaderboard"]) >= 2

    def test_evaluation_agent_execution(self) -> None:
        eval_agent = EvaluationAgent()
        result = eval_agent.run(
            {
                "y_test": [0, 1, 0, 1],
                "y_pred": [0, 1, 0, 0],
                "task": "classification",
            }
        )
        assert result.is_success
        assert "accuracy" in result.artifacts["scalar_metrics"]

    def test_reporting_agent_execution(self, sample_dataset: pd.DataFrame, tmp_path: Path) -> None:
        report_file = tmp_path / "agent_report.html"
        rep_agent = ReportingAgent()
        result = rep_agent.run(
            {
                "raw_df": sample_dataset,
                "profile": {"rows": 10, "columns": 4, "health_score": 95.0},
                "insights": ["High quality data analyzed."],
                "report_path": str(report_file),
            }
        )
        assert result.is_success
        assert report_file.exists()


class TestMasterOrchestrator:
    def test_end_to_end_orchestrator_run(self, sample_dataset: pd.DataFrame) -> None:
        events = []
        orchestrator = MasterOrchestrator(event_callback=lambda e: events.append(e.event_type))

        res = orchestrator.run_analysis(
            dataset=sample_dataset,
            target_column="default",
            model_task="classification",
        )

        assert res["status"] == "completed"
        assert len(res["agent_history"]) >= 4
        assert "RUN_STARTED" in events
        assert "RUN_COMPLETED" in events
        assert res["profile"] is not None
        assert res["evaluation_results"] is not None
