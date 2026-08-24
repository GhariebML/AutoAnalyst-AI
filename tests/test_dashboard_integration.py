"""Dashboard integration tests (M6): run console, trace viewer, chat panel.

Contract under test:
- ``SupervisedRun.trace()`` / ``finished`` expose live progress for the UI
  in both autonomous and HITL (checkpointed) modes.
- ``qa.answer_question`` answers from a completed run's facts with zero
  model calls by default; an injected chat model upgrades the answer and
  any failure degrades to the deterministic fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from autoanalyst.agents.graph import AutoAnalystConfig, run_agent_pipeline
from autoanalyst.agents.qa import Answer, answer_question, build_facts
from autoanalyst.agents.supervisor import SupervisedRun
from autoanalyst.pipeline import PipelineResult

EXAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "sample" / "example.csv"


@pytest.fixture(scope="module")
def example_csv() -> str:
    if not EXAMPLE_CSV.exists():
        pytest.skip("data/sample/example.csv not present")
    return str(EXAMPLE_CSV)


@pytest.fixture()
def sample_result() -> PipelineResult:
    df = pd.DataFrame({"age": [20, 30, None], "income": [1000, 2000, 3000]})
    return PipelineResult(
        raw_df=df,
        cleaned_df=df.copy(),
        model_ready_df=df.copy(),
        profile={"rows": 3, "columns": 2},
        missing_values_report=pd.DataFrame(),
        insights=["Income rises with age.", "One row has missing age."],
        model_results={"task": "classification", "model_name": "RandomForestClassifier"},
        evaluation_results={"accuracy": 0.8123, "f1_macro": 0.7654},
        warnings=["Encoding skipped for column 'x'"],
    )


def fake_llm(responses: list[str]) -> FakeMessagesListChatModel:
    return FakeMessagesListChatModel(responses=[AIMessage(content=text) for text in responses])


class TestSupervisedRunProgress:
    def test_autonomous_run_reports_trace_and_finish(self, example_csv: str, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AUTOANALYST_LLM_ENABLED", raising=False)
        run = SupervisedRun(AutoAnalystConfig(dataset_path=example_csv, target_column="loan_status"))

        assert run.finished is False
        assert run.trace() == []

        run.start()

        assert run.finished is True
        nodes = [entry.node for entry in run.trace()]
        assert nodes[0] == "intake"
        assert "report" in nodes
        assert nodes[-1] == "memory"
        statuses = {entry.node: entry.status for entry in run.trace()}
        assert statuses["intake"] == "ok"
        assert all(status == "ok" for node, status in statuses.items() if node not in {"report", "drift", "memory"})

    def test_hitl_run_not_finished_while_paused(self, example_csv: str) -> None:
        config = AutoAnalystConfig(dataset_path=example_csv, target_column="loan_status", require_approval=True)
        run = SupervisedRun(config)
        run.start()

        assert run.pending_approval() == "cleaning"
        assert run.finished is False
        executed = [entry.node for entry in run.trace()]
        assert executed == ["intake", "profiling", "drift", "eda"]

    def test_unstarted_run_is_never_finished(self, example_csv: str) -> None:
        run = SupervisedRun(AutoAnalystConfig(dataset_path=example_csv))
        assert run.finished is False
        assert run.trace() == []


class TestBuildFacts:
    def test_facts_condense_result(self, sample_result: PipelineResult) -> None:
        facts = build_facts(sample_result)

        assert facts["rows"] == 3
        assert facts["columns"] == 2
        assert facts["missing_values"] == 1
        assert facts["column_names"] == ["age", "income"]
        assert facts["model"]["model_name"] == "RandomForestClassifier"
        assert facts["metrics"]["accuracy"] == pytest.approx(0.8123)
        assert facts["insights"][0] == "Income rises with age."
        assert facts["warnings"] == ["Encoding skipped for column 'x'"]

    def test_facts_omit_absent_sections(self) -> None:
        df = pd.DataFrame({"a": [1]})
        bare = PipelineResult(
            raw_df=df,
            cleaned_df=df.copy(),
            model_ready_df=df.copy(),
            profile={},
            missing_values_report=pd.DataFrame(),
        )
        facts = build_facts(bare)

        assert "model" not in facts
        assert "metrics" not in facts
        assert "insights" not in facts
        assert "warnings" not in facts


class TestAnswerQuestion:
    def test_metric_question_answered_from_rules(self, sample_result: PipelineResult) -> None:
        answer = answer_question(sample_result, "What accuracy did we get?", llm=None)

        assert answer.source == "rules"
        assert "accuracy=0.812" in answer.text
        assert "RandomForestClassifier" in answer.text

    def test_shape_and_missing_questions(self, sample_result: PipelineResult) -> None:
        shape = answer_question(sample_result, "How many rows are there?")
        missing = answer_question(sample_result, "Any missing values?")

        assert "3 rows" in shape.text
        assert "1 missing value" in missing.text

    def test_model_question_without_target(self) -> None:
        df = pd.DataFrame({"a": [1, 2]})
        bare = PipelineResult(
            raw_df=df,
            cleaned_df=df.copy(),
            model_ready_df=df.copy(),
            profile={},
            missing_values_report=pd.DataFrame(),
        )
        answer = answer_question(bare, "Which model was trained?")

        assert "No model was trained" in answer.text

    def test_insights_question_lists_findings(self, sample_result: PipelineResult) -> None:
        answer = answer_question(sample_result, "What are the key insights?")

        assert "Income rises with age." in answer.text

    def test_unknown_question_states_limits(self, sample_result: PipelineResult) -> None:
        answer = answer_question(sample_result, "What is the meaning of life?")

        assert answer.source == "rules"
        assert "only answer from this run's facts" in answer.text

    def test_empty_question_prompts_user(self, sample_result: PipelineResult) -> None:
        answer = answer_question(sample_result, "   ")

        assert "Ask me about" in answer.text

    def test_llm_answer_used_when_available(self, sample_result: PipelineResult) -> None:
        llm = fake_llm(["The run found strong income-age correlation."])
        answer = answer_question(sample_result, "Summarize this run.", llm=llm)

        assert isinstance(answer, Answer)
        assert answer.source == "llm"
        assert "income-age" in answer.text

    def test_llm_failure_degrades_to_rules(self, sample_result: PipelineResult) -> None:
        class ExplodingModel(FakeMessagesListChatModel):
            def invoke(self, *args: Any, **kwargs: Any) -> Any:
                raise RuntimeError("api down")

        answer = answer_question(sample_result, "How many rows?", llm=ExplodingModel(responses=[]))

        assert answer.source == "rules"
        assert "3 rows" in answer.text

    def test_prompt_carries_facts_and_question(
        self, sample_result: PipelineResult, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, str] = {}

        class RecordingModel(FakeMessagesListChatModel):
            def invoke(self, input_: Any, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
                captured["prompt"] = input_ if isinstance(input_, str) else str(input_)
                return super().invoke(input_, *args, **kwargs)

        monkeypatch.setattr("autoanalyst.agents.qa._truncate", lambda text, max_chars=4000: text)
        RecordingModel(responses=[AIMessage(content="ok")])
        model = RecordingModel(responses=[AIMessage(content="ok")])
        answer_question(sample_result, "How accurate is the model?", llm=model)

        prompt = captured["prompt"]
        assert "How accurate is the model?" in prompt
        assert '"rows": 3' in prompt
        assert '"accuracy"' in prompt


class TestAgentPipelineStillDeterministic:
    def test_full_agent_run_feeds_qa(self, example_csv: str, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AUTOANALYST_LLM_ENABLED", raising=False)
        result = run_agent_pipeline(AutoAnalystConfig(dataset_path=example_csv, target_column="loan_status"))
        answer = answer_question(result, "How many rows were analyzed?")

        assert str(result.raw_df.shape[0]) in answer.text
