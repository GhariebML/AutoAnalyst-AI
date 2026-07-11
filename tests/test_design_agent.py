"""Design agent validation and runtime tests."""

import asyncio
import pytest

from adpilot.agents.design_agent import DesignAgent
from adpilot.schemas.agent_schemas import (
    DesignBrief,
    FunnelStage,
    ImageDimensions,
    MarketingChannel,
    StrategyAgentOutput,
    FunnelStageStrategy,
    CampaignContext,
    CampaignInput,
    CampaignGoal,
    ToneOfVoice,
    ContentAgentOutput,
)


def test_design_brief_invalid_format_coerced_to_png():
    brief = DesignBrief(
        dalle_prompt="An image prompt",
        negative_prompt="Avoid low quality",
        concept="Concept",
        rationale="Rationale",
        image_dimensions=ImageDimensions(width=1200, height=628),
        style="illustration",
        format="bmp",
    )
    assert brief.format == "png"


def test_generated_visual_image_url_can_be_placeholder():
    brief = DesignBrief(
        dalle_prompt="A clean brand image",
        negative_prompt="No blur",
        concept="Placeholder concept",
        rationale="Placeholder rationale",
        image_dimensions=ImageDimensions(width=1200, height=628),
        style="photorealistic",
        format="png",
    )
    visual = DesignAgent()._build_placeholder_image_url(brief, 1)

    assert visual.endswith(".png")
    assert visual.startswith("https://")


def test_design_agent_run_generates_valid_output(monkeypatch):
    strategy = StrategyAgentOutput(
        positioning_statement="A bold campaign for modern consumers.",
        usp="Fast, premium quality product delivery.",
        elevator_pitch="A smart choice for busy shoppers.",
        tone_of_voice="friendly",
        brand_voice_guidelines="Use warm language, simple visuals, and optimistic messaging.",
        primary_channels=[MarketingChannel.instagram],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage=FunnelStage.awareness, budget_allocation_percent=100, key_messages=[])
        ],
        target_persona_summary="Young professionals seeking convenience.",
        key_differentiators=["Fast delivery"],
        risks_and_considerations=["Need clear calls to action"],
    )

    content = {
        "ads": [
            {
                "headline": "Launch better in minutes",
                "body": "A compelling campaign creative that drives awareness.",
                "call_to_action": "Shop now",
                "funnel_stage": "awareness",
                "format": "image",
                "hashtags": ["#launch"],
            }
        ],
        "email_sequences": [
            {
                "sequence_name": "Welcome series",
                "emails": [
                    {"subject": "Welcome", "body": "Hello", "day_offset": 0}
                ],
            }
        ],
        "social_posts": [
            {
                "platform": "instagram",
                "content": "A fresh launch post.",
                "hashtags": ["#fresh"],
            }
        ],
        "blog_outlines": [{"title": "Launch guide", "sections": ["Intro"]}],
        "cta_variants": [{"text": "Shop now"}],
        "content_calendar_note": "Post on launch day.",
    }

    mock_response = {
        "design_briefs": [
            {
                "dalle_prompt": "A modern product shot",
                "negative_prompt": "No blur",
                "concept": "Modernity",
                "rationale": "Appeals to target persona",
                "image_dimensions": {"width": 1200, "height": 628},
                "style": "photorealistic",
                "format": "png"
            }
        ],
            "generated_visuals": [
                {
                    "image_url": "https://placehold.co/1200x628.png",
                    "brief": {
                        "dalle_prompt": "A modern product shot",
                        "negative_prompt": "No blur",
                        "concept": "Modernity",
                        "rationale": "Appeals to target persona",
                        "image_dimensions": {"width": 1200, "height": 628},
                        "style": "photorealistic",
                        "format": "png"
                    },
                    "generation_error": None
                }
            ],
            "brand_style_guide_snippet": "Use clean typography.",
            "generation_errors": []
        }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(mock_response)

    monkeypatch.setattr("adpilot.agents.design_agent.DesignAgent.call_llm", fake_call_llm)

    campaign = CampaignInput(
        business_name="Test Business",
        product_description="Test Product Description",
        target_market="Test Target Market",
        budget_usd=1000.0,
        goals=[CampaignGoal.brand_awareness],
        channels=[MarketingChannel.instagram],
        tone_of_voice=ToneOfVoice.friendly,
        competitors=["Competitor X"],
        campaign_duration_days=30,
        brand_colors=["#1A1A1A", "#FFFFFF"],
    )
    context = CampaignContext(
        campaign_id="test-campaign",
        brief=campaign,
        strategy=strategy,
        content=ContentAgentOutput.model_validate(content),
    )
    agent = DesignAgent()
    result_context = asyncio.run(agent.run(context))

    assert result_context.creative is not None
    assert result_context.creative.creative_brief == "Modernity"
    assert result_context.creative.design_direction == "Use clean typography."
    assert result_context.creative.color_palette == ["#1A1A1A", "#FFFFFF"]
    assert result_context.creative.image_prompts == ["A modern product shot"]
