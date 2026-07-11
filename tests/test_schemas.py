"""General schema validation tests."""

import pytest
from pydantic import ValidationError

from adpilot.schemas.agent_schemas import (
    StrategyAgentOutput,
    FunnelStageStrategy,
    CampaignInput,
)


def test_funnel_allocation_sum_valid():
    # construct a minimal valid StrategyAgentOutput with proper allocation sum
    output = StrategyAgentOutput(
        positioning_statement="p",
        usp="u",
        elevator_pitch="e",
        tone_of_voice="friendly",
        brand_voice_guidelines="b",
        primary_channels=["instagram"],
        messaging_pillars=[],
        funnel_strategy=[
            FunnelStageStrategy(stage="awareness", budget_allocation_percent=40, key_messages=[]),
            FunnelStageStrategy(stage="consideration", budget_allocation_percent=30, key_messages=[]),
            FunnelStageStrategy(stage="conversion", budget_allocation_percent=30, key_messages=[]),
        ],
        target_persona_summary="t",
        key_differentiators=[],
        risks_and_considerations=[],
    )
    # No exception means validation passed
    assert output.funnel_strategy[0].budget_allocation_percent == 40


def test_funnel_allocation_sum_invalid():
    with pytest.raises(ValidationError):
        StrategyAgentOutput(
            positioning_statement="p",
            usp="u",
            elevator_pitch="e",
            tone_of_voice="friendly",
            brand_voice_guidelines="b",
            primary_channels=["instagram"],
            messaging_pillars=[],
            funnel_strategy=[
                FunnelStageStrategy(stage="awareness", budget_allocation_percent=50, key_messages=[]),
                FunnelStageStrategy(stage="consideration", budget_allocation_percent=30, key_messages=[]),
            ],
            target_persona_summary="t",
            key_differentiators=[],
            risks_and_considerations=[],
        )


def test_campaign_input_invalid_duration():
    with pytest.raises(ValidationError):
        CampaignInput(
            business_name="Test",
            product_description="Desc",
            target_market="Market",
            budget_usd=1000,
            goals=["lead_generation"],
            channels=["email"],
            tone_of_voice="friendly",
            competitors=[],
            campaign_duration_days=5,
        )
