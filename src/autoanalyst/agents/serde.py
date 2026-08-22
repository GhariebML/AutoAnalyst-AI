"""Checkpoint serialization for the agent graph.

LangGraph's default JSON/msgpack serializer cannot encode pandas objects
stored in ``AutoAnalystState``. ``PickleSerde`` keeps checkpointed HITL runs
working by pickling channel values.

Security note: pickle is only acceptable here because checkpoints are local,
single-process, and contain exclusively project-generated state. Do not load
checkpoint blobs from untrusted sources.
"""

from __future__ import annotations

import pickle
from typing import Any


class PickleSerde:
    """Minimal LangGraph SerializerProtocol implementation based on pickle."""

    def dumps_typed(self, obj: Any) -> tuple[str, bytes]:
        return ("pickle", pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))

    def loads_typed(self, data: tuple[str, bytes]) -> Any:
        kind, blob = data
        if kind != "pickle":
            raise ValueError(f"Unsupported checkpoint payload type: {kind}")
        return pickle.loads(blob)


__all__ = ["PickleSerde"]
