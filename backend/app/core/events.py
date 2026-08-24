"""Real-time event broker for SSE and WebSocket agent telemetry streaming."""

from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any, AsyncGenerator

from autoanalyst.agents.orchestrator import OrchestratorEvent

logger = logging.getLogger(__name__)


class EventBroker:
    """Pub/Sub event broker routing orchestrator events to connected SSE listeners."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[str]]] = defaultdict(list)
        self._history: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def publish_event(self, event: OrchestratorEvent) -> None:
        """Publish an event to all subscribers listening to run_id."""
        event_dict = {
            "event_type": event.event_type,
            "run_id": event.run_id,
            "agent_name": event.agent_name,
            "data": event.data,
            "timestamp": event.timestamp,
        }
        self._history[event.run_id].append(event_dict)

        payload = json.dumps(event_dict)
        for queue in list(self._subscribers.get(event.run_id, [])):
            try:
                queue.put_nowait(payload)
            except Exception as exc:
                logger.warning("Failed to enqueue event to subscriber: %s", exc)

    def get_run_history(self, run_id: str) -> list[dict[str, Any]]:
        """Retrieve stored event history for a run."""
        return list(self._history.get(run_id, []))

    async def subscribe(self, run_id: str) -> AsyncGenerator[str, None]:
        """Subscribe to a run's live event stream as an async generator."""
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._subscribers[run_id].append(queue)

        # First yield past historical events
        for past_event in self._history.get(run_id, []):
            yield f"data: {json.dumps(past_event)}\n\n"

        try:
            while True:
                data = await queue.get()
                yield f"data: {data}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in self._subscribers[run_id]:
                self._subscribers[run_id].remove(queue)


GLOBAL_EVENT_BROKER = EventBroker()
