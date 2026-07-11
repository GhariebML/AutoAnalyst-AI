import re

with open(r"d:\ADPilot\src\adpilot\services\task_manager.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace run
new_run = """    async def run(self, orchestrator_input: OrchestratorInput) -> OrchestratorOutput:
        self._run_records = []
        self._errors = []
        campaign = orchestrator_input.campaign

        logger.info("TaskManager | starting pipeline | business=%s", campaign.business_name)

        from ..schemas.agent_schemas import CampaignContext
        context = CampaignContext(
            campaign_id="task-" + _now().replace(":", ""),
            brief=campaign
        )

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
        )"""

content = re.sub(r"    async def run\(self, orchestrator_input: OrchestratorInput\) -> OrchestratorOutput:.*?errors=self._errors,\n        \)", new_run, content, flags=re.DOTALL)

# Replace evaluate
new_evaluate = """    async def evaluate(self, analytics_input: AnalyticsAgentInput) -> AnalyticsAgentOutput:
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

        return output"""

content = re.sub(r"    async def evaluate\(self, analytics_input: AnalyticsAgentInput\) -> AnalyticsAgentOutput:.*?return output", new_evaluate, content, flags=re.DOTALL)

# Replace _run_strategy
new_strategy = """    async def _run_strategy(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(
            agent_name=self._strategy_agent.name,
            status=AgentRunStatus.running,
            started_at=started,
        )
        try:
            context = await self._strategy_agent.run(context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"positioning_statement": context.strategy.positioning_statement}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"StrategyAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)"""

content = re.sub(r"    async def _run_strategy\(self, campaign: CampaignInput\) -> StrategyAgentOutput:.*?self._run_records.append\(record\)", new_strategy, content, flags=re.DOTALL)

# Replace _run_research
new_research = """    async def _run_research(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(
            agent_name=self._research_agent.name,
            status=AgentRunStatus.running,
            started_at=started,
        )
        try:
            context = await self._research_agent.run(context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"key_insights_count": len(context.research.key_insights)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"ResearchAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)"""

content = re.sub(r"    async def _run_research\(self, campaign: CampaignInput\) -> ResearchAgentOutput:.*?self._run_records.append\(record\)", new_research, content, flags=re.DOTALL)

# Replace _run_content_analytics_loop
new_loop = """    async def _run_content_analytics_loop(self, context: CampaignContext) -> CampaignContext:
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

        return context"""

content = re.sub(r"    async def _run_content_analytics_loop\([^)]+\) -> tuple\[ContentAgentOutput, AnalyticsAgentOutput\]:.*?return content_output, analytics_output", new_loop, content, flags=re.DOTALL)

# Replace _run_content
new_content = """    async def _run_content(self, context: CampaignContext, optimization_context: list[str] | None, attempt: int) -> CampaignContext:
        started = _now()
        agent_label = f"{self._content_agent.name}" if attempt == 0 else f"{self._content_agent.name}_retry_{attempt}"
        record = AgentRunRecord(agent_name=agent_label, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._content_agent.run(context, optimization_context=optimization_context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"ads_count": len(context.content.ads), "social_posts_count": len(context.content.social_posts)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"ContentAgent (attempt {attempt}) failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)"""

content = re.sub(r"    async def _run_content\(.*?self._run_records.append\(record\)", new_content, content, flags=re.DOTALL)

# Replace _run_analytics
new_analytics = """    async def _run_analytics(self, context: CampaignContext, attempt: int) -> CampaignContext:
        started = _now()
        agent_label = f"{self._analytics_agent.name}" if attempt == 0 else f"{self._analytics_agent.name}_retry_{attempt}"
        record = AgentRunRecord(agent_name=agent_label, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._analytics_agent.run(context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"health_score_overall": context.analytics.health_score.overall, "gate_passed": AnalyticsAgent.passes_quality_gate(context.analytics)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"AnalyticsAgent (attempt {attempt}) failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)"""

content = re.sub(r"    async def _run_analytics\(.*?self._run_records.append\(record\)", new_analytics, content, flags=re.DOTALL)

# Replace _run_design
new_design = """    async def _run_design(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(agent_name=self._design_agent.name, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._design_agent.run(context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"briefs_count": len(context.design.design_briefs), "visuals_count": len(context.design.generated_visuals)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"DesignAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)"""

content = re.sub(r"    async def _run_design\(.*?self._run_records.append\(record\)", new_design, content, flags=re.DOTALL)

# Replace _run_campaign_manager
new_cm = """    async def _run_campaign_manager(self, context: CampaignContext) -> CampaignContext:
        started = _now()
        record = AgentRunRecord(agent_name=self._campaign_manager_agent.name, status=AgentRunStatus.running, started_at=started)
        try:
            context = await self._campaign_manager_agent.run(context)
            record.status = AgentRunStatus.success
            record.output_snapshot = {"channel_allocations_count": len(context.campaign_manager.channel_budget_allocations), "weekly_schedule_count": len(context.campaign_manager.weekly_schedule)}
            return context
        except Exception as exc:
            record.status = AgentRunStatus.failed
            record.error_message = str(exc)
            raise AgentExecutionError(f"CampaignManagerAgent failed: {exc}") from exc
        finally:
            record.finished_at = _now()
            self._run_records.append(record)"""

content = re.sub(r"    async def _run_campaign_manager\(.*?self._run_records.append\(record\)", new_cm, content, flags=re.DOTALL)

with open(r"d:\ADPilot\src\adpilot\services\task_manager.py", "w", encoding="utf-8") as f:
    f.write(content)
