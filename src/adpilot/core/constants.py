"""Project-wide constants and enum re-exports for AdPilot."""

from enum import Enum

from ..schemas.agent_schemas import (
    AdFormat as AdFormat,
    AgentRunStatus as AgentRunStatus,
    CampaignGoal as CampaignGoal,
    ContentType as ContentType,
    FunnelStage as FunnelStage,
    ImageStyle as ImageStyle,
    MarketingChannel as MarketingChannel,
    MetricType as MetricType,
    ToneOfVoice as ToneOfVoice,
)

# You can import directly from ``adpilot.core.constants`` in code.
CHAMBER = Enum("CHAMBER", "DEVELOPMENT TESTING STAGING PRODUCTION")

__all__ = [
    "AdFormat",
    "AgentRunStatus",
    "CampaignGoal",
    "CHAMBER",
    "ContentType",
    "FunnelStage",
    "ImageStyle",
    "MarketingChannel",
    "MetricType",
    "ToneOfVoice",
]
