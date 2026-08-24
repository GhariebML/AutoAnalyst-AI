"""Pydantic schemas for analysis runs and agent telemetry."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnalysisCreateRequest(BaseModel):
    dataset_id: str
    target_column: str | None = None
    model_task: str = "auto"
    missing_strategy: str = "median"
    require_approval: bool = False


class AnalysisApproveRequest(BaseModel):
    step: str
    approved: bool = True
    modifications: dict[str, Any] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    id: str
    dataset_id: str
    target_column: str | None = None
    model_task: str
    status: str
    champion_model_name: str | None = None
    champion_score: float | None = None
    executive_summary: str | None = None
    insights: list[str] = Field(default_factory=list)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    profile: dict[str, Any] | None = None
    eda_results: dict[str, Any] | None = None
    model_results: dict[str, Any] | None = None
    evaluation_results: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    duration_ms: float = 0.0
    report_path: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentEventResponse(BaseModel):
    event_type: str
    run_id: str
    agent_name: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: str
