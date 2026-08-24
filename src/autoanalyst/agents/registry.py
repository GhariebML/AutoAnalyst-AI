"""Agent Registry and dynamic capability discovery engine for AutoAnalyst AI."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from autoanalyst.agents.base import BaseAutonomousAgent

logger = logging.getLogger(__name__)


class AgentCapability(BaseModel):
    """Specific analytical capability exposed by an agent."""

    name: str
    description: str
    required_inputs: list[str] = Field(default_factory=list)
    produced_outputs: list[str] = Field(default_factory=list)


@dataclass
class AgentManifest:
    """Registration record for an agent in the registry."""

    agent: BaseAutonomousAgent
    name: str
    description: str
    capabilities: list[AgentCapability] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


class AgentRegistry:
    """Central registry providing dynamic agent lookup and capability-based routing."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentManifest] = {}

    def register(
        self,
        agent: BaseAutonomousAgent,
        capabilities: list[AgentCapability] | None = None,
        tools: list[str] | None = None,
    ) -> None:
        manifest = AgentManifest(
            agent=agent,
            name=agent.name,
            description=agent.description,
            capabilities=capabilities or [],
            tools=tools or [],
        )
        self._agents[agent.name] = manifest
        logger.info("Registered agent: %s with %d capabilities", agent.name, len(manifest.capabilities))

    def get(self, name: str) -> BaseAutonomousAgent | None:
        manifest = self._agents.get(name)
        return manifest.agent if manifest else None

    def get_manifest(self, name: str) -> AgentManifest | None:
        return self._agents.get(name)

    def list_agents(self) -> list[AgentManifest]:
        return list(self._agents.values())

    def find_agents_for_capability(self, capability_name: str) -> list[BaseAutonomousAgent]:
        matched = []
        for manifest in self._agents.values():
            if any(cap.name == capability_name for cap in manifest.capabilities):
                matched.append(manifest.agent)
        return matched


GLOBAL_AGENT_REGISTRY = AgentRegistry()
