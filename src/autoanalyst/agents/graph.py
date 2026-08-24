"""LangGraph assembly for the AutoAnalyst multiagent workflow.

Builds the documented graph with M3 supervisor intelligence:

    intake → profiling → eda → cleaning → features
        ├─ target available → modeling → evaluation ─┐
        └──────────────────────────────────────────→ insights → report → END

Every edge is supervised: when ``fail_fast`` is enabled and any node has
recorded an error, the supervisor routes to END instead of continuing.
With ``require_approval`` the graph compiles with checkpoints and pauses
before the cleaning/modeling steps (see ``agents/supervisor.py``).
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import pandas as pd
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from autoanalyst.agents.nodes import (
    cleaning_node,
    dataset_intake_node,
    drift_node,
    eda_node,
    evaluation_node,
    feature_node,
    insight_node,
    memory_node,
    modeling_node,
    profiling_node,
    report_node,
)
from autoanalyst.agents.plugins import plugins_for_anchor
from autoanalyst.agents.state import AutoAnalystConfig, AutoAnalystState, create_initial_state
from autoanalyst.pipeline import PipelineResult

logger = logging.getLogger(__name__)

GRAPH_NODES = (
    "intake",
    "profiling",
    "drift",
    "eda",
    "cleaning",
    "features",
    "modeling",
    "evaluation",
    "insights",
    "report",
    "memory",
)


def should_abort(state: AutoAnalystState) -> bool:
    """True when fail-fast mode is on and at least one node failed."""
    return bool(state.get("fail_fast")) and bool(state.get("errors"))


def route_after_features(state: AutoAnalystState) -> str:
    """Supervisor routing decision coming out of the feature node."""
    if should_abort(state):
        return END
    target = state.get("target_column")
    model_ready = state.get("model_ready_df")
    if target and model_ready is not None and target in model_ready.columns:
        return "modeling"
    return "insights"


def build_graph(
    checkpointer: Any | None = None,
    interrupt_before: Sequence[str] | None = None,
) -> CompiledStateGraph:
    """Compile the supervised AutoAnalyst agent graph.

    Parameters
    ----------
    checkpointer:
        Optional LangGraph checkpointer enabling resumable HITL runs.
    interrupt_before:
        Node names to pause before (used with ``require_approval``).
    """
    builder = StateGraph(AutoAnalystState)

    builder.add_node("intake", dataset_intake_node)
    builder.add_node("profiling", profiling_node)
    builder.add_node("drift", drift_node)
    builder.add_node("eda", eda_node)
    builder.add_node("cleaning", cleaning_node)
    builder.add_node("features", feature_node)
    builder.add_node("modeling", modeling_node)
    builder.add_node("evaluation", evaluation_node)
    builder.add_node("insights", insight_node)
    builder.add_node("report", report_node)
    builder.add_node("memory", memory_node)

    builder.add_edge(START, "intake")
    _supervised_edge(builder, "intake", "profiling")
    _supervised_edge(builder, "profiling", "drift")
    _supervised_edge(builder, "drift", "eda")
    _supervised_edge(builder, "eda", "cleaning")
    _supervised_edge(builder, "cleaning", "features")
    builder.add_conditional_edges(
        "features",
        route_after_features,
        {"modeling": "modeling", "insights": "insights", END: END},
    )
    _supervised_edge(builder, "modeling", "evaluation")
    _supervised_edge(builder, "evaluation", "insights")

    if not _splice_plugins(builder, "insights", "report"):
        _supervised_edge(builder, "insights", "report")
    builder.add_edge("report", "memory")
    builder.add_edge("memory", END)
    interrupts = list(interrupt_before) if interrupt_before else None
    return builder.compile(checkpointer=checkpointer, interrupt_before=interrupts)


def _splice_plugins(builder: StateGraph, anchor: str, successor: str) -> bool:
    """Wire anchor→[plugin1→…→pluginN]→successor for registered plugins.

    Returns True when plugins were spliced and the caller must skip the
    direct anchor→successor edge. Registration order defines chain order.
    """
    specs = plugins_for_anchor(anchor)
    if not specs:
        return False

    names = [spec.name for spec in specs]
    clashes = sorted(set(names) & set(GRAPH_NODES))
    if clashes:
        raise ValueError(f"Plugin names may not shadow built-in nodes: {clashes}")

    for spec in specs:
        builder.add_node(spec.name, spec.function)
    builder.add_edge(anchor, names[0])
    for current, following in zip(names, names[1:]):
        builder.add_edge(current, following)
    builder.add_edge(names[-1], successor)
    logger.info("Spliced %d plugin(s) after '%s': %s", len(specs), anchor, names)
    return True


def run_agent_pipeline(config: AutoAnalystConfig) -> PipelineResult:
    """Run the agent graph and return the stable PipelineResult contract."""
    graph = build_graph()
    final_state = cast(AutoAnalystState, graph.invoke(create_initial_state(config)))

    errors = final_state.get("errors") or []
    if errors:
        logger.warning("Agent pipeline completed with %d error(s): %s", len(errors), errors)

    return _to_pipeline_result(final_state)


def _supervised_edge(builder: StateGraph, src: str, dst: str) -> None:
    """Add src→dst with a fail-fast gate that routes to END on abort."""

    def gate(state: AutoAnalystState) -> str:
        return dst if not should_abort(state) else END

    builder.add_conditional_edges(src, gate, {dst: dst, END: END})


def _to_pipeline_result(state: AutoAnalystState) -> PipelineResult:
    """Map the final graph state onto the public PipelineResult contract."""
    raw = state.get("df")
    raw_df = raw if raw is not None else pd.DataFrame()
    cleaned = state.get("cleaned_df")
    cleaned_df = cleaned if cleaned is not None else raw_df.copy()
    model_ready = state.get("model_ready_df")
    model_ready_df = model_ready if model_ready is not None else cleaned_df.copy()
    missing_report = state.get("missing_values_report")
    report_path = state.get("report_path")

    return PipelineResult(
        raw_df=raw_df,
        cleaned_df=cleaned_df,
        model_ready_df=model_ready_df,
        profile=state.get("profile") or {},
        missing_values_report=missing_report if missing_report is not None else pd.DataFrame(),
        eda_results=state.get("eda_results") or {},
        insights=list(state.get("insights") or []),
        narrated_by=str(state.get("narrated_by") or "rules"),
        executive_summary=state.get("executive_summary"),
        model_results=state.get("model_results"),
        evaluation_results=state.get("evaluation_results"),
        report_path=Path(report_path) if report_path else None,
        warnings=list(state.get("warnings") or []),
    )


__all__ = [
    "GRAPH_NODES",
    "AutoAnalystConfig",
    "build_graph",
    "route_after_features",
    "run_agent_pipeline",
    "should_abort",
]
