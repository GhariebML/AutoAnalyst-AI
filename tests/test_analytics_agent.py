"""Tests for the AnalyticsAgent."""

from __future__ import annotations

import pytest
from src.adpilot.core.exceptions import AgentOutputError

from src.adpilot.agents.analytics_agent import AnalyticsAgent
from src.adpilot.schemas.agent_schemas import (
    AnalyticsAgentOutput,
    CampaignHealthScore,
    ContentScorecard,
    ImprovementSuggestion,
    MetricPrediction,
    SuggestionPriority,
)


class TestAnalyticsAgent:
    """Test suite for AnalyticsAgent."""

    def test_invalid_health_score_rejected(self) -> None:
        """Test that health scores outside 0-100 are rejected."""
        agent = AnalyticsAgent()

        # Invalid overall score > 100
        invalid_dict = {
            "health_score": {"overall": 150.0, "stage_scores": {}},
            "predicted_metrics": [],
            "content_scorecards": [],
            "improvement_suggestions": [],
            "ab_test_recommendations": [],
            "budget_reallocation_advice": "",
            "executive_summary": "",
            "next_review_checkpoint": ""
        }

        with pytest.raises(AgentOutputError):
            agent.validate_output(invalid_dict)

        # Invalid overall score < 0
        invalid_dict["health_score"]["overall"] = -10.0
        with pytest.raises(AgentOutputError):
            agent.validate_output(invalid_dict)

    def test_suggestion_priority_enum_works(self) -> None:
        """Test that SuggestionPriority enum values are accepted."""
        agent = AnalyticsAgent()

        valid_output = AnalyticsAgentOutput(
            health_score=CampaignHealthScore(overall=85.0, stage_scores={}),
            predicted_metrics=[],
            content_scorecards=[],
            improvement_suggestions=[
                ImprovementSuggestion(
                    suggestion="Improve ad copy",
                    priority=SuggestionPriority.high,
                    impact_estimate_percent=20.0,
                )
            ],
            ab_test_recommendations=[],
            budget_reallocation_advice="",
            executive_summary="",
            next_review_checkpoint="",
        )

        # Should not raise
        result = agent.validate_output(valid_output.model_dump())
        assert result.improvement_suggestions[0].priority == SuggestionPriority.high

    def test_predicted_metrics_include_confidence_and_basis(self) -> None:
        """Test that MetricPrediction includes confidence and basis."""
        agent = AnalyticsAgent()

        valid_output = AnalyticsAgentOutput(
            health_score=CampaignHealthScore(overall=90.0, stage_scores={}),
            predicted_metrics=[
                MetricPrediction(
                    metric="ctr",
                    predicted_value=1000.0,
                    confidence=85.0,
                    basis="Based on historical data",
                )
            ],
            content_scorecards=[],
            improvement_suggestions=[],
            ab_test_recommendations=[],
            budget_reallocation_advice="",
            executive_summary="",
            next_review_checkpoint="",
        )

        result = agent.validate_output(valid_output.model_dump())
        metric = result.predicted_metrics[0]
        assert metric.confidence == 85.0
        assert metric.basis == "Based on historical data"

    def test_output_validation_for_valid_structure(self) -> None:
        """Test that a fully valid output structure passes validation."""
        agent = AnalyticsAgent()

        valid_output = AnalyticsAgentOutput(
            health_score=CampaignHealthScore(overall=75.0, stage_scores={"awareness": 80.0}),
            predicted_metrics=[
                MetricPrediction(
                    metric="impressions",
                    predicted_value=50000.0,
                    confidence=90.0,
                    basis="Market research",
                )
            ],
            content_scorecards=[
                ContentScorecard(
                    content_type="ad_copy",
                    score=8,
                    comments="Strong messaging",
                )
            ],
            improvement_suggestions=[
                ImprovementSuggestion(
                    suggestion="Optimize targeting",
                    priority=SuggestionPriority.medium,
                    impact_estimate_percent=15.0,
                )
            ],
            ab_test_recommendations=["Test headline variations"],
            budget_reallocation_advice="Increase spend on social media",
            executive_summary="Campaign shows good potential",
            next_review_checkpoint="2026-06-01",
        )

        # Should not raise
        result = agent.validate_output(valid_output.model_dump())
        assert result.health_score.overall == 75.0
        assert len(result.predicted_metrics) == 1
        assert len(result.content_scorecards) == 1
        assert len(result.improvement_suggestions) == 1