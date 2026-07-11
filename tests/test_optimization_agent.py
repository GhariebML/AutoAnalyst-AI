import asyncio
import pytest
from adpilot.agents.optimization_agent import OptimizationAgent
from adpilot.core.exceptions import AgentOutputError
from adpilot.schemas.agent_schemas import (
    CampaignInput,
    CampaignGoal,
    MarketingChannel,
    ToneOfVoice,
    AnalyticsAgentOutput,
    CampaignHealthScore,
    SuggestionPriority,
    CampaignContext,
)


def test_optimization_agent_run_parses_valid_llm_response(monkeypatch):
    agent = OptimizationAgent()

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

    analytics = AnalyticsAgentOutput(
        health_score=CampaignHealthScore(overall=85.0, stage_scores={"awareness": 85.0}),
        predicted_metrics=[],
        content_scorecards=[],
        improvement_suggestions=[],
        ab_test_recommendations=[],
        budget_reallocation_advice="No budget changes",
        executive_summary="Summary text",
        next_review_checkpoint="1 week",
    )

    valid_payload = {
        "optimization_actions": [
            {
                "condition": "low_ctr",
                "metric": "ctr",
                "current_value": 1.2,
                "target_value": 3.0,
                "recommendation": "Rewrite headlines",
                "priority": "high",
                "action_steps": ["Improve readability", "A/B test different headers"],
            }
        ],
        "budget_reallocation_plan": "Reallocate 10% to email",
        "performance_forecast": "Expected CTR increase to 3.5%",
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(valid_payload)

    monkeypatch.setattr("adpilot.agents.optimization_agent.OptimizationAgent.call_llm", fake_call_llm)

    context = CampaignContext(campaign_id="test-campaign", brief=campaign, analytics=analytics)
    result_context = asyncio.run(agent.run(context))
    result = result_context.optimization

    assert result.optimization_actions[0].condition == "low_ctr"
    assert result.optimization_actions[0].priority == SuggestionPriority.high
    assert result.budget_reallocation_plan == "Reallocate 10% to email"


def test_optimization_agent_run_rejects_invalid_llm_output(monkeypatch):
    agent = OptimizationAgent()

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

    analytics = AnalyticsAgentOutput(
        health_score=CampaignHealthScore(overall=85.0, stage_scores={"awareness": 85.0}),
        predicted_metrics=[],
        content_scorecards=[],
        improvement_suggestions=[],
        ab_test_recommendations=[],
        budget_reallocation_advice="No budget changes",
        executive_summary="Summary text",
        next_review_checkpoint="1 week",
    )

    invalid_payload = {
        "optimization_actions": [
            {
                "condition": "low_ctr"
                # Missing fields
            }
        ],
        "budget_reallocation_plan": "Reallocate 10% to email",
        "performance_forecast": "Expected CTR increase to 3.5%",
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(invalid_payload)

    monkeypatch.setattr("adpilot.agents.optimization_agent.OptimizationAgent.call_llm", fake_call_llm)

    with pytest.raises(AgentOutputError):
        context = CampaignContext(campaign_id="test-campaign", brief=campaign, analytics=analytics)
        asyncio.run(agent.run(context))
