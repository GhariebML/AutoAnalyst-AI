"""LangGraph assembly for the AutoAnalyst multiagent workflow.

Builds the documented fixed graph (Stage 1 autonomy):

    intake → profiling → eda → cleaning → features
        ├─ target available → modeling → evaluation ─┐
        └──────────────────────────────────────────→ insights → report → END

The supervisor gains routing/retry intelligence in M3; today it is the
error-containment wrapper on every node.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import cast

import pandas as pd
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from autoanalyst.agents.nodes import (
    cleaning_node,
    dataset_intake_node,
    eda_node,
    evaluation_node,
    feature_node,
    insight_node,
    modeling_node,
    profiling_node,
    report_node,
)
from autoanalyst.agents.state import AutoAnalystConfig, AutoAnalystState, create_initial_state
from autoanalyst.pipeline import PipelineResult

logger = logging.getLogger(__name__)

GRAPH_NODES = (
    "intake",
    "profiling",
    "eda",
    "cleaning",
    "features",
    "modeling",
    "evaluation",
    "insights",
    "report",
)


def build_graph() -> CompiledStateGraph:
    """Compile the fixed AutoAnalyst agent graph."""
    builder = StateGraph(AutoAnalystState)

    builder.add_node("intake", dataset_intake_node)
    builder.add_node("profiling", profiling_node)
    builder.add_node("eda", eda_node)
    builder.add_node("cleaning", cleaning_node)
    builder.add_node("features", feature_node)
    builder.add_node("modeling", modeling_node)
    builder.add_node("evaluation", evaluation_node)
    builder.add_node("insights", insight_node)
    builder.add_node("report", report_node)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "profiling")
    builder.add_edge("profiling", "eda")
    builder.add_edge("eda", "cleaning")
    builder.add_edge("cleaning", "features")
    builder.add_conditional_edges(
        "features",
        _route_after_features,
        {"modeling": "modeling", "insights": "insights"},
    )
    builder.add_edge("modeling", "evaluation")
    builder.add_edge("evaluation", "insights")
    builder.add_edge("insights", "report")
    builder.add_edge("report", END)
    return builder.compile()


def run_agent_pipeline(config: AutoAnalystConfig) -> PipelineResult:
    """Run the agent graph and return the stable PipelineResult contract."""
    graph = build_graph()
    final_state = cast(AutoAnalystState, graph.invoke(create_initial_state(config)))

    errors = final_state.get("errors") or []
    if errors:
        logger.warning("Agent pipeline completed with %d error(s): %s", len(errors), errors)

    return _to_pipeline_result(final_state)


def _route_after_features(state: AutoAnalystState) -> str:
    target = state.get("target_column")
    model_ready = state.get("model_ready_df")
    if target and model_ready is not None and target in model_ready.columns:
        return "modeling"
    return "insights"


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
        model_results=state.get("model_results"),
        evaluation_results=state.get("evaluation_results"),
        report_path=Path(report_path) if report_path else None,
        warnings=list(state.get("warnings") or []),
    )


__all__ = [
    "GRAPH_NODES",
    "AutoAnalystConfig",
    "build_graph",
    "run_agent_pipeline",
]
