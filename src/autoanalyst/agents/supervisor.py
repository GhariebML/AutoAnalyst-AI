"""Supervisor intelligence for the AutoAnalyst agent graph (M3).

Responsibilities:
- re-exports the supervisor routing primitives (``should_abort``,
  ``route_after_features``) owned by ``graph.py``
- HITL sessions: checkpointed runs that pause before cleaning/modeling until
  a human approves the step

The supervisor is deterministic; an optional LLM router arrives in M5.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver

from autoanalyst.agents.graph import (
    _to_pipeline_result,
    build_graph,
    route_after_features,  # noqa: F401 - re-exported for supervisor consumers
    should_abort,  # noqa: F401 - re-exported for supervisor consumers
)
from autoanalyst.agents.serde import PickleSerde
from autoanalyst.agents.state import (
    APPROVAL_STEPS,
    AutoAnalystConfig,
    AutoAnalystState,
    create_initial_state,
)
from autoanalyst.pipeline import PipelineResult

logger = logging.getLogger(__name__)


class SupervisedRun:
    """Checkpointed agent run with human-in-the-loop approval pauses.

    Usage::

        run = SupervisedRun(config)
        run.start()                      # executes until a pause or completion
        if run.pending_approval():
            run.approve(run.pending_approval())
            run.resume()                 # repeats until completion
        result = run.final_result()
    """

    def __init__(self, config: AutoAnalystConfig) -> None:
        self.config = config
        self._checkpointed = config.require_approval
        self._thread_id = str(uuid.uuid4())
        self._thread_config: RunnableConfig = {"configurable": {"thread_id": self._thread_id}}
        self._graph = build_graph(
            checkpointer=MemorySaver(serde=PickleSerde()) if config.require_approval else None,
            interrupt_before=("cleaning", "modeling") if config.require_approval else None,
        )
        self._state: AutoAnalystState | None = None

    @property
    def thread_id(self) -> str:
        return self._thread_id

    def start(self) -> None:
        """Run from the beginning until completion or an approval pause."""
        self._invoke(create_initial_state(self.config))

    def pending_approval(self) -> str | None:
        """Return the step awaiting approval, or None when not paused."""
        if not self._checkpointed:
            return None
        snapshot = self._graph.get_state(self._thread_config)
        nxt = tuple(getattr(snapshot, "next", ()) or ())
        if len(nxt) != 1:
            return None
        candidate = nxt[0]
        return candidate if candidate in APPROVAL_STEPS else None

    def approve(self, step: str, approved: bool = True) -> None:
        """Record a human decision for a supervised step."""
        if step not in APPROVAL_STEPS:
            raise ValueError(f"Unknown supervised step '{step}'. Expected one of {sorted(APPROVAL_STEPS)}.")
        approvals = dict((self._state or {}).get("approvals") or {})
        approvals[step] = approved
        self._graph.update_state(self._thread_config, {"approvals": approvals})
        if self._state is not None:
            self._state["approvals"] = approvals

    def resume(self) -> None:
        """Continue a paused run until completion or the next pause."""
        self._invoke(None)

    def final_result(self) -> PipelineResult:
        """Map the latest state onto the public PipelineResult contract."""
        if self._state is None:
            raise RuntimeError("Run has not been started.")
        return _to_pipeline_result(self._state)

    @property
    def finished(self) -> bool:
        """True when the run started and no node remains to execute."""
        if self._state is None:
            return False
        if not self._checkpointed:
            return True
        snapshot = self._graph.get_state(self._thread_config)
        return not tuple(getattr(snapshot, "next", ()) or ())

    def trace(self) -> list[Any]:
        """Trace records for every executed/skipped/failed node so far."""
        if self._state is None:
            return []
        return list(self._state.get("trace") or [])

    # ------------------------------------------------------------------

    def _invoke(self, input_state: Any) -> None:
        raw = self._graph.invoke(input_state, config=self._thread_config)
        self._state = cast(AutoAnalystState, raw)


__all__ = ["SupervisedRun", "route_after_features", "should_abort"]
