"""Phase 2 DAG Task Manager – full async pipeline orchestration.

DAG Execution Order
-------------------
CampaignInput
    └─► StrategyAgent → StrategyAgentOutput
    └─► ResearchAgent → ResearchAgentOutput
    └─► ContentAgent  → ContentAgentOutput
    └─► AnalyticsAgent (Quality Gate)
            │
            ├─ health_score < 70  ──► ContentAgent (retry with recommendations)
            │                              └─► AnalyticsAgent (re-evaluate)
            │                     (max MAX_CONTENT_RETRIES retries)
            │
             └─ health_score ≥ 70 ──► DesignAgent → DesignAgentOutput
                                     └─► CampaignManagerAgent → CampaignManagerOutput
                                     └─► OrchestratorOutput (status: completed)

The ``TaskManager`` is the single async service consumed by the FastAPI layer.
It records every agent run via ``AgentRunRecord`` and assembles the final
``OrchestratorOutput``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from ..agents.analytics_agent import AnalyticsAgent
from ..agents.campaign_manager_agent import CampaignManagerAgent
from ..agents.content_agent import ContentAgent
from ..agents.design_agent import DesignAgent
from ..agents.research_agent import ResearchAgent
from ..agents.strategy_agent import StrategyAgent
from ..core.exceptions import AgentExecutionError
from .memory_service import MemoryService
from ..schemas.agent_schemas import (
    AgentRunRecord,
    AgentRunStatus,
    AnalyticsAgentInput,
    AnalyticsAgentOutput,
    CampaignInput,
    DesignAgentOutput,
    OrchestratorInput,
    OrchestratorOutput,
)
from ..utils.logging_utils import logger


def _now() -> str:
    """Return the current UTC timestamp as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


