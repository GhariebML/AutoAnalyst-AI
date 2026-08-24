"""Shared LangGraph state for the AutoAnalyst agent workflow.

The state is a ``TypedDict`` with ``operator.add`` reducers on the
accumulating list fields (errors, warnings, trace) so each node can return
partial updates that LangGraph merges. Trace entries are validated
``NodeRun`` pydantic models.
"""

from __future__ import annotations

import operator
import uuid
from typing import Annotated, Any, TypedDict

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class NodeRun(BaseModel):
    """Trace record for a single executed graph node."""

    model_config = ConfigDict(frozen=True)

    node: str
    status: str = "ok"
    duration_ms: float = 0.0
    attempts: int = 1
    error: str | None = None


class AutoAnalystConfig(BaseModel):
    """Validated configuration for one agent workflow run."""

    dataset_path: str | None = None
    target_column: str | None = None
    missing_strategy: str = "median"
    encode_categoricals: bool = True
    report_path: str | None = None

    # supervisor intelligence (M3)
    max_retries: int = Field(default=2, ge=0)
    retry_backoff_seconds: float = Field(default=0.05, ge=0)
    fail_fast: bool = False
    require_approval: bool = False

    # completeness extras (M7)
    dataset_name: str | None = None
    enable_memory: bool = False
    enable_drift: bool = False
    memory_path: str | None = None


APPROVAL_STEPS = frozenset({"cleaning", "modeling"})
"""Graph nodes that support human-in-the-loop approval gates."""


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

    # supervisor settings (seeded from config, read by nodes/edges)
    max_retries: int
    retry_backoff_seconds: float
    fail_fast: bool
    require_approval: bool
    approvals: dict[str, bool]

    # completeness extras (M7)
    run_id: str
    dataset_name: str | None
    enable_memory: bool
    enable_drift: bool
    memory_path: str | None
    drift_report: dict[str, Any] | None
    run_record_id: str | None

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
    y_proba: list[list[float]] | None
    label_classes: list[Any] | None
    model_results: dict[str, Any] | None
    evaluation_results: dict[str, Any] | None
    insights: list[str]
    narrated_by: str
    executive_summary: str | None

    # observability (accumulating)
    warnings: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
    trace: Annotated[list[NodeRun], operator.add]
    escalations: Annotated[list[str], operator.add]


def create_initial_state(config: AutoAnalystConfig) -> AutoAnalystState:
    """Build the starting state for a graph invocation from a config."""
    return AutoAnalystState(
        run_id=uuid.uuid4().hex,
        dataset_path=config.dataset_path,
        target_column=config.target_column,
        missing_strategy=config.missing_strategy,
        encode_categoricals=config.encode_categoricals,
        report_path=config.report_path,
        dataset_name=config.dataset_name,
        enable_memory=config.enable_memory,
        enable_drift=config.enable_drift,
        memory_path=config.memory_path,
        drift_report=None,
        run_record_id=None,
        max_retries=config.max_retries,
        retry_backoff_seconds=config.retry_backoff_seconds,
        fail_fast=config.fail_fast,
        require_approval=config.require_approval,
        approvals={},
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
        y_proba=None,
        label_classes=None,
        model_results=None,
        evaluation_results=None,
        insights=[],
        narrated_by="rules",
        executive_summary=None,
        warnings=[],
        errors=[],
        trace=[],
        escalations=[],
    )
