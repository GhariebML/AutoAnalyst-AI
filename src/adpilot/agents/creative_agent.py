"""Creative brief and visual specification agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import CampaignContext, CreativeAgentInput, CreativeOutput


class CreativeAgent(BaseAgent[CreativeAgentInput, CreativeOutput]):
    """Generate professional creative briefs and visual specifications using LangChain."""

    name = "creative_agent"
    input_model = CreativeAgentInput
    output_model = CreativeOutput

    system_prompt = (
        "You are AdPilot's Executive Creative Director. Formulate a comprehensive creative brief, "
        "set design directions, establish a curated color palette (with precise hex codes), and "
        "generate highly detailed text prompts for image generation (DALL-E), video scripts/prompts, "
        "and video thumbnails. Ensure the visual aesthetic is premium, high-impact, and directly "
        "complements the campaign strategy. Do not call image generation APIs; focus on descriptive "
        "prompt generation. Return output that exactly matches the CreativeOutput schema."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate creative briefs and prompts from campaign brief and strategy and update context."""
        agent_input = CreativeAgentInput(campaign=context.brief, strategy=context.strategy)
        validated_input = self.validate_input(agent_input)
        prompt = self.build_prompt()
        output = await self.call_llm(
            prompt=prompt,
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            strategy_json=json.dumps(validated_input.strategy.model_dump(mode="json") if validated_input.strategy else {}, indent=2),
            campaign_id=context.campaign_id,
        )
        context.creative = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for creative brief formulation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Develop a creative direction plan for this campaign:\n\n"
                    "Campaign Brief:\n{campaign_json}\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
