import pytest
from unittest.mock import AsyncMock

from adpilot.orchestrator.orchestrator import CampaignOrchestrator
from adpilot.schemas.agent_schemas import (
    CampaignInput,
    CampaignGoal,
    MarketingChannel,
    ToneOfVoice,
    StrategyAgentOutput,
    AudienceOutput,
    CompetitorLandscape,
    ContentAgentOutput,
    AnalyticsAgentOutput,
    OptimizationOutput,
    FunnelStageStrategy,
    Persona,
    Competitor,
    AdCopy,
    CampaignHealthScore,
    OptimizationAction,
    SuggestionPriority,
)

@pytest.mark.asyncio
async def test_campaign_orchestrator_full_pipeline(monkeypatch):
    # Setup mock payloads for each stage
    brief = CampaignInput(
        business_name="Test Enterprise",
        product_description="Enterprise CRM Software",
        target_market="B2B mid-market companies",
        budget_usd=50000.0,
        goals=[CampaignGoal.lead_generation],
        channels=[MarketingChannel.linkedin, MarketingChannel.email],
        tone_of_voice=ToneOfVoice.authoritative,
        competitors=["Salesforce", "HubSpot"],
        campaign_duration_days=90,
    )

    strategy_payload = StrategyAgentOutput(
        positioning_statement="Enterprise CRM simplified",
        usp="AI-driven deal insights",
        elevator_pitch="Close deals 50% faster.",
        tone_of_voice=ToneOfVoice.authoritative,
        brand_voice_guidelines="Authoritative and clear",
        primary_channels=[MarketingChannel.linkedin],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage="awareness", budget_allocation_percent=55, key_messages=["CRM simplicity"]),
            FunnelStageStrategy(stage="conversion", budget_allocation_percent=45, key_messages=["AI insights"]),
        ],
        target_persona_summary="Sales directors",
        key_differentiators=["AI auto-data entry"],
        risks_and_considerations=["Sales team onboarding"],
    )

    audience_payload = AudienceOutput(
        primary_persona=Persona(
            name="John Executive",
            demographics="Male, 40-55",
            psychographics="Hates manual CRM logging",
            pain_points=["Inaccurate forecast data"],
            goals=["Streamline sales process"],
            objections=["Implementation time"],
            buying_triggers=["New quarterly budget"],
        ),
        secondary_personas=[],
        pain_points=["CRM friction"],
        motivations=["Revenue visibility"],
        objections=["Setup cost"],
    )

    competitor_payload = CompetitorLandscape(
        competitors=[
            Competitor(
                name="HubSpot",
                strengths=["Great UX"],
                weaknesses=["Expensive for enterprise scale"],
                opportunities=[],
                threats=[],
                messaging_analysis="Focuses on growth",
                pricing_comparison="Freemium entry but high add-on costs",
                market_gaps=["Lacks deep custom security rules"],
            )
        ],
        opportunities=["Highlight simple setup vs HubSpot"],
        threats=["Market consolidation"],
    )

    content_payload = ContentAgentOutput(
        ads=[
            AdCopy(
                headline="Stop logging data manually",
                body="Let our AI CRM update deal states automatically.",
                call_to_action="Get a demo",
                funnel_stage="conversion",
                format="text",
                hashtags=[],
            )
        ],
        email_sequences=[],
        social_posts=[],
        blog_outlines=[],
        cta_variants=[],
        content_calendar_note="Post weekly",
    )

    analytics_payload = AnalyticsAgentOutput(
        health_score=CampaignHealthScore(overall=90.0, stage_scores={"awareness": 90.0}),
        predicted_metrics=[],
        content_scorecards=[],
        improvement_suggestions=[],
        ab_test_recommendations=[],
        budget_reallocation_advice="No budget changes",
        executive_summary="Excellent forecast metrics",
        next_review_checkpoint="Bi-weekly review",
    )

    optimization_payload = OptimizationOutput(
        optimization_actions=[
            OptimizationAction(
                condition="high_cpc",
                metric="cpc",
                current_value=4.5,
                target_value=3.0,
                recommendation="Refine LinkedIn targeting",
                priority=SuggestionPriority.medium,
                action_steps=["Target sales director title only"],
            )
        ],
        budget_reallocation_plan="Shift 5% from awareness to conversion",
        performance_forecast="Expected CTR increase to 3.5%",
    )

    # Monkeypatch call_llm for all agents
    monkeypatch.setattr("adpilot.agents.strategy_agent.StrategyAgent.call_llm", AsyncMock(return_value=strategy_payload))
    monkeypatch.setattr("adpilot.agents.audience_agent.AudienceAgent.call_llm", AsyncMock(return_value=audience_payload))
    monkeypatch.setattr("adpilot.agents.competitor_agent.CompetitorAgent.call_llm", AsyncMock(return_value=competitor_payload))
    monkeypatch.setattr("adpilot.agents.content_agent.ContentAgent.call_llm", AsyncMock(return_value=content_payload))
    monkeypatch.setattr("adpilot.agents.analytics_agent.AnalyticsAgent.call_llm", AsyncMock(return_value=analytics_payload))
    monkeypatch.setattr("adpilot.agents.optimization_agent.OptimizationAgent.call_llm", AsyncMock(return_value=optimization_payload))

    orchestrator = CampaignOrchestrator()
    campaign_id = "test-campaign-123"

    context = await orchestrator.run(campaign_id, brief)

    # Assertions on context completion
    assert context.campaign_id == campaign_id
    assert context.strategy == strategy_payload
    assert context.audience == audience_payload
    assert context.competitors == competitor_payload
    assert context.content == content_payload
    assert context.analytics == analytics_payload
    assert context.optimization == optimization_payload

    # Assertions on memory service storage
    stored_context = await orchestrator.memory_service.get_context(campaign_id)
    assert stored_context is not None
    assert stored_context.strategy == strategy_payload

    # Assertions on agent run records
    records = orchestrator.agent_run_records
    assert len(records) == 6
    agent_names = [r.agent_name for r in records]
    assert agent_names == [
        "strategy_agent",
        "audience_agent",
        "competitor_agent",
        "content_agent",
        "analytics_agent",
        "optimization_agent",
    ]
    for r in records:
        assert r.status.value == "success"
        assert r.started_at is not None
        assert r.finished_at is not None

