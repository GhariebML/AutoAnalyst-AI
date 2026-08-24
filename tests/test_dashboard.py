"""Dashboard integration tests (M6): pure helpers plus an AppTest smoke run."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

from autoanalyst.agents.state import NodeRun
from autoanalyst.dashboard.helpers import (
    MAX_UPLOAD_BYTES,
    RunContext,
    answer_question,
    build_run_context,
    save_upload_to_temp,
    scalar_metrics,
    trace_to_dataframe,
)
from autoanalyst.pipeline import PipelineResult


def make_result(**overrides: Any) -> PipelineResult:
    empty = pd.DataFrame()
    defaults: dict[str, Any] = dict(
        raw_df=pd.DataFrame({"a": [1, 2]}),
        cleaned_df=pd.DataFrame({"a": [1, 2]}),
        model_ready_df=pd.DataFrame({"a": [1, 2]}),
        profile={"rows": 2, "columns": 1, "column_names": ["a"]},
        missing_values_report=empty,
        eda_results={},
        insights=["Dataset has 2 rows."],
        model_results=None,
        evaluation_results=None,
        report_path=None,
        warnings=[],
    )
    defaults.update(overrides)
    return PipelineResult(**defaults)


class TestUploadGuard:
    def _upload(self, data: bytes) -> Any:
        upload = MagicMock()
        upload.getvalue.return_value = data
        return upload

    def test_saves_valid_upload(self) -> None:
        path = save_upload_to_temp(self._upload(b"a,b\n1,2\n"))
        assert Path(path).exists()
        assert Path(path).read_bytes() == b"a,b\n1,2\n"
        Path(path).unlink(missing_ok=True)

    def test_rejects_empty_upload(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            save_upload_to_temp(self._upload(b""))

    def test_rejects_oversized_upload(self) -> None:
        with pytest.raises(ValueError, match="upload limit"):
            save_upload_to_temp(self._upload(b"x" * (MAX_UPLOAD_BYTES + 1)))


class TestTraceTable:
    def test_columns_and_values(self) -> None:
        trace = [
            NodeRun(node="intake", status="ok", duration_ms=1.5),
            NodeRun(node="cleaning", status="skipped", duration_ms=0.0, error="awaiting human approval."),
            NodeRun(node="intake2", status="error", duration_ms=9.0, attempts=3, error="boom"),
        ]
        df = trace_to_dataframe(trace)
        assert list(df.columns) == ["node", "status", "duration_ms", "attempts", "error"]
        assert df.iloc[2]["attempts"] == 3
        assert len(df) == 3


class TestScalarMetrics:
    def test_only_numeric_scalars(self) -> None:
        metrics = scalar_metrics({"accuracy": 0.91234, "f1_macro": True, "confusion_matrix": [[1]], "report": {"a": 1}})
        assert metrics == {"accuracy": 0.9123}


class TestAnswerQuestion:
    @pytest.fixture()
    def context(self) -> RunContext:
        result = make_result(
            evaluation_results={"accuracy": 0.85, "f1_macro": 0.8, "confusion_matrix": [[1]]},
            executive_summary="Ran on tiny data.",
            model_results={"task": "classification", "model_name": "RandomForestClassifier"},
        )
        return build_run_context(result, target_column="label")

    def test_rows_question(self, context: RunContext) -> None:
        assert "2 rows" in answer_question(context, "How many rows are there?")

    def test_columns_question(self, context: RunContext) -> None:
        answer = answer_question(context, "What columns exist?")
        assert "'a'" in answer or "`a`" in answer or "a," in answer or "columns: a" in answer

    def test_target_question_with_and_without_target(self, context: RunContext) -> None:
        assert "'label'" in answer_question(context, "What is the target?")
        bare = build_run_context(make_result())
        assert "No target" in answer_question(bare, "What is the target?")

    def test_metrics_question(self, context: RunContext) -> None:
        answer = answer_question(context, "What is the accuracy?")
        assert "accuracy=0.8500" in answer

    def test_insights_question(self, context: RunContext) -> None:
        assert "Dataset has 2 rows." in answer_question(context, "Any insights?")

    def test_summary_question(self, context: RunContext) -> None:
        assert answer_question(context, "Give me a summary.") == "Ran on tiny data."

    def test_empty_and_unknown_questions(self, context: RunContext) -> None:
        assert "Ask about" in answer_question(context, "")
        assert "I can answer questions" in answer_question(context, "what is the meaning of life?")

    def test_llm_answer_preferred_when_available(self, context: RunContext) -> None:
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(content="From the model: it looks great.")
        answer = answer_question(context, "How does the model look?", llm=llm)
        assert answer.startswith("From the model:")

    def test_llm_failure_falls_back(self, context: RunContext) -> None:
        llm = MagicMock()
        llm.invoke.side_effect = RuntimeError("down")
        assert "2 rows" in answer_question(context, "How many rows?", llm=llm)


def EXAMPLE_CSV() -> str:
    from pathlib import Path

    return str(Path(__file__).resolve().parents[1] / "data" / "sample" / "example.csv")


class TestSupervisorAccessors:
    def test_finished_and_trace_before_start(self) -> None:
        from autoanalyst.agents.graph import AutoAnalystConfig
        from autoanalyst.agents.supervisor import SupervisedRun

        run = SupervisedRun(AutoAnalystConfig(dataset_path=EXAMPLE_CSV()))
        assert run.finished is False
        assert run.trace() == []

        run.start()
        assert run.finished is True
        statuses = {entry.node for entry in run.trace()}
        assert "intake" in statuses and "insights" in statuses

    def test_hitl_run_not_finished_while_paused(self) -> None:
        from autoanalyst.agents.graph import AutoAnalystConfig
        from autoanalyst.agents.supervisor import SupervisedRun

        run = SupervisedRun(AutoAnalystConfig(dataset_path=EXAMPLE_CSV(), require_approval=True))
        run.start()
        assert run.finished is False
        assert run.pending_approval() == "cleaning"


class TestStreamlitSmoke:
    """AppTest executes the script headlessly; no file uploaded → early stop."""

    def test_app_boots_without_exception(self) -> None:
        pytest.importorskip("streamlit.testing")
        from streamlit.testing.v1 import AppTest

        app_path = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"
        at = AppTest.from_file(str(app_path), default_timeout=60)
        at.run()
        assert not at.exception
        assert any("AutoAnalyst AI" in title.value for title in at.title)
