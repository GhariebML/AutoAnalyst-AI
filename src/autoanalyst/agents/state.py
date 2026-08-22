"""Shared LangGraph state for the AutoAnalyst agent workflow.

The state is a ``TypedDict`` with ``operator.add`` reducers on the
accumulating list fields (errors, warnings, trace) so each node can return
partial updates that LangGraph merges. Trace entries are validated
``NodeRun`` pydantic models.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

import pandas as pd
from pydantic import BaseModel, ConfigDict


class NodeRun(BaseModel):
    """Trace record for a single executed graph node."""

    model_config = ConfigDict(frozen=True)

    node: str
    status: str = "ok"
    duration_ms: float = 0.0
    error: str | None = None


class AutoAnalystConfig(BaseModel):
    """Validated configuration for one agent workflow run."""

    dataset_path: str | None = None
    target_column: str | None = None
    missing_strategy: str = "median"
    encode_categoricals: bool = True
    report_path: str | None = None


class AutoAnalystState(TypedDict, total=False):
    """Graph state flowing through every agent node.

    Fields with ``Annotated[..., operator.add]`` accumulate across nodes;
    all other fields are overwritten by whichever node produces them.
    """

    # configuration
    dataset_path: str | None
    target_column: str | None
    missing_strategy: str
    encode_categoricals: bool
    report_path: str | None

    # data frames
    df: pd.DataFrame | None
    cleaned_df: pd.DataFrame | None
    model_ready_df: pd.DataFrame | None

    # analysis artifacts
    profile: dict[str, Any] | None
    missing_values_report: pd.DataFrame | None
    eda_results: dict[str, Any]
    cleaning_log: list[str]
    feature_columns: list[str]
    y_test: list[Any] | None
    y_pred: list[Any] | None
    model_results: dict[str, Any] | None
    evaluation_results: dict[str, Any] | None
    insights: list[str]

    # observability (accumulating)
    warnings: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
    trace: Annotated[list[NodeRun], operator.add]


def create_initial_state(config: AutoAnalystConfig) -> AutoAnalystState:
    """Build the starting state for a graph invocation from a config."""
    return AutoAnalystState(
        dataset_path=config.dataset_path,
        target_column=config.target_column,
        missing_strategy=config.missing_strategy,
        encode_categoricals=config.encode_categoricals,
        report_path=config.report_path,
        df=None,
        cleaned_df=None,
        model_ready_df=None,
        profile=None,
        missing_values_report=None,
        eda_results={},
        cleaning_log=[],
        feature_columns=[],
        y_test=None,
        y_pred=None,
        model_results=None,
        evaluation_results=None,
        insights=[],
        warnings=[],
        errors=[],
        trace=[],
    )
