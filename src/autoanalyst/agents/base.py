"""Standardized Autonomous Agent base contract and telemetry interfaces for AutoAnalyst AI."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentAction(BaseModel):
    """Record of a tool call or action executed by an agent."""

    tool_name: str
    action_type: str
    status: str  # "ok" | "error"
    duration_ms: float
    summary: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentFinding(BaseModel):
    """Structured analytical finding distinguishing facts from interpretations."""

    category: str
    fact: str
    evidence: str
    interpretation: str
    recommendation: str
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    uncertainty: str | None = None


class AgentDecision(BaseModel):
    """Structured reasoning decision produced by an agent."""

    decision: str
    reason: str
    recommended_agent: str | None = None
    priority: str = "NORMAL"  # "LOW" | "NORMAL" | "HIGH" | "CRITICAL"
    requires_human_approval: bool = False
    approval_prompt: str | None = None


@dataclass
class AgentResult:
    """Standardized output contract returned by all specialized AI agents."""

    agent_name: str
    status: str  # "success" | "error" | "paused_for_approval" | "skipped"
    objective: str
    actions_taken: list[AgentAction] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    findings: list[AgentFinding] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    next_action: AgentDecision | None = None
    requires_human_input: bool = False
    human_prompt: str | None = None
    errors: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def is_success(self) -> bool:
        return self.status == "success"


class BaseAutonomousAgent(ABC):
    """Abstract base class for all specialized AI agent personas."""

    name: str
    description: str
    capabilities: list[str] = []

    def __init__(self, llm_service: Any | None = None) -> None:
        if llm_service is not None:
            self.llm = llm_service
        else:
            from autoanalyst.llm.service import GLOBAL_LLM_SERVICE
            self.llm = GLOBAL_LLM_SERVICE

    def run(self, state: dict[str, Any]) -> AgentResult:
        """Standardized lifecycle: UNDERSTAND -> ASSESS -> DECIDE -> EXECUTE -> VALIDATE -> RECOMMEND."""
        start_time = time.perf_counter()
        logger.info("Starting agent: %s", self.name)
        try:
            result = self._execute(state)
            result.duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return result
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.error("Agent '%s' failed: %s", self.name, exc, exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status="error",
                objective=f"Execute {self.name} autonomous analysis",
                errors=[str(exc)],
                duration_ms=duration_ms,
            )

    @abstractmethod
    def _execute(self, state: dict[str, Any]) -> AgentResult:
        """Core autonomous execution logic implemented by specialized agent personas."""
        raise NotImplementedError
