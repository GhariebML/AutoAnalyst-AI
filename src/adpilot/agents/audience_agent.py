"""Audience analysis agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import AudienceAgentInput, AudienceOutput, CampaignContext


class AudienceAgent(BaseAgent[AudienceAgentInput, AudienceOutput]):
    """Formulate Ideal Customer Profiles and target personas using LangChain."""

    name = "audience_agent"
    input_model = AudienceAgentInput
    output_model = AudienceOutput

    system_prompt = (
        "You are AdPilot's Principal Audience Strategist and Buyer Persona Expert. Your objective is "
        "to define highly detailed, realistic, and actionable Ideal Customer Profiles (ICPs) and "
        "buyer personas based on the campaign brief. For every persona, detail their demographics, "
        "psychographics, core pain points, primary goals, common objections, and key buying triggers. "
        "Ensure all details are brand-relevant and directly support marketing strategy. Return output "
        "that exactly matches the AudienceOutput schema without markdown, preamble, or explanation."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate buyer personas and audience segmentation from campaign brief and strategy."""
        agent_input = AudienceAgentInput(campaign=context.brief)
        validated_input = self.validate_input(agent_input)
        prompt = self.build_prompt()
        output = await self.call_llm(
            prompt=prompt,
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            strategy_json=json.dumps(context.strategy.model_dump(mode="json") if context.strategy else {}, indent=2),
            campaign_id=context.campaign_id,
        )
        context.audience = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for audience research."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Analyze the campaign brief and strategy to define target personas:\n\n"
                    "Campaign Brief:\n{campaign_json}\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
