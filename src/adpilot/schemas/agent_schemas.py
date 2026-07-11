"""Pydantic v2 schema definitions for the AdPilot multi‑agent system.

Only the data contracts are defined – no business logic.  These schemas are the
single source of truth for all agents and will be used for validation and
auto‑generation of JSON examples.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator, field_validator

# ---------------------------------------------------------------------------
# Enums – all inherit from ``str`` for JSON friendliness.
# ---------------------------------------------------------------------------


class MarketingChannel(str, Enum):
    facebook = "facebook"
    instagram = "instagram"
    twitter = "twitter"
    linkedin = "linkedin"
    email = "email"
    tiktok = "tiktok"
    youtube = "youtube"
    snapchat = "snapchat"


class CampaignGoal(str, Enum):
    lead_generation = "lead_generation"
    brand_awareness = "brand_awareness"
    sales_conversion = "sales_conversion"
    engagement = "engagement"
    website_traffic = "website_traffic"


class ToneOfVoice(str, Enum):
    friendly = "friendly"
    professional = "professional"
    witty = "witty"
    compassionate = "compassionate"
    authoritative = "authoritative"


class FunnelStage(str, Enum):
    awareness = "awareness"
    consideration = "consideration"
    conversion = "conversion"
    loyalty = "loyalty"


class ContentType(str, Enum):
    ad_copy = "ad_copy"
    email = "email"
    social_post = "social_post"
    blog = "blog"
    landing_page = "landing_page"


class AdFormat(str, Enum):
    image = "image"
    video = "video"
    carousel = "carousel"
    story = "story"
    text = "text"


class ImageStyle(str, Enum):
    photorealistic = "photorealistic"
    illustration = "illustration"
    flat = "flat"
    retro = "retro"
    minimal = "minimal"


class MetricType(str, Enum):
    ctr = "ctr"
    cpc = "cpc"
    cpa = "cpa"
    impressions = "impressions"
    conversions = "conversions"
    open_rate = "open_rate"
    engagement_rate = "engagement_rate"
    conversion_rate = "conversion_rate"
    roas = "roas"
    roi = "roi"


class AgentRunStatus(str, Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    skipped = "skipped"


class SuggestionPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ---------------------------------------------------------------------------
# Primitive type helpers (aliases) – real validation done in model validators.
# ---------------------------------------------------------------------------

PercentFloat = float  # 0‑100 inclusive percentage
PositiveFloat = float  # >0
ScoreInt = int  # arbitrary score integer

# ---------------------------------------------------------------------------
# Core input model
# ---------------------------------------------------------------------------


class CampaignInput(BaseModel):
    business_name: str
    product_description: str
    target_market: str
    budget_usd: PositiveFloat = Field(..., gt=0, description="Budget in USD, must be > 0")
    goals: List[CampaignGoal]
    channels: List[MarketingChannel]
    tone_of_voice: ToneOfVoice
    brand_colors: Optional[List[str]] = None
    competitors: List[str]
    website_url: Optional[str] = None
    existing_tagline: Optional[str] = None
    campaign_duration_days: int = Field(..., ge=7, le=365)

    @field_validator("brand_colors", mode="before")
    @classmethod
    def validate_brand_colors(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        for color in v:
            if not isinstance(color, str) or not color.startswith("#") or len(color) not in (4, 7):
                raise ValueError(f"Invalid hex color: {color}")
        return v


# ---------------------------------------------------------------------------
# Strategy schemas
# ---------------------------------------------------------------------------


class MessagingPillar(BaseModel):
    title: str
    description: str


class ChannelPriority(BaseModel):
    channel: MarketingChannel
    priority: int = Field(..., ge=1, le=5)


class FunnelStageStrategy(BaseModel):
    stage: FunnelStage
    budget_allocation_percent: PercentFloat = Field(..., ge=0, le=100)
    key_messages: List[str]


class StrategyAgentInput(BaseModel):
    campaign: CampaignInput


class StrategyAgentOutput(BaseModel):
    positioning_statement: str
    usp: str
    elevator_pitch: str
    tone_of_voice: ToneOfVoice
    brand_voice_guidelines: str
    primary_channels: List[MarketingChannel]
    messaging_pillars: List[MessagingPillar]
    funnel_strategy: List[FunnelStageStrategy]
    target_persona_summary: str
    key_differentiators: List[str]
    risks_and_considerations: List[str]

    @model_validator(mode="after")
    def check_budget_sum(self) -> "StrategyAgentOutput":
        total = sum(f.budget_allocation_percent for f in self.funnel_strategy)
        if round(total) != 100:
            raise ValueError("funnel_strategy budget allocations must sum to exactly 100%")
        return self


# ---------------------------------------------------------------------------
# Research schemas
# ---------------------------------------------------------------------------


class AudiencePersona(BaseModel):
    name: str
    description: str
    demographics: str
    interests: List[str]


class CompetitorAnalysis(BaseModel):
    name: str
    strengths: List[str]
    weaknesses: List[str]
    positioning: str


class TrendingTopic(BaseModel):
    topic: str
    relevance_score: PercentFloat = Field(..., ge=0, le=100)


class ChannelBenchmark(BaseModel):
    channel: MarketingChannel
    cpc: PositiveFloat
    ctr: PercentFloat = Field(..., ge=0, le=100)


class ResearchAgentInput(BaseModel):
    campaign: CampaignInput


class ResearchAgentOutput(BaseModel):
    audience_personas: List[AudiencePersona]
    competitor_analyses: List[CompetitorAnalysis]
    trending_topics: List[TrendingTopic]
    channel_benchmarks: List[ChannelBenchmark]
    audience_language: str
    key_insights: List[str]
    market_size_estimate: PositiveFloat
    search_queries_used: List[str]


# ---------------------------------------------------------------------------
# Content schemas
# ---------------------------------------------------------------------------


class AdCopy(BaseModel):
    headline: str
    body: str
    call_to_action: str
    funnel_stage: FunnelStage
    format: AdFormat
    hashtags: List[str]


class EmailInSequence(BaseModel):
    subject: str
    body: str
    day_offset: int


class EmailSequence(BaseModel):
    sequence_name: str
    emails: List[EmailInSequence]


class SocialPost(BaseModel):
    platform: MarketingChannel
    content: str
    hashtags: List[str]
    visual_url: Optional[str] = None


class BlogOutline(BaseModel):
    title: str
    sections: List[str]


class CTAVariant(BaseModel):
    text: str
    style: Optional[str] = None


class ContentAgentInput(BaseModel):
    strategy: StrategyAgentOutput
    research: ResearchAgentOutput


class GoogleAd(BaseModel):
    headline_1: str
    headline_2: str
    headline_3: str
    description_1: str
    description_2: str
    path_1: str
    path_2: str
    call_to_action: str


class LandingPageCopy(BaseModel):
    hero_headline: str
    hero_subheadline: str
    features: List[str]
    benefit_statement: str
    call_to_action: str
    footer_text: str


class ContentAgentOutput(BaseModel):
    ads: List[AdCopy]
    email_sequences: List[EmailSequence]
    social_posts: List[SocialPost]
    blog_outlines: List[BlogOutline]
    cta_variants: List[CTAVariant]
    content_calendar_note: str
    google_ads: Optional[List[GoogleAd]] = None
    landing_page_copy: Optional[LandingPageCopy] = None

    @field_validator("ads")
    @classmethod
    def ensure_funnel_coverage(cls, ads: List[AdCopy]) -> List[AdCopy]:
        stages = {ad.funnel_stage for ad in ads}
        if len(stages) < 2:
            # In Phase 1 we only enforce a warning via comment – real rule later.
            pass
        return ads

    @field_validator("social_posts")
    @classmethod
    def lowercase_hashtags(cls, posts: List[SocialPost]) -> List[SocialPost]:
        for p in posts:
            p.hashtags = [h.lower() for h in p.hashtags]
        return posts


# ---------------------------------------------------------------------------
# Analytics schemas
# ---------------------------------------------------------------------------


class CampaignHealthScore(BaseModel):
    overall: PercentFloat = Field(..., ge=0, le=100)
    stage_scores: dict[FunnelStage, PercentFloat]


class MetricPrediction(BaseModel):
    metric: MetricType
    predicted_value: PositiveFloat
    confidence: PercentFloat = Field(..., ge=0, le=100)
    basis: str


class ContentScorecard(BaseModel):
    content_type: ContentType
    score: ScoreInt
    comments: Optional[str] = None


class ImprovementSuggestion(BaseModel):
    suggestion: str
    priority: SuggestionPriority
    impact_estimate_percent: PercentFloat = Field(..., ge=0, le=100)


class AnalyticsAgentInput(BaseModel):
    campaign: CampaignInput
    strategy: StrategyAgentOutput
    research: ResearchAgentOutput
    content: ContentAgentOutput


class KPITargetsDetailed(BaseModel):
    ctr_target: PercentFloat
    cpc_target: PositiveFloat
    cpa_target: PositiveFloat
    roas_target: PositiveFloat
    conversion_goals: List[str]
    kpi_recommendations: List[str]


class AnalyticsAgentOutput(BaseModel):
    health_score: CampaignHealthScore
    predicted_metrics: List[MetricPrediction]
    content_scorecards: List[ContentScorecard]
    improvement_suggestions: List[ImprovementSuggestion]
    ab_test_recommendations: List[str]
    budget_reallocation_advice: str
    executive_summary: str
    next_review_checkpoint: str
    kpi_targets: Optional[KPITargetsDetailed] = None

    @field_validator("health_score")
    @classmethod
    def health_range(cls, hs: CampaignHealthScore) -> CampaignHealthScore:
        if not (0 <= hs.overall <= 100):
            raise ValueError("Health score must be between 0 and 100")
        return hs


# ---------------------------------------------------------------------------
# Design schemas
# ---------------------------------------------------------------------------


class ImageDimensions(BaseModel):
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)


class DesignBrief(BaseModel):
    dalle_prompt: str
    negative_prompt: str
    concept: str
    rationale: str
    image_dimensions: ImageDimensions
    style: ImageStyle
    format: str  # e.g., png, jpg, webp

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        val = v.strip().lower()
        if val in {"png", "jpg", "jpeg", "webp"}:
            return "png" if val == "jpeg" else val
        return "png"


class GeneratedVisual(BaseModel):
    image_url: str
    brief: DesignBrief
    generation_error: Optional[str] = None


class DesignAgentInput(BaseModel):
    content: ContentAgentOutput
    strategy: StrategyAgentOutput
    campaign_id: Optional[str] = None
    task_id: Optional[str] = None


class DesignAgentOutput(BaseModel):
    design_briefs: List[DesignBrief]
    generated_visuals: List[GeneratedVisual]
    brand_style_guide_snippet: str
    generation_errors: List[str] = []


# ---------------------------------------------------------------------------
# Campaign manager schemas
# ---------------------------------------------------------------------------


class ChannelBudgetAllocation(BaseModel):
    channel: MarketingChannel
    allocation_percent: PercentFloat = Field(..., ge=0, le=100)


class WeeklyScheduleItem(BaseModel):
    week_number: int = Field(..., ge=1)
    activities: List[str]


class AdSet(BaseModel):
    ads: List[AdCopy]
    budget_allocation: List[ChannelBudgetAllocation]


class ABTestPlan(BaseModel):
    test_name: str
    variant_a: str
    variant_b: str
    metric: MetricType
    duration_days: int


class KPITargets(BaseModel):
    metric: MetricType
    target_value: PositiveFloat


class CampaignManagerInput(BaseModel):
    campaign: CampaignInput
    strategy: StrategyAgentOutput
    research: ResearchAgentOutput
    content: ContentAgentOutput
    analytics: AnalyticsAgentOutput
    design: DesignAgentOutput


class CampaignManagerOutput(BaseModel):
    channel_budget_allocations: List[ChannelBudgetAllocation]
    weekly_schedule: List[WeeklyScheduleItem]
    ad_sets: List[AdSet]
    ab_test_plans: List[ABTestPlan]
    kpi_targets: List[KPITargets]


# ---------------------------------------------------------------------------
# Orchestrator schemas
# ---------------------------------------------------------------------------


class AgentRunRecord(BaseModel):
    agent_name: str
    status: AgentRunStatus
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error_message: Optional[str] = None
    output_snapshot: Optional[dict] = None


class OrchestratorInput(BaseModel):
    campaign: CampaignInput


class OrchestratorOutput(BaseModel):
    campaign_input: CampaignInput
    strategy: StrategyAgentOutput
    research: ResearchAgentOutput
    content: ContentAgentOutput
    analytics: AnalyticsAgentOutput
    design: DesignAgentOutput
    campaign_manager: Optional[CampaignManagerOutput] = None
    agent_run_records: List[AgentRunRecord]
    final_campaign_summary: str
    errors: List[str] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "campaign_input": {
                    "business_name": "Nourish Egypt",
                    "product_description": "Healthy meal‑kit delivery",
                    "target_market": "Urban professionals 25‑40",
                    "budget_usd": 5000,
                    "goals": ["lead_generation", "brand_awareness"],
                    "channels": ["instagram", "facebook", "email"],
                    "tone_of_voice": "friendly",
                    "brand_colors": ["#2D6A4F", "#B7E4C7"],
                    "competitors": ["Eat Clean Egypt", "The Food Lab"],
                    "campaign_duration_days": 30,
                }
            }
        }
    }


# ---------------------------------------------------------------------------
# Phase 1 New Agent Schemas
# ---------------------------------------------------------------------------


class Persona(BaseModel):
    name: str
    demographics: str
    psychographics: str
    pain_points: List[str]
    goals: List[str]
    objections: List[str]
    buying_triggers: List[str]


class AudienceOutput(BaseModel):
    primary_persona: Persona
    secondary_personas: List[Persona]
    pain_points: List[str]
    motivations: List[str]
    objections: List[str]


class AudienceAgentInput(BaseModel):
    campaign: CampaignInput


class Competitor(BaseModel):
    name: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    messaging_analysis: str
    pricing_comparison: str
    market_gaps: List[str]


class CompetitorLandscape(BaseModel):
    competitors: List[Competitor]
    opportunities: List[str]
    threats: List[str]


class CompetitorAgentInput(BaseModel):
    campaign: CampaignInput


class CreativeOutput(BaseModel):
    creative_brief: str
    design_direction: str
    color_palette: List[str]
    image_prompts: List[str]
    video_prompts: List[str]
    thumbnail_prompts: List[str]


class CreativeAgentInput(BaseModel):
    campaign: CampaignInput
    strategy: StrategyAgentOutput


class OptimizationAction(BaseModel):
    condition: str
    metric: str
    current_value: float
    target_value: float
    recommendation: str
    priority: SuggestionPriority
    action_steps: List[str]


class OptimizationOutput(BaseModel):
    optimization_actions: List[OptimizationAction]
    budget_reallocation_plan: str
    performance_forecast: str


class OptimizationAgentInput(BaseModel):
    campaign: CampaignInput
    analytics: AnalyticsAgentOutput


class UTMParameters(BaseModel):
    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


class PublishingPackage(BaseModel):
    headlines: List[str]
    ctas: List[str]
    targeting_criteria: List[str]
    budget_allocation: dict[str, float]
    utm_parameters: UTMParameters
    campaign_metadata: dict[str, str]


class PublishingAgentInput(BaseModel):
    campaign: CampaignInput
    content: ContentAgentOutput
    strategy: StrategyAgentOutput


class CampaignContext(BaseModel):
    campaign_id: str
    brief: CampaignInput
    strategy: Optional[StrategyAgentOutput] = None
    research: Optional[ResearchAgentOutput] = None
    audience: Optional[AudienceOutput] = None
    competitors: Optional[CompetitorLandscape] = None
    content: Optional[ContentAgentOutput] = None
    creative: Optional[CreativeOutput] = None
    design: Optional[DesignAgentOutput] = None
    analytics: Optional[AnalyticsAgentOutput] = None
    optimization: Optional[OptimizationOutput] = None
    publishing: Optional[PublishingPackage] = None
    campaign_manager: Optional[CampaignManagerOutput] = None

