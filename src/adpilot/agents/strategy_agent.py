"""LangChain-backed strategic planning agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import CampaignContext, StrategyAgentInput, StrategyAgentOutput


class StrategyAgent(BaseAgent[StrategyAgentInput, StrategyAgentOutput]):
    """Generate a validated campaign strategy using LangChain structured output."""

    name = "strategy_agent"
    input_model = StrategyAgentInput
    output_model = StrategyAgentOutput

    system_prompt = (
        "You are AdPilot's Principal Marketing Strategist. Your objective is to formulate a "
        "highly professional, data-driven, and enterprise-grade campaign strategy. Leverage "
        "industry best practices, ensure precise budget allocations (summing exactly to 100%), "
        "and maintain a polished, authoritative tone. Ensure the strategy is actionable, "
        "measurable, and perfectly aligned with the provided campaign brief. Output must "
        "exactly match the StrategyAgentOutput schema without any markdown, preamble, or fluff."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate a strategy from campaign input and update context."""
        agent_input = StrategyAgentInput(campaign=context.brief)
        validated_input = self.validate_input(agent_input)
        prompt = self.build_prompt()
        output = await self.call_llm(
            prompt=prompt,
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            campaign_id=context.campaign_id,
        )
        context.strategy = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for strategy generation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt or ""),
                (
                    "human",
                    "Create a complete campaign strategy for this campaign brief:\n\n"
                    "{campaign_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
