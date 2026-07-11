import asyncio
import pytest
from adpilot.agents.content_agent import ContentAgent
from adpilot.core.exceptions import AgentOutputError
from adpilot.schemas.agent_schemas import (
    ChannelBenchmark,
    CompetitorAnalysis,
    FunnelStageStrategy,
    MarketingChannel,
    PositiveFloat,
    ResearchAgentOutput,
    StrategyAgentOutput,
    ToneOfVoice,
    TrendingTopic,
    CampaignContext,
    CompetitorLandscape,
    Competitor,
    CampaignInput,
    CampaignGoal,
)


def test_content_agent_run_parses_valid_llm_response(monkeypatch):
    agent = ContentAgent()

    strategy = StrategyAgentOutput(
        positioning_statement="Lead with product quality",
        usp="High-conversion creative tailored to the target persona",
        elevator_pitch="A campaign designed to convert awareness into revenue.",
        tone_of_voice=ToneOfVoice.friendly,
        brand_voice_guidelines="Use simple language, friendly tone, and clear CTAs.",
        primary_channels=[MarketingChannel.email],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage="awareness", budget_allocation_percent=50, key_messages=["Introduce benefits"]),
            FunnelStageStrategy(stage="conversion", budget_allocation_percent=50, key_messages=["Ask for the sale"]),
        ],
        target_persona_summary="Busy professionals who want quick results.",
        key_differentiators=["Fast turnaround", "Proven messaging"],
        risks_and_considerations=["Need to maintain brand tone"],
    )

    research = ResearchAgentOutput(
        audience_personas=[],
        competitor_analyses=[
            CompetitorAnalysis(
                name="Competitor A",
                strengths=["Strong brand recognition"],
                weaknesses=["High price point"],
                positioning="Premium offering for larger businesses.",
            )
        ],
        trending_topics=[TrendingTopic(topic="AI marketing", relevance_score=75.0)],
        channel_benchmarks=[ChannelBenchmark(channel=MarketingChannel.email, cpc=1.2, ctr=10.0)],
        audience_language="English",
        key_insights=["Email remains the top converting channel."],
        market_size_estimate=PositiveFloat(500000.0),
        search_queries_used=["email marketing best practices"],
    )

    content_payload = {
        "ads": [
            {
                "headline": "Launch your next campaign today",
                "body": "Reach busy professionals with messaging that converts.",
                "call_to_action": "Start now",
                "funnel_stage": "awareness",
                "format": "text",
                "hashtags": ["#marketing", "#growth"],
            }
        ],
        "email_sequences": [],
        "social_posts": [],
        "blog_outlines": [],
        "cta_variants": [],
        "content_calendar_note": "Publish promotional email week 1 and follow up with social posts.",
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(content_payload)

    monkeypatch.setattr("adpilot.agents.content_agent.ContentAgent.call_llm", fake_call_llm)

    campaign = CampaignInput(
        business_name="Test Business",
        product_description="Test Product Description",
        target_market="Test Target Market",
        budget_usd=1000.0,
        goals=[CampaignGoal.brand_awareness],
        channels=[MarketingChannel.email],
        tone_of_voice=ToneOfVoice.friendly,
        competitors=["Competitor A"],
        campaign_duration_days=30,
    )
    competitors_list = [
        Competitor(
            name=c.name,
            strengths=c.strengths,
            weaknesses=c.weaknesses,
            opportunities=[],
            threats=[],
            messaging_analysis=c.positioning,
            pricing_comparison="",
            market_gaps=[],
        )
        for c in research.competitor_analyses
    ]
    competitor_landscape = CompetitorLandscape(competitors=competitors_list, opportunities=[], threats=[])
    context = CampaignContext(
        campaign_id="test-campaign",
        brief=campaign,
        strategy=strategy,
        competitors=competitor_landscape,
    )
    result_context = asyncio.run(agent.run(context))
    result = result_context.content

    assert result.content_calendar_note == content_payload["content_calendar_note"]
    assert result.ads[0].headline == content_payload["ads"][0]["headline"]
    assert result.ads[0].hashtags == content_payload["ads"][0]["hashtags"]


def test_content_agent_run_rejects_invalid_llm_output(monkeypatch):
    agent = ContentAgent()

    strategy = StrategyAgentOutput(
        positioning_statement="Lead with product quality",
        usp="High-conversion creative tailored to the target persona",
        elevator_pitch="A campaign designed to convert awareness into revenue.",
        tone_of_voice=ToneOfVoice.friendly,
        brand_voice_guidelines="Use simple language, friendly tone, and clear CTAs.",
        primary_channels=[MarketingChannel.email],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage="awareness", budget_allocation_percent=50, key_messages=["Introduce benefits"]),
            FunnelStageStrategy(stage="conversion", budget_allocation_percent=50, key_messages=["Ask for the sale"]),
        ],
        target_persona_summary="Busy professionals who want quick results.",
        key_differentiators=["Fast turnaround", "Proven messaging"],
        risks_and_considerations=["Need to maintain brand tone"],
    )

    research = ResearchAgentOutput(
        audience_personas=[],
        competitor_analyses=[
            CompetitorAnalysis(
                name="Competitor A",
                strengths=["Strong brand recognition"],
                weaknesses=["High price point"],
                positioning="Premium offering for larger businesses.",
            )
        ],
        trending_topics=[TrendingTopic(topic="AI marketing", relevance_score=75.0)],
        channel_benchmarks=[ChannelBenchmark(channel=MarketingChannel.email, cpc=1.2, ctr=10.0)],
        audience_language="English",
        key_insights=["Email remains the top converting channel."],
        market_size_estimate=PositiveFloat(500000.0),
        search_queries_used=["email marketing best practices"],
    )

    invalid_payload = {
        "ads": [
            {
                "headline": "Launch your next campaign today",
                "body": "Reach busy professionals with messaging that converts.",
                "call_to_action": "Start now",
                "funnel_stage": "awareness",
                "format": "text",
                "hashtags": ["#marketing", "#growth"],
            }
        ],
        "email_sequences": [],
        "social_posts": [],
        "blog_outlines": [],
        "cta_variants": [],
        # Missing required content_calendar_note field to force validation failure.
    }

    async def fake_call_llm(self, **kwargs):
        return self.validate_output(invalid_payload)

    monkeypatch.setattr("adpilot.agents.content_agent.ContentAgent.call_llm", fake_call_llm)

    campaign = CampaignInput(
        business_name="Test Business",
        product_description="Test Product Description",
        target_market="Test Target Market",
        budget_usd=1000.0,
        goals=[CampaignGoal.brand_awareness],
        channels=[MarketingChannel.email],
        tone_of_voice=ToneOfVoice.friendly,
        competitors=["Competitor A"],
        campaign_duration_days=30,
    )
    competitors_list = [
        Competitor(
            name=c.name,
            strengths=c.strengths,
            weaknesses=c.weaknesses,
            opportunities=[],
            threats=[],
            messaging_analysis=c.positioning,
            pricing_comparison="",
            market_gaps=[],
        )
        for c in research.competitor_analyses
    ]
    competitor_landscape = CompetitorLandscape(competitors=competitors_list, opportunities=[], threats=[])
    context = CampaignContext(
        campaign_id="test-campaign",
        brief=campaign,
        strategy=strategy,
        competitors=competitor_landscape,
    )
    with pytest.raises(AgentOutputError):
        asyncio.run(agent.run(context))
