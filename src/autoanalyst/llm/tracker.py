"""Thread-safe usage tracker and telemetry metrics aggregator for LLM requests."""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any

from autoanalyst.llm.types import LLMRecord


class LLMUsageTracker:
    """Thread-safe collector for LLM token usage, latencies, and error rates."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: list[LLMRecord] = []
        self._total_requests: int = 0
        self._successful_requests: int = 0
        self._failed_requests: int = 0
        self._total_prompt_tokens: int = 0
        self._total_completion_tokens: int = 0
        self._tokens_by_agent: dict[str, int] = defaultdict(int)
        self._tokens_by_model: dict[str, int] = defaultdict(int)

    def record_request(self, record: LLMRecord) -> None:
        """Record an executed LLM request."""
        with self._lock:
            self._records.append(record)
            self._total_requests += 1

            if record.status in ("success", "fallback"):
                self._successful_requests += 1
            else:
                self._failed_requests += 1

            self._total_prompt_tokens += record.usage.prompt_tokens
            self._total_completion_tokens += record.usage.completion_tokens

            agent_key = record.agent_name or "system"
            self._tokens_by_agent[agent_key] += record.usage.total_tokens
            self._tokens_by_model[record.model] += record.usage.total_tokens

    def get_summary(self) -> dict[str, Any]:
        """Get aggregate metrics across all recorded LLM requests."""
        with self._lock:
            total_tokens = self._total_prompt_tokens + self._total_completion_tokens
            success_rate = (
                (self._successful_requests / self._total_requests * 100.0)
                if self._total_requests > 0
                else 100.0
            )
            avg_duration_ms = (
                sum(r.duration_ms for r in self._records) / len(self._records)
                if self._records
                else 0.0
            )

            return {
                "total_requests": self._total_requests,
                "successful_requests": self._successful_requests,
                "failed_requests": self._failed_requests,
                "success_rate_pct": round(success_rate, 2),
                "total_prompt_tokens": self._total_prompt_tokens,
                "total_completion_tokens": self._total_completion_tokens,
                "total_tokens": total_tokens,
                "average_latency_ms": round(avg_duration_ms, 2),
                "tokens_by_agent": dict(self._tokens_by_agent),
                "tokens_by_model": dict(self._tokens_by_model),
                "recent_records_count": len(self._records),
            }

    def get_records_for_run(self, run_id: str) -> list[LLMRecord]:
        """Retrieve all telemetry records for a specific analysis run."""
        with self._lock:
            return [r for r in self._records if r.run_id == run_id]

    def reset(self) -> None:
        """Reset all tracking counters."""
        with self._lock:
            self._records.clear()
            self._total_requests = 0
            self._successful_requests = 0
            self._failed_requests = 0
            self._total_prompt_tokens = 0
            self._total_completion_tokens = 0
            self._tokens_by_agent.clear()
            self._tokens_by_model.clear()


# Global singleton instance
GLOBAL_USAGE_TRACKER = LLMUsageTracker()
