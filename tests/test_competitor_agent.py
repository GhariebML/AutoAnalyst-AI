import asyncio
import pytest
from adpilot.agents.competitor_agent import CompetitorAgent
from adpilot.core.exceptions import AgentOutputError
from adpilot.schemas.agent_schemas import (
    CampaignInput,
    CampaignGoal,
    MarketingChannel,
    ToneOfVoice,
    CampaignContext,
)


def test_competitor_agent_run_parses_valid_llm_response(monkeypatch):
    agent = CompetitorAgent()

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
        "competitors": [
            {
                "name": "Competitor X",
                "strengths": ["Market dominance"],
                "weaknesses": ["Slow turnaround"],
                "opportunities": ["Leverage AI integration"],
                "threats": ["New startups entering"],
                "messaging_analysis": "Focuses on safety and trust",
                "pricing_comparison": "Premium pricing model",
                "market_gaps": ["No self-serve option"],
            }
        ],
        "opportunities": ["Introduce cheaper starter tier"],
        "threats": ["High advertising cost"],
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(valid_payload)

    monkeypatch.setattr("adpilot.agents.competitor_agent.CompetitorAgent.call_llm", fake_call_llm)

    context = CampaignContext(campaign_id="test-campaign", brief=campaign)
    result_context = asyncio.run(agent.run(context))
    result = result_context.competitors

    assert result.competitors[0].name == "Competitor X"
    assert result.competitors[0].strengths == ["Market dominance"]
    assert result.opportunities == ["Introduce cheaper starter tier"]


def test_competitor_agent_run_rejects_invalid_llm_output(monkeypatch):
    agent = CompetitorAgent()

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
        "competitors": [
            {
                "name": "Competitor X"
                # Missing other details
            }
        ],
        "opportunities": [],
        "threats": [],
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(invalid_payload)

    monkeypatch.setattr("adpilot.agents.competitor_agent.CompetitorAgent.call_llm", fake_call_llm)

    context = CampaignContext(campaign_id="test-campaign", brief=campaign)
    with pytest.raises(AgentOutputError):
        asyncio.run(agent.run(context))
