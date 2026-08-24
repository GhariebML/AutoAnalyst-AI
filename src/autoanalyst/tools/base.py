"""Base analytical tool contracts and metadata interfaces for AutoAnalyst AI."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT")


class ToolMetadata(BaseModel):
    """Metadata describing an analytical tool's capabilities and requirements."""

    name: str
    description: str
    category: str
    version: str = "1.0.0"
    tags: list[str] = Field(default_factory=list)


@dataclass
class ToolResult(Generic[OutputT]):
    """Structured result contract returned by analytical tools."""

    tool_name: str
    status: str  # "success" | "error" | "skipped"
    data: OutputT | None = None
    duration_ms: float = 0.0
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def is_success(self) -> bool:
        return self.status == "success"


class BaseAnalyticalTool(ABC, Generic[InputT, OutputT]):
    """Abstract base class for typed analytical tools wrapping deterministic modules."""

    metadata: ToolMetadata

    def execute(self, params: InputT) -> ToolResult[OutputT]:
        """Execute tool with timing, error handling, and structured result contracts."""
        start_time = time.perf_counter()
        logger.info("Executing tool: %s", self.metadata.name)
        try:
            output = self._run(params)
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return ToolResult(
                tool_name=self.metadata.name,
                status="success",
                data=output,
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.error("Tool '%s' failed: %s", self.metadata.name, exc, exc_info=True)
            return ToolResult(
                tool_name=self.metadata.name,
                status="error",
                error=str(exc),
                duration_ms=duration_ms,
            )

    @abstractmethod
    def _run(self, params: InputT) -> OutputT:
        """Internal execution logic implemented by subclasses."""
        raise NotImplementedError
