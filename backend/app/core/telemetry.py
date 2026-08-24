"""Prometheus APM metrics telemetry exporter for AutoAnalyst AI."""

from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsStore:
    """In-memory thread-safe metrics storage for Prometheus exposition."""

    def __init__(self) -> None:
        self.request_counts: dict[str, int] = {}
        self.request_latencies: dict[str, float] = {}
        self.agent_executions: dict[str, int] = {}
        self.active_runs: int = 0

    def record_request(self, method: str, path: str, status_code: int, duration_sec: float) -> None:
        key = f'{method}_{path}_{status_code}'
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        self.request_latencies[key] = self.request_latencies.get(key, 0.0) + duration_sec

    def record_agent_run(self, agent_name: str) -> None:
        self.agent_executions[agent_name] = self.agent_executions.get(agent_name, 0) + 1

    def generate_prometheus_text(self) -> str:
        lines: list[str] = [
            "# HELP autoanalyst_http_requests_total Total HTTP requests handled by AutoAnalyst API",
            "# TYPE autoanalyst_http_requests_total counter",
        ]
        for key, count in self.request_counts.items():
            parts = key.split("_", 2)
            if len(parts) == 3:
                m, p, s = parts
                lines.append(f'autoanalyst_http_requests_total{{method="{m}",path="{p}",status="{s}"}} {count}')

        lines.extend([
            "",
            "# HELP autoanalyst_agent_executions_total Total autonomous agent executions",
            "# TYPE autoanalyst_agent_executions_total counter",
        ])
        for agent, count in self.agent_executions.items():
            lines.append(f'autoanalyst_agent_executions_total{{agent="{agent}"}} {count}')

        lines.extend([
            "",
            "# HELP autoanalyst_active_runs Current active multi-agent runs",
            "# TYPE autoanalyst_active_runs gauge",
            f"autoanalyst_active_runs {self.active_runs}",
            "",
        ])
        return "\n".join(lines)


GLOBAL_METRICS = MetricsStore()


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware collecting HTTP request telemetry for Prometheus."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        path = request.url.path
        # Normalize dynamic path prefixes
        if path.startswith("/api/v1"):
            GLOBAL_METRICS.record_request(request.method, path, response.status_code, duration)
        return response
