import asyncio
import pytest
from adpilot.agents.audience_agent import AudienceAgent
from adpilot.core.exceptions import AgentOutputError
from adpilot.schemas.agent_schemas import (
    CampaignInput,
    CampaignGoal,
    MarketingChannel,
    ToneOfVoice,
    CampaignContext,
)


def test_audience_agent_run_parses_valid_llm_response(monkeypatch):
    agent = AudienceAgent()

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

    valid_payload = {
        "primary_persona": {
            "name": "Jane Doe",
            "demographics": "Female, 30-45",
            "psychographics": "Values efficiency and productivity",
            "pain_points": ["Lack of time"],
            "goals": ["Automate workflows"],
            "objections": ["Expensive pricing"],
            "buying_triggers": ["Limited-time discount"],
        },
        "secondary_personas": [],
        "pain_points": ["Time waste"],
        "motivations": ["Growth"],
        "objections": ["Security"],
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(valid_payload)

    monkeypatch.setattr("adpilot.agents.audience_agent.AudienceAgent.call_llm", fake_call_llm)

    context = CampaignContext(campaign_id="test-campaign", brief=campaign)
    result_context = asyncio.run(agent.run(context))
    result = result_context.audience

    assert result.primary_persona.name == "Jane Doe"
    assert result.primary_persona.pain_points == ["Lack of time"]
    assert result.pain_points == ["Time waste"]


def test_audience_agent_run_rejects_invalid_llm_output(monkeypatch):
    agent = AudienceAgent()

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

    invalid_payload = {
        "primary_persona": {
            "name": "Jane Doe",
            # Missing demographic, psychographics and other lists to trigger validation error.
        },
        "secondary_personas": [],
        "pain_points": [],
        "motivations": [],
        "objections": [],
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(invalid_payload)

    monkeypatch.setattr("adpilot.agents.audience_agent.AudienceAgent.call_llm", fake_call_llm)

    context = CampaignContext(campaign_id="test-campaign", brief=campaign)
    with pytest.raises(AgentOutputError):
        asyncio.run(agent.run(context))
