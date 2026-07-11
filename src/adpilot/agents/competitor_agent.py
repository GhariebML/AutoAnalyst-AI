"""Competitor analysis agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import CampaignContext, CompetitorAgentInput, CompetitorLandscape


class CompetitorAgent(BaseAgent[CompetitorAgentInput, CompetitorLandscape]):
    """Analyze competitors and identify market gaps using LangChain."""

    name = "competitor_agent"
    input_model = CompetitorAgentInput
    output_model = CompetitorLandscape

    system_prompt = (
        "You are AdPilot's Lead Competitive Intelligence Analyst. Your objective is to perform a "
        "rigorous competitive landscape analysis. Identify primary competitors, detail their strengths "
        "and weaknesses, formulate SWOT profiles, analyze their messaging tactics, compare pricing models, "
        "and discover viable market gaps/opportunities. Make sure the insights are strategic and "
        "actionable for the campaign. Return output that exactly matches the CompetitorLandscape schema "
        "without markdown, preamble, or explanation."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate competitor analysis from campaign, strategy, and audience data."""
        agent_input = CompetitorAgentInput(campaign=context.brief)
        validated_input = self.validate_input(agent_input)
        prompt = self.build_prompt()
        output = await self.call_llm(
            prompt=prompt,
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            strategy_json=json.dumps(context.strategy.model_dump(mode="json") if context.strategy else {}, indent=2),
            audience_json=json.dumps(context.audience.model_dump(mode="json") if context.audience else {}, indent=2),
            campaign_id=context.campaign_id,
        )
        context.competitors = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for competitor research."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Conduct a competitive market assessment for this campaign:\n\n"
                    "Campaign Brief:\n{campaign_json}\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Target Persona Focus:\n{audience_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
