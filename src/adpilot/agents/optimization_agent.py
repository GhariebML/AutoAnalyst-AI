"""Optimization recommendations agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import CampaignContext, OptimizationAgentInput, OptimizationOutput


class OptimizationAgent(BaseAgent[OptimizationAgentInput, OptimizationOutput]):
    """Analyze campaign health metrics and generate structured optimization recommendations."""

    name = "optimization_agent"
    input_model = OptimizationAgentInput
    output_model = OptimizationOutput

    system_prompt = (
        "You are AdPilot's Marketing Optimization Architect. Analyze the campaign inputs and "
        "the analytics forecasts. Formulate clear, structured optimization actions based on "
        "standard performance triggers (e.g., if CTR is low, suggest improving headline/creative/audience; "
        "if CPA is high, suggest reducing budget/pausing adsets/duplicating winners). Provide a "
        "reallocation plan for budgets and a predictive performance forecast. Return output that "
        "exactly matches the OptimizationOutput schema without markdown, preamble, or explanation."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate optimization recommendations from campaign and analytics data and update context."""
        agent_input = OptimizationAgentInput(campaign=context.brief, analytics=context.analytics)
        validated_input = self.validate_input(agent_input)
        prompt = self.build_prompt()
        output = await self.call_llm(
            prompt=prompt,
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            analytics_json=json.dumps(validated_input.analytics.model_dump(mode="json") if validated_input.analytics else {}, indent=2),
            campaign_id=context.campaign_id,
        )
        context.optimization = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for optimization generation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Formulate optimization recommendations from this data:\n\n"
                    "Campaign Brief:\n{campaign_json}\n\n"
                    "Analytics Forecast:\n{analytics_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
