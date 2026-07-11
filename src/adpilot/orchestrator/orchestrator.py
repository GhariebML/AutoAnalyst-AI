"""Multi-agent campaign pipeline orchestrator using shared memory context."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Awaitable, Callable, List, Optional

from ..agents.strategy_agent import StrategyAgent
from ..agents.audience_agent import AudienceAgent
from ..agents.competitor_agent import CompetitorAgent
from ..agents.content_agent import ContentAgent
from ..agents.analytics_agent import AnalyticsAgent
from ..agents.optimization_agent import OptimizationAgent
from ..schemas.agent_schemas import (
    CampaignContext,
    CampaignInput,
    AgentRunRecord,
    AgentRunStatus,
)
from ..services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class CampaignOrchestrator:
    """Coordinate the production-grade multi-agent campaign pipeline with memory."""

    def __init__(
        self,
        memory_service: Optional[MemoryService] = None,
        strategy_agent: Optional[StrategyAgent] = None,
        audience_agent: Optional[AudienceAgent] = None,
        competitor_agent: Optional[CompetitorAgent] = None,
        content_agent: Optional[ContentAgent] = None,
        analytics_agent: Optional[AnalyticsAgent] = None,
        optimization_agent: Optional[OptimizationAgent] = None,
    ) -> None:
        self.memory_service = memory_service or MemoryService()
        self.strategy_agent = strategy_agent or StrategyAgent()
        self.audience_agent = audience_agent or AudienceAgent()
        self.competitor_agent = competitor_agent or CompetitorAgent()
        self.content_agent = content_agent or ContentAgent()
        self.analytics_agent = analytics_agent or AnalyticsAgent()
        self.optimization_agent = optimization_agent or OptimizationAgent()
        self.agent_run_records: List[AgentRunRecord] = []

    async def run(self, campaign_id: str, brief: CampaignInput) -> CampaignContext:
        """Run the full context-aware agent pipeline."""
        logger.info("Initializing campaign orchestration for id: %s", campaign_id)
        
        # Initialize context in memory store
        context = CampaignContext(campaign_id=campaign_id, brief=brief)
        await self.memory_service.save_context(campaign_id, context)

        # 1. Strategy Agent
        context = await self._execute_stage("strategy_agent", self.strategy_agent.run, campaign_id)

        # 2. Audience Agent
        context = await self._execute_stage("audience_agent", self.audience_agent.run, campaign_id)

        # 3. Competitor Agent
        context = await self._execute_stage("competitor_agent", self.competitor_agent.run, campaign_id)

        # 4. Content Agent
        context = await self._execute_stage("content_agent", self.content_agent.run, campaign_id)

        # 5. Analytics Agent
        context = await self._execute_stage("analytics_agent", self.analytics_agent.run, campaign_id)

        # 6. Optimization Agent
        context = await self._execute_stage("optimization_agent", self.optimization_agent.run, campaign_id)

        logger.info("Successfully completed campaign orchestration for id: %s", campaign_id)
        return context

    async def _execute_stage(
        self,
        agent_name: str,
        agent_run_fn: Callable[[CampaignContext], Awaitable[CampaignContext]],
        campaign_id: str,
        max_attempts: int = 3,
        backoff_ms: int = 200,
    ) -> CampaignContext:
        """Execute a single pipeline agent stage with loading, saving, retries, and recording."""
        started_at = datetime.now(timezone.utc).isoformat()
        logger.info("Starting agent stage: %s for campaign: %s", agent_name, campaign_id)

        # Load context from shared memory store
        context = await self.memory_service.get_context(campaign_id)
        if not context:
            raise RuntimeError(f"Campaign context for {campaign_id} not found in memory store before stage {agent_name}.")

        for attempt in range(1, max_attempts + 1):
            try:
                # Call agent with context
                context = await agent_run_fn(context)
                
                # Save context back to shared memory store (Memory Store Step)
                await self.memory_service.save_context(campaign_id, context)

                finished_at = datetime.now(timezone.utc).isoformat()
                self._record_run(
                    agent_name=agent_name,
                    status=AgentRunStatus.success,
                    started_at=started_at,
                    finished_at=finished_at,
                )
                logger.info("Agent stage %s succeeded on attempt %d", agent_name, attempt)
                return context
            except Exception as exc:
                logger.warning("Agent stage %s failed on attempt %d: %s", agent_name, attempt, exc)
                if attempt >= max_attempts:
                    finished_at = datetime.now(timezone.utc).isoformat()
                    self._record_run(
                        agent_name=agent_name,
                        status=AgentRunStatus.failed,
                        started_at=started_at,
                        finished_at=finished_at,
                        error_message=str(exc),
                    )
                    raise
                await asyncio.sleep((backoff_ms * (2 ** (attempt - 1))) / 1000)

        return context

    def _record_run(
        self,
        agent_name: str,
        status: AgentRunStatus,
        started_at: str,
        finished_at: str,
        error_message: Optional[str] = None,
    ) -> None:
        record = AgentRunRecord(
            agent_name=agent_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            error_message=error_message,
        )
        self.agent_run_records.append(record)
