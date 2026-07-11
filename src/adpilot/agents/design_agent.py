"""LangChain-backed design brief and visual specification agent."""

from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import CampaignContext, DesignAgentInput, DesignAgentOutput, CreativeOutput, DesignBrief


class DesignAgent(BaseAgent[DesignAgentInput, DesignAgentOutput]):
    """Create validated design briefs and Phase 1 visual specifications."""

    name = "design_agent"
    input_model = DesignAgentInput
    output_model = DesignAgentOutput

    system_prompt = (
        "You are AdPilot's Creative Director and Lead Visual Strategist. Your objective is to "
        "produce world-class, premium visual specifications and generation prompts.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Generate impeccably detailed, highly descriptive, and extensive visual generative prompts "
        "so that the user sees profound artistic direction when reviewing the brief.\n"
        "2. Ensure comprehensive brand style guides and sophisticated visual assets synchronize "
        "perfectly with the strategy, target personas, and copy.\n"
        "3. Use safe placeholder image URLs (like https://placehold.co/[width]x[height].png) when required.\n"
        "4. Output must exactly match the DesignAgentOutput schema with exceptional attention to "
        "aesthetic detail and brand consistency.\n"
        "5. Do not include markdown, preamble, or explanation."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate design briefs and Phase 1 visual records."""
        agent_input = DesignAgentInput(
            strategy=context.strategy,
            content=context.content,
            campaign_id=context.campaign_id,
        )
        validated_input = self.validate_input(agent_input)
        output = await self.call_llm(
            prompt=self.build_prompt(),
            strategy_json=json.dumps(validated_input.strategy.model_dump(mode="json"), indent=2),
            content_json=json.dumps(validated_input.content.model_dump(mode="json"), indent=2),
            campaign_id=validated_input.campaign_id or "phase1-local",
        )
        context.creative = CreativeOutput(
            creative_brief=output.design_briefs[0].concept if output.design_briefs else "Design brief concept blueprint.",
            design_direction=output.brand_style_guide_snippet,
            color_palette=context.brief.brand_colors or ["#1A1A1A", "#FFFFFF"],
            image_prompts=[b.dalle_prompt for b in output.design_briefs],
            video_prompts=[],
            thumbnail_prompts=[],
        )
        context.design = output
        return context

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for design generation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Create design outputs for campaign_id {campaign_id}.\n\n"
                    "Strategy:\n{strategy_json}\n\n"
                    "Content:\n{content_json}\n\n"
                    "For generated_visuals.image_url, use safe placeholder URLs such as "
                    "https://placehold.co/[width]x[height].png when no real image generation "
                    "has occurred. Return only structured data that satisfies the required "
                    "Pydantic output model.",
                ),
            ]
        )

    def _build_placeholder_image_url(self, brief: DesignBrief, seed: int = 1) -> str:
        """Build a safe deterministic placeholder URL for Phase 1 visuals."""
        width = brief.image_dimensions.width
        height = brief.image_dimensions.height
        return f"https://placehold.co/{width}x{height}.{brief.format}"
