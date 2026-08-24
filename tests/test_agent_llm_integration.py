"""Integration tests validating Agent and Orchestrator integration with LLMService."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from autoanalyst.agents.base import AgentFinding
from autoanalyst.agents.orchestrator import MasterOrchestrator
from autoanalyst.agents.profiling_agent import DataProfilingAgent
from autoanalyst.agents.reporting_agent import ReportingAgent
from autoanalyst.llm.provider import MockLLMProvider
from autoanalyst.llm.service import LLMService


def test_profiling_agent_hybrid_llm_reasoning() -> None:
    df = pd.DataFrame(
        {
            "age": [25, 30, 45, 22, 58],
            "salary": [50000, 60000, 95000, 42000, 120000],
            "purchased": [0, 1, 1, 0, 1],
        }
    )

    mock_llm_output = {
        "executive_diagnosis": "Dataset features high signal with clean numerical bounds.",
        "key_risks": ["Small sample size (5 records)"],
        "recommended_target": "purchased",
        "interpretations": ["Strong potential for binary classification."],
        "recommendations": ["Execute EDA correlation inspection."],
    }
    mock_provider = MockLLMProvider(
        predefined_responses={"Evaluate data quality": json.dumps(mock_llm_output)}
    )
    llm_service = LLMService(provider=mock_provider, enabled=True)

    agent = DataProfilingAgent(llm_service=llm_service)
    result = agent.run({"df": df, "run_id": "test_run_1"})

    assert result.is_success
    assert len(result.findings) >= 2
    assert any("Small sample size" in f.fact for f in result.findings)
    assert result.next_action is not None
    assert result.next_action.decision == "TRIGGER_EDA"


def test_reporting_agent_hybrid_synthesis() -> None:
    mock_synthesis = {
        "executive_summary": "AutoAnalyst AI identified strong predictive relationships with 94.2% accuracy.",
        "key_takeaways": [
            "Salary is the dominant predictive driver",
            "Model generalizability is confirmed via holdout evaluation",
        ],
        "business_recommendations": [
            "Deploy champion model for automated customer scoring",
            "Monitor drift quarterly",
        ],
    }
    mock_provider = MockLLMProvider(
        predefined_responses={"Synthesize the multi-agent findings": json.dumps(mock_synthesis)}
    )
    llm_service = LLMService(provider=mock_provider, enabled=True)

    agent = ReportingAgent(llm_service=llm_service)
    state = {
        "run_id": "test_run_rep",
        "all_findings": [
            AgentFinding(
                category="Model Performance",
                fact="Champion algorithm achieved 94.2% accuracy.",
                evidence="Holdout size: 20",
                interpretation="Strong generalization.",
                recommendation="Deploy model.",
                confidence=0.95,
            )
        ],
        "model_results": {"champion_model_name": "RandomForestClassifier", "champion_score": 0.942},
        "evaluation_results": {"accuracy": 0.942},
    }

    result = agent.run(state)
    assert result.is_success
    assert "94.2% accuracy" in result.artifacts["executive_summary"]
    assert len(result.artifacts["insights"]) >= 2
    assert result.next_action.decision == "WORKFLOW_COMPLETE"


def test_orchestrator_end_to_end_with_mock_llm(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "feature1": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "feature2": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5],
            "target": [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        }
    )
    csv_file = tmp_path / "test_llm_ds.csv"
    df.to_csv(csv_file, index=False)

    mock_provider = MockLLMProvider()
    llm_service = LLMService(provider=mock_provider, enabled=True)

    orchestrator = MasterOrchestrator(llm_service=llm_service)
    res = orchestrator.run_analysis(
        dataset=str(csv_file),
        target_column="target",
        model_task="classification",
        run_id="run_llm_orchestrator_test",
    )

    assert res["status"] == "completed"
    assert res["executive_summary"] is not None
    assert len(res["all_findings"]) > 0
