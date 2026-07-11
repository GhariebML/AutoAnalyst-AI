"""Framework-agnostic campaign orchestrator.

The orchestrator coordinates the ADPilot agent pipeline, records each agent
execution, and returns a structured campaign result that can be consumed by the
API layer, CLI scripts, or future worker queues.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from ..agents.analytics_agent import AnalyticsAgent
from ..agents.campaign_manager_agent import CampaignManagerAgent
from ..agents.content_agent import ContentAgent
from ..agents.design_agent import DesignAgent
from ..agents.research_agent import ResearchAgent
from ..agents.strategy_agent import StrategyAgent
from ..schemas.agent_schemas import (
    AgentRunRecord,
    AgentRunStatus,
    AnalyticsAgentInput,
    AnalyticsAgentOutput,
    CampaignInput,
    CampaignManagerInput,
    CampaignManagerOutput,
    ContentAgentInput,
    ContentAgentOutput,
    DesignAgentInput,
    DesignAgentOutput,
    OrchestratorInput,
    OrchestratorOutput,
    ResearchAgentInput,
    ResearchAgentOutput,
    StrategyAgentInput,
    StrategyAgentOutput,
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinate all agents for a single campaign run."""

    def __init__(
        self,
        strategy_agent: StrategyAgent | None = None,
        research_agent: ResearchAgent | None = None,
        content_agent: ContentAgent | None = None,
        analytics_agent: AnalyticsAgent | None = None,
        design_agent: DesignAgent | None = None,
        campaign_manager_agent: CampaignManagerAgent | None = None,
    ) -> None:
        self.strategy_agent = strategy_agent or StrategyAgent()
        self.research_agent = research_agent or ResearchAgent()
        self.content_agent = content_agent or ContentAgent()
        self.analytics_agent = analytics_agent or AnalyticsAgent()
        self.design_agent = design_agent or DesignAgent()
        self.campaign_manager_agent = campaign_manager_agent or CampaignManagerAgent()
        self.agent_run_records: list[AgentRunRecord] = []

    async def run(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        """Run the full multi-agent campaign pipeline."""
        campaign = input_data.campaign
        self.agent_run_records = []
        logger.info("Starting campaign orchestration for %s", campaign.business_name)

        strategy = await self._run_with_retry(
            "strategy_agent",
            self.strategy_agent.run,
            StrategyAgentInput(campaign=campaign),
        )
        research = await self._run_with_retry(
            "research_agent",
            self.research_agent.run,
            ResearchAgentInput(campaign=campaign),
        )
        content = await self._run_with_retry(
            "content_agent",
            self.content_agent.run,
            ContentAgentInput(strategy=strategy, research=research),
        )
        analytics = await self._run_with_retry(
            "analytics_agent",
            self.analytics_agent.run,
            AnalyticsAgentInput(
                campaign=campaign,
                strategy=strategy,
                research=research,
                content=content,
            ),
        )
        design = await self._run_with_retry(
            "design_agent",
            self.design_agent.run,
            DesignAgentInput(strategy=strategy, content=content),
        )
        campaign_manager = await self._run_with_retry(
            "campaign_manager_agent",
            self.campaign_manager_agent.run,
            CampaignManagerInput(
                campaign=campaign,
                strategy=strategy,
                research=research,
                content=content,
                analytics=analytics,
                design=design,
            ),
        )

        return self.assemble_final_output(
            campaign=campaign,
            strategy=strategy,
            research=research,
            content=content,
            analytics=analytics,
            design=design,
            campaign_manager=campaign_manager,
        )

    async def run_campaign(self, campaign_input: CampaignInput) -> CampaignManagerOutput:
        """Backward-compatible helper that returns only the final campaign package."""
        output = await self.run(OrchestratorInput(campaign=campaign_input))
        if output.campaign_manager is None:  # pragma: no cover - defensive guard
            raise RuntimeError("Campaign manager output was not produced.")
        return output.campaign_manager

    async def run_agent(self, agent_name: str, agent_input: dict[str, Any]) -> dict[str, Any]:
        """Run one named agent and return its serialized output."""
        agent_map: dict[str, tuple[Callable[[Any], Awaitable[Any]], type[Any]]] = {
            "strategy_agent": (self.strategy_agent.run, StrategyAgentInput),
            "research_agent": (self.research_agent.run, ResearchAgentInput),
            "content_agent": (self.content_agent.run, ContentAgentInput),
            "analytics_agent": (self.analytics_agent.run, AnalyticsAgentInput),
            "design_agent": (self.design_agent.run, DesignAgentInput),
            "campaign_manager_agent": (self.campaign_manager_agent.run, CampaignManagerInput),
        }
        if agent_name not in agent_map:
            raise ValueError(f"Unknown agent: {agent_name}")

        agent_callable, input_model = agent_map[agent_name]
        result = await self._run_with_retry(agent_name, agent_callable, input_model(**agent_input))
        return result.model_dump()

    def collect_run_record(
        self,
        agent_name: str,
        status: AgentRunStatus,
        started_at: str,
        finished_at: str | None = None,
        error_message: str | None = None,
        output_snapshot: dict[str, Any] | None = None,
    ) -> AgentRunRecord:
        """Create and store one agent run record."""
        record = AgentRunRecord(
            agent_name=agent_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            error_message=error_message,
            output_snapshot=output_snapshot,
        )
        self.agent_run_records.append(record)
        return record

    def assemble_final_output(
        self,
        campaign: CampaignInput,
        strategy: StrategyAgentOutput,
        research: ResearchAgentOutput,
        content: ContentAgentOutput,
        analytics: AnalyticsAgentOutput,
        design: DesignAgentOutput,
        campaign_manager: CampaignManagerOutput | None = None,
    ) -> OrchestratorOutput:
        """Build the final orchestrator response."""
        summary = (
            f"Campaign package generated for {campaign.business_name} using "
            f"{len(campaign.channels)} channel(s), {len(content.ads)} ad copy item(s), "
            f"and {len(design.generated_visuals)} generated visual(s)."
        )
        return OrchestratorOutput(
            campaign_input=campaign,
            strategy=strategy,
            research=research,
            content=content,
            analytics=analytics,
            design=design,
            campaign_manager=campaign_manager,
            agent_run_records=self.agent_run_records,
            final_campaign_summary=summary,
            errors=[],
        )

    async def _run_with_retry(
        self,
        agent_name: str,
        agent_callable: Callable[[Any], Awaitable[Any]],
        input_data: Any,
        max_attempts: int = 3,
        backoff_ms: int = 200,
    ) -> Any:
        """Execute an agent with retry and run-record tracking."""
        started_at = _utc_now()

        for attempt in range(1, max_attempts + 1):
            try:
                result = await agent_callable(input_data)
                finished_at = _utc_now()
                self.collect_run_record(
                    agent_name=agent_name,
                    status=AgentRunStatus.success,
                    started_at=started_at,
                    finished_at=finished_at,
                    output_snapshot=result.model_dump() if hasattr(result, "model_dump") else None,
                )
                logger.info("%s succeeded on attempt %d", agent_name, attempt)
                return result
            except Exception as exc:
                logger.warning("%s failed on attempt %d: %s", agent_name, attempt, exc)
                if attempt >= max_attempts:
                    finished_at = _utc_now()
                    self.collect_run_record(
                        agent_name=agent_name,
                        status=AgentRunStatus.failed,
                        started_at=started_at,
                        finished_at=finished_at,
                        error_message=str(exc),
                    )
                    raise

                await asyncio.sleep((backoff_ms * (2 ** (attempt - 1))) / 1000)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
