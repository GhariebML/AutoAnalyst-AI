import asyncio
import pytest
from adpilot.agents.creative_agent import CreativeAgent
from adpilot.core.exceptions import AgentOutputError
from adpilot.schemas.agent_schemas import (
    CampaignInput,
    CampaignGoal,
    MarketingChannel,
    ToneOfVoice,
    StrategyAgentOutput,
    FunnelStageStrategy,
    CampaignContext,
)


def test_creative_agent_run_parses_valid_llm_response(monkeypatch):
    agent = CreativeAgent()

    campaign = CampaignInput(
        business_name="Test Business",
        product_description="Test Product Description",
        target_market="Test Target Market",
        budget_usd=1000.0,
        goals=[CampaignGoal.brand_awareness],
        channels=[MarketingChannel.linkedin],
        tone_of_voice=ToneOfVoice.professional,
        competitors=["Competitor X"],
        campaign_duration_days=30,
    )

    strategy = StrategyAgentOutput(
        positioning_statement="Lead with product quality",
        usp="High-conversion creative",
        elevator_pitch="A campaign designed to convert.",
        tone_of_voice=ToneOfVoice.friendly,
        brand_voice_guidelines="Friendly tone",
        primary_channels=[MarketingChannel.email],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage="awareness", budget_allocation_percent=50, key_messages=["Intro"]),
            FunnelStageStrategy(stage="conversion", budget_allocation_percent=50, key_messages=["Buy"]),
        ],
        target_persona_summary="Busy professionals",
        key_differentiators=["Fast turnaround"],
        risks_and_considerations=["tone Consistency"],
    )

    valid_payload = {
        "creative_brief": "Creative brief summary text",
        "design_direction": "Modern minimalist",
        "color_palette": ["#1A1A1A", "#FFFFFF"],
        "image_prompts": ["Sleek dashboard prompt"],
        "video_prompts": ["Fast paced UI transition video prompt"],
        "thumbnail_prompts": ["Static image thumbnail prompt"],
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(valid_payload)

    monkeypatch.setattr("adpilot.agents.creative_agent.CreativeAgent.call_llm", fake_call_llm)

    context = CampaignContext(campaign_id="test-campaign", brief=campaign, strategy=strategy)
    result_context = asyncio.run(agent.run(context))
    result = result_context.creative

    assert result.creative_brief == "Creative brief summary text"
    assert result.color_palette == ["#1A1A1A", "#FFFFFF"]
    assert result.image_prompts == ["Sleek dashboard prompt"]


def test_creative_agent_run_rejects_invalid_llm_output(monkeypatch):
    agent = CreativeAgent()

    campaign = CampaignInput(
        business_name="Test Business",
        product_description="Test Product Description",
        target_market="Test Target Market",
        budget_usd=1000.0,
        goals=[CampaignGoal.brand_awareness],
        channels=[MarketingChannel.linkedin],
        tone_of_voice=ToneOfVoice.professional,
        competitors=["Competitor X"],
        campaign_duration_days=30,
    )

    strategy = StrategyAgentOutput(
        positioning_statement="Lead with product quality",
        usp="High-conversion creative",
        elevator_pitch="A campaign designed to convert.",
        tone_of_voice=ToneOfVoice.friendly,
        brand_voice_guidelines="Friendly tone",
        primary_channels=[MarketingChannel.email],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage="awareness", budget_allocation_percent=50, key_messages=["Intro"]),
            FunnelStageStrategy(stage="conversion", budget_allocation_percent=50, key_messages=["Buy"]),
        ],
        target_persona_summary="Busy professionals",
        key_differentiators=["Fast turnaround"],
        risks_and_considerations=["tone Consistency"],
    )

    invalid_payload = {
        "creative_brief": "Creative brief summary text",
        # Missing required lists to force validation failure.
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(invalid_payload)

    monkeypatch.setattr("adpilot.agents.creative_agent.CreativeAgent.call_llm", fake_call_llm)

    with pytest.raises(AgentOutputError):
        context = CampaignContext(campaign_id="test-campaign", brief=campaign, strategy=strategy)
        asyncio.run(agent.run(context))
