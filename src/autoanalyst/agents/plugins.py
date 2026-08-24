"""Plugin registry for extending the agent graph with third-party nodes.

Plugins are ordinary node functions (``state -> dict`` updates) registered
against an anchor node. At ``build_graph`` time each plugin is spliced into
the linear flow *before its anchor's successor*, in registration order:

    intake → profiling → eda → cleaning → features → [modeling → evaluation] → insights → report

Anchors map to successors statically; anchors with conditional or terminal
outgoing edges (``features``, ``report``) are not addressable.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

NodeFunction = Callable[[dict[str, Any]], dict[str, Any]]

ANCHOR_SUCCESSORS: dict[str, str] = {
    "intake": "profiling",
    "profiling": "eda",
    "eda": "cleaning",
    "cleaning": "features",
    "modeling": "evaluation",
    "evaluation": "insights",
    "insights": "report",
}


@dataclass(frozen=True)
class PluginSpec:
    """A registered plugin node."""

    name: str
    anchor: str
    function: NodeFunction


_REGISTRY: dict[str, PluginSpec] = {}


def register_plugin(
    name: str,
    function: NodeFunction,
    anchor: str = "insights",
) -> PluginSpec:
    """Register a plugin node; raises on duplicates or unknown anchors."""
    if name in _REGISTRY:
        raise ValueError(f"Plugin '{name}' is already registered.")
    if anchor not in ANCHOR_SUCCESSORS:
        raise ValueError(f"Unknown anchor '{anchor}'. Addressable anchors: {sorted(ANCHOR_SUCCESSORS)}.")
    if not callable(function):
        raise TypeError("Plugin function must be callable: state -> dict.")
    spec = PluginSpec(name=name, anchor=anchor, function=function)
    _REGISTRY[name] = spec
    logger.info("Registered plugin '%s' after '%s'.", name, anchor)
    return spec


def unregister_plugin(name: str) -> None:
    _REGISTRY.pop(name, None)


def clear_plugins() -> None:
    _REGISTRY.clear()


def active_plugins() -> list[PluginSpec]:
    """Plugins in registration order."""
    return list(_REGISTRY.values())


def plugins_for_anchor(anchor: str) -> list[PluginSpec]:
    return [spec for spec in active_plugins() if spec.anchor == anchor]


__all__ = [
    "ANCHOR_SUCCESSORS",
    "PluginSpec",
    "active_plugins",
    "clear_plugins",
    "plugins_for_anchor",
    "register_plugin",
    "unregister_plugin",
]
