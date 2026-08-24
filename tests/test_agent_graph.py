"""Golden-path and resilience tests for the agent graph (M2).

Acceptance criteria from docs/multiagent_completion_plan.md:
- Full dry-run on data/sample/example.csv passes with and without a target.
- Errors never crash the graph; they accumulate into state["errors"].
- A trace record exists for every executed node.
- The graph emits the stable PipelineResult contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from autoanalyst.agents.graph import GRAPH_NODES, AutoAnalystConfig, build_graph, run_agent_pipeline
from autoanalyst.agents.state import create_initial_state

EXAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "sample" / "example.csv"


@pytest.fixture(scope="module")
def example_csv() -> str:
    if not EXAMPLE_CSV.exists():
        pytest.skip("data/sample/example.csv not present")
    return str(EXAMPLE_CSV)


class TestGoldenPath:
    def test_full_run_with_target(self, example_csv: str, tmp_path: Path) -> None:
        config = AutoAnalystConfig(
            dataset_path=example_csv,
            target_column="loan_status",
            report_path=str(tmp_path / "agent_report.md"),
        )
        result = run_agent_pipeline(config)

        assert result.raw_df.shape == (29, 12)
        assert result.cleaned_df.isna().sum().sum() == 0
        assert result.model_results is not None
        assert result.model_results["task"] == "classification"
        assert result.model_results["model_name"] == "RandomForestClassifier"
        assert result.evaluation_results is not None
        assert "accuracy" in result.evaluation_results
        assert result.insights
        assert result.report_path is not None and result.report_path.exists()

    def test_full_run_without_target(self, example_csv: str) -> None:
        result = run_agent_pipeline(AutoAnalystConfig(dataset_path=example_csv))

        assert result.model_results is None
        assert result.evaluation_results is None
        assert result.insights
        assert "numeric_summary" in result.eda_results

    def test_trace_covers_every_executed_node_with_target(self, example_csv: str, tmp_path: Path) -> None:
        config = AutoAnalystConfig(
            dataset_path=example_csv,
            target_column="loan_status",
            report_path=str(tmp_path / "trace_report.md"),
        )
        final_state = build_graph().invoke(create_initial_state(config))
        trace = final_state["trace"]
        executed = {entry.node for entry in trace}
        assert executed == set(GRAPH_NODES)
        assert all(entry.status in {"ok", "skipped"} for entry in trace)
        assert all(entry.duration_ms >= 0 for entry in trace)

    def test_trace_routes_around_modeling_without_target(self, example_csv: str) -> None:
        final_state = build_graph().invoke(create_initial_state(AutoAnalystConfig(dataset_path=example_csv)))
        statuses = {entry.node: entry.status for entry in final_state["trace"]}
        assert "modeling" not in statuses
        assert "evaluation" not in statuses
        assert statuses["intake"] == "ok"
        assert statuses["insights"] == "ok"


class TestResilience:
    def test_missing_file_never_crashes_graph(self) -> None:
        config = AutoAnalystConfig(dataset_path="does_not_exist.csv", target_column="y")
        result = run_agent_pipeline(config)

        assert result.profile == {}
        assert any("intake" in error for error in _last_errors(config))
        skipped = [node for node in ("profiling", "cleaning") if node in _last_statuses(config)]
        assert skipped

    def test_empty_dataset_recorded_as_error(self, tmp_path: Path) -> None:
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("a,b\n", encoding="utf-8")
        result = run_agent_pipeline(AutoAnalystConfig(dataset_path=str(empty_csv)))

        assert result.raw_df.empty


class TestInitialState:
    def test_create_initial_state_seeds_accumulators(self) -> None:
        state = create_initial_state(AutoAnalystConfig())
        assert state["errors"] == []
        assert state["warnings"] == []
        assert state["trace"] == []
        assert state["missing_strategy"] == "median"


def _config_with_target(example_csv: str) -> AutoAnalystConfig:
    return AutoAnalystConfig(dataset_path=example_csv, target_column="loan_status")


def _last_errors(config: AutoAnalystConfig) -> list[str]:
    final_state = build_graph().invoke(create_initial_state(config))
    return list(final_state["errors"])


def _last_statuses(config: AutoAnalystConfig) -> dict[str, str]:
    final_state = build_graph().invoke(create_initial_state(config))
    return {entry.node: entry.status for entry in final_state["trace"]}
