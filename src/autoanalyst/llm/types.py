"""Core data contracts, task categories, and token usage schemas for LLM infrastructure."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskCategory(str, Enum):
    """Categorization of agent and system tasks for fine-grained model routing."""

    ORCHESTRATION = "orchestration"
    DATA_PROFILING = "data_profiling"
    EDA = "eda"
    PREPROCESSING = "preprocessing"
    MACHINE_LEARNING = "machine_learning"
    EVALUATION = "evaluation"
    INSIGHTS = "insights"
    REPORTING = "reporting"
    CHAT = "chat"
    GENERAL = "general"


class LLMMessage(BaseModel):
    """Structured chat completion message."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: str | None = None


class LLMUsage(BaseModel):
    """Token consumption and estimated cost breakdown."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float | None = None


class LLMResponse(BaseModel):
    """Standardized response from the centralized LLM gateway."""

    content: str
    model: str
    provider: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    duration_ms: float = 0.0
    parsed: Any | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class LLMRecord:
    """Telemetry log record for a single LLM generation request."""

    request_id: str
    run_id: str | None
    agent_name: str | None
    task_category: str
    model: str
    provider: str
    status: Literal["success", "retry", "fallback", "error"]
    duration_ms: float
    usage: LLMUsage
    error_message: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
