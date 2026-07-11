"""LangChain-backed campaign manager agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import (
    CampaignContext, CampaignManagerInput, CampaignManagerOutput, ResearchAgentOutput, CompetitorAnalysis,
    PositiveFloat, DesignBrief, GeneratedVisual, ImageDimensions, DesignAgentOutput
)


class CampaignManagerAgent(BaseAgent[CampaignManagerInput, CampaignManagerOutput]):
    """Assemble validated media plan, schedule, ad sets, tests, and KPI targets."""

    name = "campaign_manager_agent"
    input_model = CampaignManagerInput
    output_model = CampaignManagerOutput

    system_prompt = (
        "You are AdPilot's Senior Media Director and Campaign Manager. Your objective is to "
        "orchestrate a flawless, enterprise-ready Phase 1 media plan by synthesizing inputs "
        "from strategy, research, content, analytics, and design. Formulate highly optimized "
        "channel budget allocations (summing exactly to 100%), robust weekly execution schedules, "
        "precise ad sets, statistically rigorous A/B test plans, and ambitious yet realistic KPI "
        "targets. Do not invoke live ad platform APIs; construct this as an authoritative, "
        "deployment-ready architectural blueprint. Return output that exactly matches the "
        "CampaignManagerOutput schema without markdown, preamble, or explanation."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate the final campaign management plan and update context."""
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

        design_briefs = []
        generated_visuals = []
        if context.creative:
            for prompt in context.creative.image_prompts:
                db = DesignBrief(
                    dalle_prompt=prompt,
                    negative_prompt="",
                    concept=context.creative.creative_brief,
                    rationale=context.creative.design_direction,
                    image_dimensions=ImageDimensions(width=1024, height=1024),
                    style="minimal",
                    format="png",
                )
                design_briefs.append(db)
                generated_visuals.append(
                    GeneratedVisual(
                        image_url="https://placehold.co/1024x1024.png",
                        brief=db,
                    )
                )

        synthetic_design = DesignAgentOutput(
            design_briefs=design_briefs,
            generated_visuals=generated_visuals,
            brand_style_guide_snippet=context.creative.design_direction if context.creative else "",
        )

        agent_input = CampaignManagerInput(
            campaign=context.brief,
            strategy=context.strategy,
            research=synthetic_research,
            content=context.content,
            analytics=context.analytics,
            design=synthetic_design,
        )
        validated_input = self.validate_input(agent_input)
        output = await self.call_llm(
            prompt=self.build_prompt(),
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            strategy_json=json.dumps(validated_input.strategy.model_dump(mode="json"), indent=2),
            research_json=json.dumps(validated_input.research.model_dump(mode="json"), indent=2),
            content_json=json.dumps(validated_input.content.model_dump(mode="json"), indent=2),
            analytics_json=json.dumps(validated_input.analytics.model_dump(mode="json"), indent=2),
            design_json=json.dumps(validated_input.design.model_dump(mode="json"), indent=2),
            campaign_id=context.campaign_id,
        )
        context.campaign_manager = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for campaign management."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Create the final Phase 1 campaign management plan.\n\n"
                    "Campaign:\n{campaign_json}\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Research:\n{research_json}\n\n"
                    "Content:\n{content_json}\n\n"
                    "Analytics:\n{analytics_json}\n\n"
                    "Design:\n{design_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
