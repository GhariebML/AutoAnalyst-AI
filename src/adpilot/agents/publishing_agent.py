"""Publishing preparation agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import CampaignContext, PublishingAgentInput, PublishingPackage


class PublishingAgent(BaseAgent[PublishingAgentInput, PublishingPackage]):
    """Prepare campaign package for deployment and publishing using LangChain."""

    name = "publishing_agent"
    input_model = PublishingAgentInput
    output_model = PublishingPackage

    system_prompt = (
        "You are AdPilot's Campaign Operations and Publishing Manager. Your objective is to compile "
        "and package the generated strategy, target segments, and creatives into a production-ready "
        "deployment model. Compile all headlines and CTAs, specify targeting criteria, allocate budget "
        "by marketing channel, generate structured UTM parameters for URL tracking, and provide "
        "campaign metadata. Return output that exactly matches the PublishingPackage schema."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Compile campaign details into a publishing package and update context."""
        agent_input = PublishingAgentInput(campaign=context.brief, content=context.content, strategy=context.strategy)
        validated_input = self.validate_input(agent_input)
        prompt = self.build_prompt()
        output = await self.call_llm(
            prompt=prompt,
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            content_json=json.dumps(validated_input.content.model_dump(mode="json") if validated_input.content else {}, indent=2),
            strategy_json=json.dumps(validated_input.strategy.model_dump(mode="json") if validated_input.strategy else {}, indent=2),
            campaign_id=context.campaign_id,
        )
        context.publishing = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for publishing generation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Compile and package this campaign for publishing:\n\n"
                    "Campaign Brief:\n{campaign_json}\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Content:\n{content_json}\n\n"
                    "Return only structured data that satisfies the required Pydantic output model.",
                ),
            ]
        )
