"""AI Optimizer Rule Engine."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel


class CampaignMetrics(BaseModel):
    """Input metrics for a campaign."""

    ctr: float
    cpa: float
    roas: float


class CampaignTargets(BaseModel):
    """Target metrics for a campaign."""

    ctr_target: float
    cpa_target: float
    roas_target: float


class OptimizationRecommendation(BaseModel):
    """A single rule evaluation result/recommendation."""

    rule_name: str
    condition: str
    recommendation: str
    action_type: str  # regenerate_content, reduce_budget, increase_budget


class AIOptimizer:
    """Evaluate performance metrics and generate optimization recommendations."""

    def evaluate(
        self, metrics: CampaignMetrics, targets: CampaignTargets
    ) -> List[OptimizationRecommendation]:
        """Evaluate rules and generate recommendations."""
        recommendations: List[OptimizationRecommendation] = []

        # Rule 1: CTR less than target
        if metrics.ctr < targets.ctr_target:
            recommendations.append(
                OptimizationRecommendation(
                    rule_name="Low CTR Rule",
                    condition=f"CTR ({metrics.ctr}%) < Target ({targets.ctr_target}%)",
                    recommendation="The click-through rate is below target. We recommend regenerating the ad copies and social post creatives with high-converting hooks.",
                    action_type="regenerate_content",
                )
            )

        # Rule 2: CPA greater than target
        if metrics.cpa > targets.cpa_target:
            recommendations.append(
                OptimizationRecommendation(
                    rule_name="High CPA Rule",
                    condition=f"CPA (${metrics.cpa:.2f}) > Target (${targets.cpa_target:.2f})",
                    recommendation="The cost per acquisition is exceeding the target. We recommend reducing the budget on lower-performing channels to lower acquisition costs.",
                    action_type="reduce_budget",
                )
            )

        # Rule 3: ROAS greater than target
        if metrics.roas > targets.roas_target:
            recommendations.append(
                OptimizationRecommendation(
                    rule_name="High ROAS Rule",
                    condition=f"ROAS ({metrics.roas:.2f}x) > Target ({targets.roas_target:.2f}x)",
                    recommendation="The return on ad spend is exceeding the target. We recommend increasing the budget to scale the campaign and capture additional conversions.",
                    action_type="increase_budget",
                )
            )

        return recommendations
