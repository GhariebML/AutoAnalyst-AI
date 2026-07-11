import asyncio
import pytest
from adpilot.agents.publishing_agent import PublishingAgent
from adpilot.core.exceptions import AgentOutputError
from adpilot.schemas.agent_schemas import (
    CampaignInput,
    CampaignGoal,
    MarketingChannel,
    ToneOfVoice,
    ContentAgentOutput,
    StrategyAgentOutput,
    FunnelStageStrategy,
    CampaignContext,
)


def test_publishing_agent_run_parses_valid_llm_response(monkeypatch):
    agent = PublishingAgent()

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

    content = ContentAgentOutput(
        ads=[],
        email_sequences=[],
        social_posts=[],
        blog_outlines=[],
        cta_variants=[],
        content_calendar_note="No notes",
    )

    valid_payload = {
        "headlines": ["Headline 1", "Headline 2"],
        "ctas": ["Try for free", "Book a call"],
        "targeting_criteria": ["Location: US", "Industry: SaaS"],
        "budget_allocation": {"linkedin": 500.0, "email": 500.0},
        "utm_parameters": {
            "utm_source": "linkedin",
            "utm_medium": "cpc",
            "utm_campaign": "brand_launch",
        },
        "campaign_metadata": {"environment": "production"},
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(valid_payload)

    monkeypatch.setattr("adpilot.agents.publishing_agent.PublishingAgent.call_llm", fake_call_llm)

    context = CampaignContext(
        campaign_id="test-campaign",
        brief=campaign,
        content=content,
        strategy=strategy,
    )
    result_context = asyncio.run(agent.run(context))
    result = result_context.publishing

    assert result.headlines == ["Headline 1", "Headline 2"]
    assert result.utm_parameters.utm_source == "linkedin"
    assert result.campaign_metadata == {"environment": "production"}


def test_publishing_agent_run_rejects_invalid_llm_output(monkeypatch):
    agent = PublishingAgent()

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

    content = ContentAgentOutput(
        ads=[],
        email_sequences=[],
        social_posts=[],
        blog_outlines=[],
        cta_variants=[],
        content_calendar_note="No notes",
    )

    invalid_payload = {
        "headlines": ["Headline 1"],
        # Missing other fields
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(invalid_payload)

    monkeypatch.setattr("adpilot.agents.publishing_agent.PublishingAgent.call_llm", fake_call_llm)

    context = CampaignContext(
        campaign_id="test-campaign",
        brief=campaign,
        content=content,
        strategy=strategy,
    )
    with pytest.raises(AgentOutputError):
        asyncio.run(agent.run(context))