class TaskManager:
    """Async DAG orchestrator for the AdPilot multi-agent pipeline.

    Usage::

        manager = TaskManager()
        result = await manager.run(OrchestratorInput(campaign=campaign_input))
    """

    # Maximum times ContentAgent is retried after a quality-gate failure.
    MAX_CONTENT_RETRIES: int = 3

    def __init__(self, memory_service: Optional[MemoryService] = None) -> None:
        self.memory_service = memory_service or MemoryService()
        # Instantiate all agents once – they are stateless across runs.
        self._strategy_agent  = StrategyAgent()
        self._research_agent  = ResearchAgent()
        self._content_agent   = ContentAgent()
        self._analytics_agent = AnalyticsAgent()
        self._design_agent    = DesignAgent()
        self._campaign_manager_agent = CampaignManagerAgent()

        self._run_records: List[AgentRunRecord] = []
        self._errors: List[str] = []

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    async def run(self, orchestrator_input: OrchestratorInput) -> OrchestratorOutput:
        self._run_records = []
        self._errors = []
        campaign = orchestrator_input.campaign

        logger.info("TaskManager | starting pipeline | business=%s", campaign.business_name)

        from ..schemas.agent_schemas import CampaignContext
        context = CampaignContext(
            campaign_id="task-" + _now().replace(":", ""),
            brief=campaign
        )
        await self.memory_service.save_context(context.campaign_id, context)

        context = await self._run_strategy(context)
        context = await self._run_research(context)
        context = await self._run_content_analytics_loop(context)

        design = None
        campaign_manager = None
        if AnalyticsAgent.passes_quality_gate(context.analytics):
            context = await self._run_design(context)
            design = context.design
            context = await self._run_campaign_manager(context)
            campaign_manager = context.campaign_manager
        else:
            msg = (
                f"Quality gate failed after {self.MAX_CONTENT_RETRIES} retries "
                f"(final score: {context.analytics.health_score.overall:.2f}). "
                "DesignAgent and CampaignManagerAgent were skipped."
            )
            logger.warning("TaskManager | %s", msg)
            self._errors.append(msg)

        summary = self._build_summary(campaign, context.analytics, design)

        logger.info(
            "TaskManager | pipeline complete | score=%.2f | pass=%s | retries=%d",
            context.analytics.health_score.overall,
            AnalyticsAgent.passes_quality_gate(context.analytics),
            self._count_content_retries(),
        )

        return OrchestratorOutput(
            campaign_input=campaign,
            strategy=context.strategy,
            research=context.research,
            content=context.content,
            analytics=context.analytics,
            design=design or self._placeholder_design_output(),
            campaign_manager=campaign_manager,
            agent_run_records=self._run_records,
            final_campaign_summary=summary,
            errors=self._errors,
        )

    # ------------------------------------------------------------------ #
    # Convenience: evaluate analytics on an already-assembled input       #
    # (used by the /api/analytics/evaluate endpoint)                      #
    # ------------------------------------------------------------------ #

    async def evaluate(self, analytics_input: AnalyticsAgentInput) -> AnalyticsAgentOutput:
        self._run_records = []
        self._errors = []

        started = _now()
        record = AgentRunRecord(
            agent_name=self._analytics_agent.name,
            status=AgentRunStatus.running,
            started_at=started,
        )

        try:
            from ..schemas.agent_schemas import CampaignContext
            context = CampaignContext(
                campaign_id="eval-" + _now().replace(":", ""),
                brief=analytics_input.campaign,
                strategy=analytics_input.strategy,
                research=analytics_input.research,
                content=analytics_input.content
            )
            context = await self._analytics_agent.run(context)
            output = context.analytics
            record.status = AgentRunStatus.success
            record.output_snapshot = {"health_score_overall": output.health_score.overall}
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"Standalone analytics evaluation failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)

        return output

    # ------------------------------------------------------------------ #
    # Private DAG steps                                                    #
    # ------------------------------------------------------------------ #

    async def _run_strategy(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(
            agent_name=self._strategy_agent.name,
            status=AgentRunStatus.running,
            started_at=started,
        )
        try:
            context = await self._strategy_agent.run(context)
            await self.memory_service.save_context(context.campaign_id, context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"positioning_statement": context.strategy.positioning_statement}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"StrategyAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)

    async def _run_research(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(
            agent_name=self._research_agent.name,
            status=AgentRunStatus.running,
            started_at=started,
        )
        try:
            context = await self._research_agent.run(context)
            await self.memory_service.save_context(context.campaign_id, context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"key_insights_count": len(context.research.key_insights)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"ResearchAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)

    async def _run_content_analytics_loop(self, context: CampaignContext) -> CampaignContext:
        optimization_hints: list[str] | None = None

        for attempt in range(self.MAX_CONTENT_RETRIES + 1):
            context = await self._run_content(
                context=context,
                optimization_context=optimization_hints,
                attempt=attempt,
            )

            context = await self._run_analytics(
                context=context,
                attempt=attempt,
            )

            analytics_output = context.analytics
            passes = AnalyticsAgent.passes_quality_gate(analytics_output)
            logger.info(
                "TaskManager | attempt=%d | health_score=%.2f | gate_pass=%s",
                attempt,
                analytics_output.health_score.overall,
                passes,
            )

            if passes:
                break

            if attempt < self.MAX_CONTENT_RETRIES:
                optimization_hints = AnalyticsAgent.extract_optimization_recommendations(analytics_output)
                logger.info(
                    "TaskManager | quality gate failed | looping back to ContentAgent "
                    "| recommendations=%d | next_attempt=%d",
                    len(optimization_hints),
                    attempt + 1,
                )
            else:
                msg = (
                    f"ContentAgent exhausted all {self.MAX_CONTENT_RETRIES} retry attempts. "
                    f"Final health score: {analytics_output.health_score.overall:.2f}."
                )
                logger.warning("TaskManager | %s", msg)
                self._errors.append(msg)

        return context

    async def _run_content(self, context: CampaignContext, optimization_context: list[str] | None, attempt: int) -> CampaignContext:
        started = _now()
        agent_label = f"{self._content_agent.name}" if attempt == 0 else f"{self._content_agent.name}_retry_{attempt}"
        record = AgentRunRecord(agent_name=agent_label, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._content_agent.run(context, optimization_context=optimization_context)
            await self.memory_service.save_context(context.campaign_id, context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"ads_count": len(context.content.ads), "social_posts_count": len(context.content.social_posts)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"ContentAgent (attempt {attempt}) failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)

    async def _run_analytics(self, context: CampaignContext, attempt: int) -> CampaignContext:
        started = _now()
        agent_label = f"{self._analytics_agent.name}" if attempt == 0 else f"{self._analytics_agent.name}_retry_{attempt}"
        record = AgentRunRecord(agent_name=agent_label, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._analytics_agent.run(context)
            await self.memory_service.save_context(context.campaign_id, context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"health_score_overall": context.analytics.health_score.overall, "gate_passed": AnalyticsAgent.passes_quality_gate(context.analytics)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"AnalyticsAgent (attempt {attempt}) failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)

    async def _run_design(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(agent_name=self._design_agent.name, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._design_agent.run(context)
            await self.memory_service.save_context(context.campaign_id, context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"briefs_count": len(context.design.design_briefs), "visuals_count": len(context.design.generated_visuals)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"DesignAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)

    async def _run_campaign_manager(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(agent_name=self._campaign_manager_agent.name, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._campaign_manager_agent.run(context)
            await self.memory_service.save_context(context.campaign_id, context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"channel_allocations_count": len(context.campaign_manager.channel_budget_allocations), "weekly_schedule_count": len(context.campaign_manager.weekly_schedule)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"CampaignManagerAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _count_content_retries(self) -> int:
        """Return the number of ContentAgent retry records in this run."""
        return sum(1 for r in self._run_records if "_retry_" in r.agent_name)

    def _build_summary(
        self,
        campaign: CampaignInput,
        analytics: AnalyticsAgentOutput,
        design: Optional[DesignAgentOutput],
    ) -> str:
        passed = AnalyticsAgent.passes_quality_gate(analytics)
        retries = self._count_content_retries()
        status = "COMPLETED" if passed else "REQUIRES REVIEW"
        return (
            f"[{status}] Campaign '{campaign.business_name}' pipeline finished. "
            f"Health Score: {analytics.health_score.overall:.2f}/100 "
            f"({'✓ PASSED' if passed else '✗ FAILED'} quality gate). "
            f"Content retries: {retries}. "
            f"Design briefs generated: {len(design.design_briefs) if design else 0}. "
            f"Errors: {len(self._errors)}."
        )

    @staticmethod
    def _placeholder_design_output() -> DesignAgentOutput:
        """Return a minimal DesignAgentOutput when DesignAgent was skipped."""
        from ..schemas.agent_schemas import DesignAgentOutput as _DAO
        return _DAO(
            design_briefs=[],
            generated_visuals=[],
            brand_style_guide_snippet="Design stage skipped – quality gate not passed.",
            generation_errors=["DesignAgent skipped: health score below threshold."],
        )
