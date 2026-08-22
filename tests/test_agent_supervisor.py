"""Supervisor intelligence tests (M3): retries, escalation, fail-fast, HITL.

Chaos requirement from docs/multiagent_completion_plan.md: kill-a-node
failure injection must degrade gracefully; autonomous and approval modes
must both complete.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

from autoanalyst.agents import nodes as agent_nodes
from autoanalyst.agents.graph import AutoAnalystConfig, build_graph, run_agent_pipeline
from autoanalyst.agents.serde import PickleSerde
from autoanalyst.agents.state import APPROVAL_STEPS, create_initial_state
from autoanalyst.agents.supervisor import SupervisedRun

EXAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "sample" / "example.csv"


@pytest.fixture(scope="module")
def example_csv() -> str:
    if not EXAMPLE_CSV.exists():
        pytest.skip("data/sample/example.csv not present")
    return str(EXAMPLE_CSV)


@pytest.fixture()
def loaded_df() -> pd.DataFrame:
    return pd.read_csv(EXAMPLE_CSV)


def _flaky_tool(side_effect: list[Any]) -> MagicMock:
    tool = MagicMock()
    tool.invoke.side_effect = side_effect
    return tool


class TestRetryAndEscalation:
    def test_transient_failure_is_retried(self, monkeypatch: pytest.MonkeyPatch, loaded_df: pd.DataFrame) -> None:
        flaky = _flaky_tool([RuntimeError("transient"), loaded_df])
        monkeypatch.setattr(agent_nodes, "load_dataset_tool", flaky)
        config = AutoAnalystConfig(dataset_path="flaky.csv", max_retries=2, retry_backoff_seconds=0.0)

        result = run_agent_pipeline(config)

        assert flaky.invoke.call_count == 2
        assert result.raw_df.shape == loaded_df.shape

    def test_exhausted_retries_escalate_and_degrade(
        self, monkeypatch: pytest.MonkeyPatch, example_csv: str
    ) -> None:
        failing = _flaky_tool(RuntimeError("boom"))
        failing.invoke.side_effect = RuntimeError("boom")
        monkeypatch.setattr(agent_nodes, "load_dataset_tool", failing)
        config = AutoAnalystConfig(
            dataset_path=example_csv,
            target_column="loan_status",
            max_retries=1,
            retry_backoff_seconds=0.0,
        )

        final_state = build_graph().invoke(create_initial_state(config))

        assert failing.invoke.call_count == 2
        assert any("intake" in error for error in final_state["errors"])
        assert any("escalated" in entry for entry in final_state["escalations"])
        statuses = {entry.node: entry.status for entry in final_state["trace"]}
        assert statuses["intake"] == "error"
        assert statuses.get("profiling") == "skipped"

    def test_trace_records_attempt_counts(self, monkeypatch: pytest.MonkeyPatch, loaded_df: pd.DataFrame) -> None:
        flaky = _flaky_tool([RuntimeError("a"), RuntimeError("b"), loaded_df])
        monkeypatch.setattr(agent_nodes, "load_dataset_tool", flaky)
        config = AutoAnalystConfig(dataset_path="flaky.csv", max_retries=3, retry_backoff_seconds=0.0)

        final_state = build_graph().invoke(create_initial_state(config))
        intake_run = next(entry for entry in final_state["trace"] if entry.node == "intake")

        assert intake_run.attempts == 3
        assert intake_run.status == "ok"


class TestFailFast:
    def test_fail_fast_stops_after_first_error(self, monkeypatch: pytest.MonkeyPatch, example_csv: str) -> None:
        failing = MagicMock()
        failing.invoke.side_effect = RuntimeError("fatal")
        monkeypatch.setattr(agent_nodes, "load_dataset_tool", failing)
        config = AutoAnalystConfig(dataset_path=example_csv, fail_fast=True)

        final_state = build_graph().invoke(create_initial_state(config))

        executed_nodes = [entry.node for entry in final_state["trace"]]
        assert executed_nodes == ["intake"]
        assert final_state["errors"]

    def test_without_fail_fast_flow_continues_degraded(
        self, monkeypatch: pytest.MonkeyPatch, example_csv: str
    ) -> None:
        failing = MagicMock()
        failing.invoke.side_effect = RuntimeError("non-fatal")
        monkeypatch.setattr(agent_nodes, "load_dataset_tool", failing)
        config = AutoAnalystConfig(dataset_path=example_csv, fail_fast=False)

        result = run_agent_pipeline(config)

        assert result.profile == {}
        assert result.insights == []


class TestHumanInTheLoop:
    def test_approve_both_steps_completes_with_model(self, example_csv: str) -> None:
        config = AutoAnalystConfig(
            dataset_path=example_csv,
            target_column="loan_status",
            require_approval=True,
        )
        run = SupervisedRun(config)
        run.start()

        assert run.pending_approval() == "cleaning"
        run.approve(run.pending_approval())
        run.resume()

        assert run.pending_approval() == "modeling"
        run.approve(run.pending_approval())
        run.resume()

        assert run.pending_approval() is None
        result = run.final_result()
        assert result.model_results is not None
        statuses = {}
        # trace lives in the graph state; recover it through the session state
        trace = run._state["trace"]  # noqa: SLF001 - test inspects checkpointed state
        statuses = {entry.node: entry.status for entry in trace}
        assert statuses["cleaning"] == "ok"
        assert statuses["modeling"] == "ok"

    def test_declined_cleaning_cascades_and_completes(self, example_csv: str) -> None:
        config = AutoAnalystConfig(
            dataset_path=example_csv,
            target_column="loan_status",
            require_approval=True,
        )
        run = SupervisedRun(config)
        run.start()
        run.approve(run.pending_approval(), approved=False)
        run.resume()

        # Declining cleaning leaves no cleaned data, so the supervisor
        # routes around modeling entirely and the run completes.
        assert run.pending_approval() is None

        result = run.final_result()
        assert result.model_results is None
        trace = run._state["trace"]  # noqa: SLF001 - test inspects checkpointed state
        statuses = {entry.node: entry.status for entry in trace}
        assert statuses["cleaning"] == "skipped"
        assert "modeling" not in statuses

    def test_unknown_step_rejected(self, example_csv: str) -> None:
        run = SupervisedRun(AutoAnalystConfig(dataset_path=example_csv, require_approval=True))
        with pytest.raises(ValueError, match="Unknown supervised step"):
            run.approve("report")

    def test_autonomous_mode_never_pauses(self, example_csv: str) -> None:
        run = SupervisedRun(AutoAnalystConfig(dataset_path=example_csv, require_approval=False))
        run.start()
        assert run.pending_approval() is None


class TestApprovalConstants:
    def test_approval_steps_match_documented_gates(self) -> None:
        assert APPROVAL_STEPS == frozenset({"cleaning", "modeling"})


class TestPickleSerde:
    def test_dataframe_roundtrip(self) -> None:
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        serde = PickleSerde()
        kind, blob = serde.dumps_typed({"df": df, "errors": []})
        restored = serde.loads_typed((kind, blob))
        pd.testing.assert_frame_equal(restored["df"], df)
