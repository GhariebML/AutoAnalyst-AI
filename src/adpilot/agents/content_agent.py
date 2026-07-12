"""LangChain-backed content creation agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import (
    CampaignContext, ContentAgentInput, ContentAgentOutput, ResearchAgentOutput, CompetitorAnalysis, PositiveFloat
)


class ContentAgent(BaseAgent[ContentAgentInput, ContentAgentOutput]):
    """Generate validated campaign content using structured output."""

    name = "content_agent"
    input_model = ContentAgentInput
    output_model = ContentAgentOutput

    system_prompt = (
        "You are AdPilot's Senior Performance Content Director. Your objective is to craft "
        "premium, high-converting, and highly detailed marketing copy grounded firmly in the "
        "provided strategy and research data.\n\n"
        "CRITICAL INSTRUCTIONS FOR COPY SIZE AND PROFESSIONALISM:\n"
        "1. Write LONG, multi-paragraph, incredibly detailed body copy for all ads and emails. "
        "Do not write short or generic summaries. Provide rich, persuasive narratives.\n"
        "2. Ensure the tone is extremely sophisticated, brand-aligned, and appropriate for top-tier "
        "enterprise audiences.\n"
        "3. For ad creatives, provide extensive detail so that when users expand the view, they "
        "read a deep, professional breakdown of the value proposition.\n"
        "4. Never use placeholders like 'your tagline here', 'TBD', or 'example CTA'.\n"
        "5. Return output that exactly matches the ContentAgentOutput schema without markdown or preamble."
    )

    async def run(
        self,
        context: CampaignContext,
        optimization_context: list[str] | None = None,
    ) -> CampaignContext:
        """Generate content from campaign context and update context."""
        # Extract audience & competitor data and adapt to ContentAgentInput for backward compatibility
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

        agent_input = ContentAgentInput(strategy=context.strategy, research=synthetic_research)
        validated_input = self.validate_input(agent_input)
        retry_guidance = "\n".join(f"- {item}" for item in optimization_context or [])
        output = await self.call_llm(
            prompt=self.build_prompt(),
            strategy_json=json.dumps(validated_input.strategy.model_dump(mode="json"), indent=2),
            research_json=json.dumps(validated_input.research.model_dump(mode="json"), indent=2),
            retry_guidance=retry_guidance or "None.",
            campaign_id=context.campaign_id,
        )
        context.content = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for content generation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Generate campaign content from these inputs.\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Research:\n{research_json}\n\n"
                    "Optimization guidance from a prior analytics pass, if any:\n"
                    "{retry_guidance}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