@pytest.mark.asyncio
async def test_campaign_orchestrator_retry_and_failure(monkeypatch):
    brief = CampaignInput(
        business_name="Test Enterprise",
        product_description="Enterprise CRM Software",
        target_market="B2B mid-market companies",
        budget_usd=50000.0,
        goals=[CampaignGoal.lead_generation],
        channels=[MarketingChannel.linkedin, MarketingChannel.email],
        tone_of_voice=ToneOfVoice.authoritative,
        competitors=["Salesforce", "HubSpot"],
        campaign_duration_days=90,
    )

    strategy_payload = StrategyAgentOutput(
        positioning_statement="Enterprise CRM simplified",
        usp="AI-driven deal insights",
        elevator_pitch="Close deals 50% faster.",
        tone_of_voice=ToneOfVoice.authoritative,
        brand_voice_guidelines="Authoritative and clear",
        primary_channels=[MarketingChannel.linkedin],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage="awareness", budget_allocation_percent=55, key_messages=["CRM simplicity"]),
            FunnelStageStrategy(stage="conversion", budget_allocation_percent=45, key_messages=["AI insights"]),
        ],
        target_persona_summary="Sales directors",
        key_differentiators=["AI auto-data entry"],
        risks_and_considerations=["Sales team onboarding"],
    )

    # StrategyAgent fails first, then succeeds
    call_count = 0
    async def strategy_call_mock(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("Transient LLM error")
        return strategy_payload

    monkeypatch.setattr("adpilot.agents.strategy_agent.StrategyAgent.call_llm", strategy_call_mock)
    
    # Other agents mock to short-circuit or prevent errors
    monkeypatch.setattr("adpilot.agents.audience_agent.AudienceAgent.call_llm", AsyncMock(side_effect=ValueError("Stop pipeline")))

    orchestrator = CampaignOrchestrator()
    campaign_id = "test-fail-campaign"

    # Run orchestrator and expect failure at audience agent
    with pytest.raises(ValueError, match="Stop pipeline"):
        await orchestrator.run(campaign_id, brief)

    # Strategy agent should have succeeded on 2nd attempt, audience agent failed
    records = orchestrator.agent_run_records
    assert len(records) == 2
    assert records[0].agent_name == "strategy_agent"
    assert records[0].status.value == "success"
    assert records[1].agent_name == "audience_agent"
    assert records[1].status.value == "failed"
