"""LangChain-backed analytics and optimization agent."""

from __future__ import annotations

import logging
import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import (
    CampaignContext, AnalyticsAgentInput, AnalyticsAgentOutput, ResearchAgentOutput, CompetitorAnalysis, PositiveFloat
)

logger = logging.getLogger(__name__)



class AnalyticsAgent(BaseAgent[AnalyticsAgentInput, AnalyticsAgentOutput]):
    """Score campaign assets and produce validated optimization guidance."""

    name = "analytics_agent"
    input_model = AnalyticsAgentInput
    output_model = AnalyticsAgentOutput

    system_prompt = (
        "You are AdPilot's Principal Data Scientist and Analytics Director. Conduct a rigorous, "
        "enterprise-grade evaluation of the campaign using the supplied brief, strategy, research, "
        "and generated content. Calculate an authoritative health score, highly realistic predicted "
        "metrics (with clear statistical basis and confidence intervals), and actionable content "
        "scorecards. Provide executive-level improvement suggestions, robust A/B test methodologies, "
        "and data-backed budget reallocation advice. Phase 1 predictions should be treated as "
        "sophisticated heuristic estimates. Return output that exactly matches the "
        "AnalyticsAgentOutput schema. No markdown, preamble, or explanation."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate analytics from campaign context and update context."""
        competitor_analyses = []
        if context.competitors and context.competitors.competitors:
            for comp in context.competitors.competitors:
                competitor_analyses.append(
                    CompetitorAnalysis(
                        name=comp.name,
                        strengths=comp.strengths,
                        weaknesses=comp.weaknesses,
                        positioning=comp.messaging_analysis,
                    )
                )

        synthetic_research = ResearchAgentOutput(
            audience_personas=[],
            competitor_analyses=competitor_analyses,
            trending_topics=[],
            channel_benchmarks=[],
            audience_language="English",
            key_insights=[],
            market_size_estimate=PositiveFloat(1.0),
            search_queries_used=[],
        )

        agent_input = AnalyticsAgentInput(
            campaign=context.brief,
            strategy=context.strategy,
            research=synthetic_research,
            content=context.content,
        )
        validated_input = self.validate_input(agent_input)
        output = await self.call_llm(
            prompt=self.build_prompt(),
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            strategy_json=json.dumps(validated_input.strategy.model_dump(mode="json"), indent=2),
            research_json=json.dumps(validated_input.research.model_dump(mode="json"), indent=2),
            content_json=json.dumps(validated_input.content.model_dump(mode="json"), indent=2),
            campaign_id=context.campaign_id,
        )

        # ML Model prediction step
        try:
            from ..services.model_loader import ModelLoader
            import numpy as np
            model = ModelLoader().load_model("research/models/analytics/analytics_model.pkl")
            if model is not None:
                # [age, balance, duration, campaign, previous, bal_dur_ratio, campaign_efficiency]
                feat = np.array([[45, 10000.0, 300, 2, 1, 10000.0/301.0, 300*2]])
                roas_val = float(model.predict(feat)[0])
                logger.info("Analytics ML Model ROAS prediction: %s", roas_val)
            else:
                logger.info("Analytics ML Model files loaded as None. Skipping prediction.")
        except Exception as e:
            logger.warning("Failed analytics model prediction: %s", str(e))

        context.analytics = output
        return context


    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for analytics generation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Analyze this Phase 1 campaign package.\n\n"
                    "Campaign:\n{campaign_json}\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Research:\n{research_json}\n\n"
                    "Content:\n{content_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )

    @staticmethod
    def passes_quality_gate(output: AnalyticsAgentOutput, threshold: float = 70.0) -> bool:
        """Return ``True`` when the campaign health score meets the threshold."""
        return output.health_score.overall >= threshold

    @staticmethod
    def extract_optimization_recommendations(output: AnalyticsAgentOutput) -> list[str]:
        """Extract high/medium-priority improvement suggestions as plain strings."""
        return [
            s.suggestion
            for s in output.improvement_suggestions
            if s.priority.value in ("high", "medium")
        ]
