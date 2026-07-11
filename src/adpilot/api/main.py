"""AdPilot Phase 2 – FastAPI application.

Endpoints
---------
GET  /healthz
    Liveness probe – always returns 200 when the server is up.

POST /api/analytics/evaluate
    Standalone Analytics Quality Gate.
    Accepts a fully-assembled ``AnalyticsAgentInput`` and returns the
    scored ``AnalyticsAgentOutput`` together with the gate decision and
    any optimization recommendations.
    Use this when you already have Strategy / Research / Content outputs
    and only need the evaluation step (e.g. from the React dashboard).

POST /api/campaigns/run
    Full DAG pipeline trigger.
    Accepts a ``CampaignInput`` and runs the complete multi-agent
    workflow: Strategy → Research → Content → Analytics (with retry loop)
    → Design → Campaign Manager.  Returns the full ``OrchestratorOutput``.
"""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..models.user import User as UserORM
from ..models.organization import Organization as OrgORM
from ..models.campaign_publish import CampaignPublish as PublishORM
from ..models.audit_log import AuditLog as AuditORM
from .auth import get_current_user, require_role
from ..services.analytics.connectors import LiveAnalyticsConnector
from ..services.audit_service import log_action
from ..services.integrations import dispatch_publish
from ..services.ai_optimizer import AIOptimizer, CampaignMetrics, CampaignTargets
from ..services.rag_service import RAGService
from starlette.responses import StreamingResponse

from ..agents.analytics_agent import AnalyticsAgent
from ..core.config import get_config
from ..core.database import create_tables
from ..schemas.agent_schemas import (
    AnalyticsAgentInput,
    AnalyticsAgentOutput,
    CampaignInput,
    CampaignGoal,
    MarketingChannel,
    OrchestratorInput,
    OrchestratorOutput,
    ToneOfVoice,
)
from ..services.asset_packager import AssetPackager
from ..services.task_manager import TaskManager
from ..utils.logging_utils import logger
from .auth import verify_api_key

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    _HAS_SLOWAPI = True
except ImportError:
    _HAS_SLOWAPI = False


# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create database tables on startup."""
    # Import models so they register with Base.metadata
    from ..models import campaign_task, design_asset, user, organization, campaign_publish, audit_log  # noqa: F401

    await create_tables()
    from ..core.database import async_session_factory
    from ..services.scheduler import PublishScheduler

    scheduler = PublishScheduler(session_factory=async_session_factory, interval_seconds=1.0)
    scheduler.start()
    
    logger.info("Database tables created/verified and PublishScheduler started.")
    try:
        yield
    finally:
        await scheduler.stop()


app = FastAPI(
    title="AdPilot API",
    description=(
        "Phase 2 REST API for the AdPilot autonomous marketing multi-agent platform. "
        "Exposes the Analytics Quality Gate and the full campaign DAG pipeline."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

from fastapi.responses import JSONResponse

# CORS — configurable origins, defaults to localhost dev ports
_settings = get_config()
_cors_origins = [o.strip() for o in _settings.allowed_origins.split(",")]

# Always include common dev origins so local development never breaks
_dev_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
]
for _o in _dev_origins:
    if _o not in _cors_origins:
        _cors_origins.append(_o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Global Exception Handler (RFC 7807 Problem Details)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred. Our engineers have been notified.",
            "instance": request.url.path,
        },
    )

# Rate limiting (optional — degrades gracefully if slowapi not installed)
if _HAS_SLOWAPI:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
else:
    limiter = None


# ---------------------------------------------------------------------------
# API-layer response models (not agent schemas – these are transport wrappers)
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Liveness probe response."""
    status: str = "ok"
    version: str = "2.0.0"


class AnalyticsEvaluationResponse(BaseModel):
    """Response envelope for POST /api/analytics/evaluate.

    Wraps ``AnalyticsAgentOutput`` with gate metadata so the frontend or
    calling service can act on the decision without parsing sub-fields.
    """
    gate_passed: bool
    health_score: float
    optimization_recommendations: List[str]
    analytics: AnalyticsAgentOutput

    model_config = {"json_schema_extra": {
        "example": {
            "gate_passed": True,
            "health_score": 82.5,
            "optimization_recommendations": [],
            "analytics": {},
        }
    }}


class CampaignRunResponse(BaseModel):
    """Response envelope for POST /api/campaigns/run."""
    gate_passed: bool
    final_health_score: float
    content_retries: int
    pipeline: OrchestratorOutput


class FrontendCampaignBrief(BaseModel):
    """Dashboard form payload.

    The React dashboard uses a compact camelCase shape. This model keeps that
    transport detail out of the agent schemas, which remain the source of truth.
    """

    businessName: str
    productName: str
    productDescription: str
    targetAudience: str
    goals: List[str] = []
    budget: float
    duration: str
    tone: str


class TaskResponse(BaseModel):
    """Dashboard task polling response."""

    taskId: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    progress: int
    message: Optional[str] = None


# Persistent campaign repository
from ..core.container import get_container
_repo = get_container().campaign_repo


# ---------------------------------------------------------------------------
# Dependency: shared TaskManager instance
# ---------------------------------------------------------------------------

def _get_task_manager() -> TaskManager:
    """Return a fresh TaskManager for each request (stateless per-request)."""
    return TaskManager(memory_service=get_container().memory_service)


def _normalize_goal(goal: str) -> CampaignGoal:
    value = goal.strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "lead_gen": CampaignGoal.lead_generation,
        "leads": CampaignGoal.lead_generation,
        "sales": CampaignGoal.sales_conversion,
        "traffic": CampaignGoal.website_traffic,
    }
    return aliases.get(value, CampaignGoal(value) if value in CampaignGoal._value2member_map_ else CampaignGoal.brand_awareness)


def _normalize_tone(tone: str) -> ToneOfVoice:
    value = tone.strip().lower().replace(" ", "_").replace("&", "and")
    aliases = {
        "casual": ToneOfVoice.friendly,
        "playful": ToneOfVoice.witty,
        "luxury": ToneOfVoice.authoritative,
        "technical": ToneOfVoice.authoritative,
        "modern_and_edgy": ToneOfVoice.witty,
    }
    return aliases.get(value, ToneOfVoice(value) if value in ToneOfVoice._value2member_map_ else ToneOfVoice.professional)


def _duration_to_days(duration: str) -> int:
    mapping = {
        "1-week": 7,
        "2-weeks": 14,
        "1-month": 30,
        "3-months": 90,
    }
    return mapping.get(duration.strip().lower(), 30)


def _to_campaign_input(brief: FrontendCampaignBrief) -> CampaignInput:
    goals = [_normalize_goal(goal) for goal in brief.goals] or [CampaignGoal.brand_awareness]
    return CampaignInput(
        business_name=brief.businessName,
        product_description=f"{brief.productName}: {brief.productDescription}",
        target_market=brief.targetAudience,
        budget_usd=brief.budget,
        goals=goals,
        channels=[MarketingChannel.linkedin, MarketingChannel.instagram, MarketingChannel.email],
        tone_of_voice=_normalize_tone(brief.tone),
        competitors=[],
        campaign_duration_days=_duration_to_days(brief.duration),
    )


def _provider_key_is_configured() -> bool:
    if os.getenv("ADPILOT_DASHBOARD_USE_REAL_LLM", "").strip().lower() not in {"1", "true", "yes"}:
        return False
    settings = get_config()
    provider = settings.llm_provider.strip().lower()
    if provider == "openai":
        return bool(settings.openai_api_key)
    if provider == "openrouter":
        return bool(settings.openrouter_api_key)
    if provider == "huggingface":
        return bool(settings.hf_token)
    return False


def _frontend_content_from_pipeline(result: OrchestratorOutput) -> Dict[str, Any]:
    content = result.content
    return {
        "ads": [
            {
                "platform": ad.format.value.title(),
                "headline": ad.headline,
                "body": ad.body,
                "cta": ad.call_to_action,
                "performance": ad.funnel_stage.value.title(),
                "targetAudience": result.campaign_input.target_market,
                "funnelStage": ad.funnel_stage.value.title(),
                "adFormat": ad.format.value.title(),
                "visualPrompt": (
                    next((b.dalle_prompt for b in result.design.design_briefs if ad.headline in b.concept or ad.headline in b.dalle_prompt), f"Sleek professional modern creative graphic illustration designed for {ad.format.value.title()} marketing campaigns.")
                    if result.design and result.design.design_briefs
                    else f"Sleek professional modern creative graphic illustration designed for {ad.format.value.title()} marketing campaigns."
                ),
                "hashtags": ad.hashtags,
                "cpcEstimate": "$1.45" if ad.format.value in ("image", "carousel") else "$2.10",
                "ctrEstimate": "3.2%" if ad.format.value in ("image", "carousel") else "4.8%",
            }
            for ad in content.ads
        ],
        "emailSequences": [
            {
                "subject": email.subject,
                "preview": email.body[:140] + "..." if len(email.body) > 140 else email.body,
                "body": email.body,
                "sequence": email.day_offset,
                "sendDay": email.day_offset,
                "triggerCondition": "Subscriber segment registered/updated",
                "goal": "Relationship building, product introduction & direct activation",
                "audienceFocus": result.campaign_input.target_market,
            }
            for sequence in content.email_sequences
            for email in sequence.emails
        ],
        "socialPosts": [
            {
                "platform": post.platform.value.title(),
                "content": post.content,
                "hashtags": post.hashtags,
                "imagePrompt": post.visual_url or "Clean minimal digital visual depicting modern business workflow concepts, corporate blue and warm orange accent lighting.",
                "postType": "Visual Post with Caption",
                "bestTimeToPost": "Tuesday 10:00 AM (local time)",
                "captionCopy": post.content,
            }
            for post in content.social_posts
        ],
        "summary": result.final_campaign_summary,
    }


def _demo_content(brief: FrontendCampaignBrief) -> Dict[str, Any]:
    product = brief.productName or brief.businessName
    audience = brief.targetAudience or "Forward-thinking business professionals"
    
    return {
        "ads": [
            {
                "platform": "LinkedIn",
                "headline": f"Unlock 10x Operational Efficiency with {product}",
                "body": (
                    f"Stop losing hours on manual administrative workflows. {brief.businessName} leverages "
                    f"advanced automation to orchestrate your business logic. Built specifically for "
                    f"{audience} who value rapid scaling, precision execution, and seamless integration."
                ),
                "cta": "Schedule an Operations Audit",
                "performance": "Awareness Stage",
                "targetAudience": audience,
                "funnelStage": "Awareness (Top of Funnel)",
                "adFormat": "Single Image Ad (Sponsored Content)",
                "visualPrompt": (
                    "Premium glassmorphic dashboard interface showing multi-agent workflow flows, "
                    "performance KPI charts with upward trends, sleek dark slate theme with glowing cyan "
                    "and amber accents, high-end corporate style."
                ),
                "hashtags": ["automation", "productivity", "management", "innovation"],
                "cpcEstimate": "$2.85",
                "ctrEstimate": "4.2%",
            },
            {
                "platform": "Instagram",
                "headline": f"Meet the Smartest Way to Manage {product}",
                "body": (
                    f"Is your team bogged down by repetitive processes? {brief.businessName} is the ultimate "
                    f"infrastructure that coordinates strategy, analytics, and content generation. "
                    f"Empower {audience} to focus on high-impact growth."
                ),
                "cta": "Start a Free 14-Day Trial",
                "performance": "Consideration Stage",
                "targetAudience": audience,
                "funnelStage": "Consideration (Middle of Funnel)",
                "adFormat": "Carousel Post (3-Slide Structure)",
                "visualPrompt": (
                    "Three-part graphic sequence: Slide 1: Modern creative workspace with a glowing device displaying "
                    "the product name. Slide 2: An isometric 3D flow diagram showing task inputs transforming to outputs. "
                    "Slide 3: A minimalist checklist highlighting core features with vibrant green success icons."
                ),
                "hashtags": ["digitalops", "workflow", "smartbusiness", "techsolutions"],
                "cpcEstimate": "$0.95",
                "ctrEstimate": "5.1%",
            },
            {
                "platform": "Facebook",
                "headline": "Stop Outsourcing. Start Automating Your Core Work.",
                "body": (
                    f"Why hire expensive agencies when AI agents can collaborate to deliver professional-grade "
                    f"outputs in seconds? {brief.businessName} provides an all-in-one suite designed to optimize "
                    f"operations for {audience}. Run faster, spend smarter, and scale effortlessly."
                ),
                "cta": "Claim Your Onboarding Consultation",
                "performance": "Conversion Stage",
                "targetAudience": audience,
                "funnelStage": "Conversion (Bottom of Funnel)",
                "adFormat": "Video Ad (15-Second Motion Demo)",
                "visualPrompt": (
                    "A dynamic screen-recording walkthrough of the AdPilot platform, demonstrating the swift "
                    "generation of a complete marketing campaign from a single brief. Colors align with "
                    "professional blue and teal gradients, exhibiting a premium UI feel."
                ),
                "hashtags": ["saas", "agencygrowth", "scalingup", "biztech"],
                "cpcEstimate": "$1.35",
                "ctrEstimate": "4.6%",
            },
        ],
        "emailSequences": [
            {
                "subject": f"Revolutionizing your business operations with {brief.businessName}",
                "preview": f"Discover how {product} helps you move from fragmented systems to automated growth.",
                "body": (
                    f"Dear Marketing & Ops Professional,\n\n"
                    f"In today's fast-paced digital ecosystem, the difference between leaders and laggards is "
                    f"operational speed. That's why we created {brief.businessName}.\n\n"
                    f"By deploying a cooperative network of specialized digital agents, {product} solves the "
                    f"bottlenecks in your current workflows:\n"
                    f"• Strategy & Research: Real-time intelligence mapped in under 2 minutes.\n"
                    f"• Content Creation: High-converting, platform-specific copy aligned with your brand voice.\n"
                    f"• Analytics & Forecasting: Predictive guardrails that score your content before launching.\n\n"
                    f"Are you ready to see how {brief.businessName} can transform your operations? Reply directly "
                    f"to this email or click the link below to set up your customized workspace.\n\n"
                    f"Best regards,\n"
                    f"The {brief.businessName} Team"
                ),
                "sequence": 1,
                "sendDay": 1,
                "triggerCondition": "User registers a workspace or requests a campaign package",
                "goal": "Introduce core value propositions, build trust, and drive initial workspace onboarding",
                "audienceFocus": audience,
            },
            {
                "subject": f"Case Study: How scaling teams save 40+ hours per week using {product}",
                "preview": "See the exact workflow blueprint boutique agencies and startups use to multiply output.",
                "body": (
                    f"Hello,\n\n"
                    f"Operational bottlenecks cost businesses thousands of dollars in lost productivity every month. "
                    f"We recently sat down with a growth agency director who was managing campaigns for multiple clients.\n\n"
                    f"Here is what they accomplished with {brief.businessName} in just one week:\n"
                    f"1. Cut client brief onboarding time from 3 days to 15 minutes.\n"
                    f"2. Automated the creation of all search-optimized ad copies and social assets.\n"
                    f"3. Reallocated $8,500 of ad spend based on the Predictive Analytics Agent's forecasts.\n\n"
                    f"The result? A 40% reduction in overhead costs and a 2.5x increase in client delivery speed.\n\n"
                    f"You don't need to expand your headcount to multiply your output. Click below to read the full case "
                    f"study and unlock your agency growth plan.\n\n"
                    f"Warmly,\n"
                    f"The {brief.businessName} Growth Group"
                ),
                "sequence": 2,
                "sendDay": 3,
                "triggerCondition": "3 days post-onboarding if first campaign run is completed",
                "goal": "Deliver deep social proof, address common objections, and demonstrate real-world ROI",
                "audienceFocus": audience,
            },
            {
                "subject": "Unlocking predictive ROI: Your final step to campaign launch",
                "preview": "Ensure your marketing dollars are spent on validated, high-performing creatives.",
                "body": (
                    f"Hi there,\n\n"
                    f"Launching a marketing campaign without pre-validating your creative is like driving in the dark "
                    f"without headlights. That's why the Analytics Agent inside {brief.businessName} is so critical.\n\n"
                    f"Our proprietary predictive scoring evaluates:\n"
                    f"• Message Alignment: Does the copy speak directly to {audience}?\n"
                    f"• Call to Action Strength: Is the CTA optimized for the designated funnel stage?\n"
                    f"• Platform Consistency: Does the format match the channel's best practices?\n\n"
                    f"If you're ready to take the guesswork out of your campaign spend, let's launch your first live "
                    f"validated sequence. Click the button below to review your scorecard and approve the publication.\n\n"
                    f"Best, \n"
                    f"Customer Success at {brief.businessName}"
                ),
                "sequence": 3,
                "sendDay": 5,
                "triggerCondition": "5 days post-onboarding or immediately after Analytics Quality Gate review",
                "goal": "Drive premium subscription upgrades and encourage active pipeline execution",
                "audienceFocus": audience,
            },
        ],
        "socialPosts": [
            {
                "platform": "LinkedIn",
                "content": (
                    f"Traditional marketing structures are changing. With {brief.businessName}, you can deploy "
                    f"a multi-agent network to research markets, write high-converting copy, and design creative assets "
                    f"in under 5 minutes. Optimize your workflow, save time, and deliver superior marketing solutions."
                ),
                "hashtags": ["b2bmarketing", "ai", "workflowautomation", "productivity", "management"],
                "imagePrompt": (
                    "Futuristic abstract digital diagram with node points representing Strategy, Research, Content, "
                    "Analytics, and Design agents working in harmony, sleek blue and violet neon grid backdrop."
                ),
                "postType": "Thought Leadership Image Post",
                "bestTimeToPost": "Tuesday at 9:00 AM EST",
                "captionCopy": (
                    f"Traditional marketing structures are changing. With {brief.businessName}, you can deploy "
                    f"a multi-agent network to research markets, write high-converting copy, and design creative assets "
                    f"in under 5 minutes. Optimize your workflow, save time, and deliver superior marketing solutions."
                ),
            },
            {
                "platform": "Instagram",
                "content": (
                    f"Scale your brand's creative without scaling the cost. 🚀 {brief.businessName} automates high-end "
                    f"ad copy, email sequences, and visual briefs tailored specifically to your audience. Ready to win?"
                ),
                "hashtags": ["digitalmarketing", "entrepreneurlife", "creativeads", "saasgrowth"],
                "imagePrompt": (
                    "Minimalist home workspace, modern wooden desk holding a laptop with glowing screen, "
                    "framed by soft foliage shadows and warm golden hour sunlight, clean high-fashion aesthetic."
                ),
                "postType": "Creative Spotlight Feed Post",
                "bestTimeToPost": "Thursday at 5:00 PM EST",
                "captionCopy": (
                    f"Scale your brand's creative without scaling the cost. 🚀 {brief.businessName} automates high-end "
                    f"ad copy, email sequences, and visual briefs tailored specifically to your audience. Ready to win?"
                ),
            },
            {
                "platform": "Twitter",
                "content": (
                    f"Run entire campaigns on autopilot. ⚡ Provide {brief.businessName} with your product details and "
                    f"audience parameters, and watch our multi-agent architecture build your campaign roadmap instantly."
                ),
                "hashtags": ["growthmarketing", "startups", "martech", "automation"],
                "imagePrompt": (
                    "Bold digital canvas displaying clean modern san-serif typography: 'AGENTIC MARKETING' layered "
                    "over translucent glassmorphic shapes and a subtle mesh gradient background."
                ),
                "postType": "Quick Insight Text Post",
                "bestTimeToPost": "Wednesday at 11:30 AM EST",
                "captionCopy": (
                    f"Run entire campaigns on autopilot. ⚡ Provide {brief.businessName} with your product details and "
                    f"audience parameters, and watch our multi-agent architecture build your campaign roadmap instantly."
                ),
            },
        ],
        "summary": (
            f"Successfully compiled professional campaign roadmap for '{brief.businessName}'. "
            f"Ready for review and export."
        ),
    }


async def _run_dashboard_task(task_id: str, brief: FrontendCampaignBrief) -> None:
    steps = [
        (15, "Preparing campaign brief"),
        (35, "Running strategy and research agents"),
        (60, "Generating content package"),
        (82, "Evaluating campaign quality"),
    ]
    try:
        for progress, message in steps:
            await _repo.update_task(task_id, status="in_progress", progress=progress, message=message)
            await asyncio.sleep(0.35)

        if _provider_key_is_configured():
            manager = _get_task_manager()
            result = await manager.run(OrchestratorInput(campaign=_to_campaign_input(brief)))
            content = _frontend_content_from_pipeline(result)
        else:
            content = _demo_content(brief)

        await _repo.set_content(task_id, content)
    except Exception as exc:
        await _repo.set_error(task_id, str(exc))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Liveness probe",
    tags=["System"],
)
async def healthz() -> HealthResponse:
    """Return 200 when the API server is running."""
    return HealthResponse()


@app.post(
    "/api/campaigns",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a dashboard campaign brief",
    tags=["Dashboard"],
    dependencies=[Depends(verify_api_key)],
)
async def submit_dashboard_campaign(request: Request, payload: FrontendCampaignBrief) -> TaskResponse:
    """Start a dashboard-friendly campaign task.

    By default this returns professional local demo output so the dashboard
    can be tested without burning API credits, unless LIVE_MODE is set.
    """
    from ..worker import run_dashboard_task
    task_id = f"campaign-{uuid4().hex[:12]}"
    await _repo.create_task(task_id, brief_json=json.dumps(payload.model_dump()))
    
    # Fallback to local asyncio task since Docker/Redis isn't running
    asyncio.create_task(run_dashboard_task(None, task_id, payload.model_dump()))
    
    return TaskResponse(taskId=task_id, status="pending", progress=0, message="Campaign queued")


@app.get(
    "/api/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get dashboard task status",
    tags=["Dashboard"],
)
async def get_dashboard_task(request: Request, task_id: str) -> TaskResponse:
    """Return task progress for the React dashboard polling hook."""
    task = await _repo.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse(**task)


@app.get(
    "/api/campaigns/{campaign_id}/content",
    summary="Get dashboard campaign content",
    tags=["Dashboard"],
)
async def get_dashboard_campaign_content(campaign_id: str) -> Dict[str, Any]:
    """Return frontend-shaped content for a completed dashboard campaign."""
    task = await _repo.get_task(campaign_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if task["status"] == "failed":
        error = await _repo.get_error(campaign_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error or "Campaign generation failed",
        )
    content = await _repo.get_content(campaign_id)
    if content is None:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Campaign is still running")
    return content


@app.get(
    "/api/campaigns/{campaign_id}/design-assets/download",
    summary="Download dashboard design assets",
    tags=["Dashboard"],
)
async def download_dashboard_design_assets(campaign_id: str) -> StreamingResponse:
    """Package and download campaign assets as a ZIP archive."""
    task = await _repo.get_task(campaign_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    content = await _repo.get_content(campaign_id)
    buffer = AssetPackager.package_campaign(campaign_id, content)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="campaign-{campaign_id}-assets.zip"',
        },
    )


@app.post(
    "/api/analytics/evaluate",
    response_model=AnalyticsEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Standalone Analytics Quality Gate",
    description=(
        "Accepts a fully-assembled ``AnalyticsAgentInput`` "
        "(campaign + strategy + research + content) and runs only the "
        "Analytics Agent.  Returns the scored output plus the gate decision "
        "and any improvement recommendations for the frontend to display."
    ),
    tags=["Analytics"],
    dependencies=[Depends(verify_api_key)],
)
async def evaluate_analytics(
    request: Request,
    payload: AnalyticsAgentInput,
) -> AnalyticsEvaluationResponse:
    """Trigger the Analytics Quality Gate evaluation for a given input payload.

    This endpoint is the primary integration point for the React dashboard
    and external microservices that want to check campaign health without
    running the full pipeline.

    - **gate_passed** – ``true`` when ``health_score ≥ 70``
    - **optimization_recommendations** – high/medium priority suggestions
      returned when the gate fails, ready to pass back to ContentAgent
    """
    manager = _get_task_manager()

    logger.info(
        "POST /api/analytics/evaluate | business=%s",
        payload.campaign.business_name,
    )

    try:
        analytics_output = await manager.evaluate(payload)
    except Exception as exc:
        logger.error("Analytics evaluation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics evaluation failed: {exc}",
        ) from exc

    gate_passed = AnalyticsAgent.passes_quality_gate(analytics_output)
    recommendations = AnalyticsAgent.extract_optimization_recommendations(analytics_output)

    logger.info(
        "POST /api/analytics/evaluate | score=%.2f | gate_passed=%s | recommendations=%d",
        analytics_output.health_score.overall,
        gate_passed,
        len(recommendations),
    )

    return AnalyticsEvaluationResponse(
        gate_passed=gate_passed,
        health_score=analytics_output.health_score.overall,
        optimization_recommendations=recommendations,
        analytics=analytics_output,
    )


@app.post(
    "/api/campaigns/run",
    response_model=CampaignRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run full campaign pipeline",
    description=(
        "Accepts a ``CampaignInput`` and runs the complete DAG: "
        "Strategy → Research → Content → Analytics (with quality-gate retry) "
        "→ Design → Campaign Manager.  The response includes the full "
        "``OrchestratorOutput`` and a top-level summary of the pipeline result."
    ),
    tags=["Pipeline"],
    dependencies=[Depends(verify_api_key)],
)
async def run_campaign(
    request: Request,
    campaign: CampaignInput,
) -> CampaignRunResponse:
    """Trigger the full AdPilot multi-agent DAG for a given campaign.

    The pipeline enforces the Analytics quality gate internally:
    if the health score is below **70**, ContentAgent is automatically
    retried (up to 3 times) with the improvement recommendations injected
    into its prompt.  The final result is returned regardless of gate status.
    """
    manager = _get_task_manager()

    logger.info(
        "POST /api/campaigns/run | business=%s | budget=%.0f",
        campaign.business_name,
        campaign.budget_usd,
    )

    try:
        result = await manager.run(OrchestratorInput(campaign=campaign))
    except Exception as exc:
        logger.error("Campaign pipeline error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {exc}",
        ) from exc

    gate_passed = AnalyticsAgent.passes_quality_gate(result.analytics)
    retries = sum(1 for r in result.agent_run_records if "_retry_" in r.agent_name)

    return CampaignRunResponse(
        gate_passed=gate_passed,
        final_health_score=result.analytics.health_score.overall,
        content_retries=retries,
        pipeline=result,
    )


# Apply rate limiting if slowapi is available
if _HAS_SLOWAPI and limiter is not None:
    evaluate_analytics = limiter.limit("30/minute")(evaluate_analytics)
    run_campaign = limiter.limit("30/minute")(run_campaign)
    get_dashboard_task = limiter.limit("120/minute")(get_dashboard_task)


# ---------------------------------------------------------------------------
# Phase 3 REST Dashboard & Enterprise APIs
# ---------------------------------------------------------------------------

@app.get(
    "/api/campaigns",
    summary="List all campaign tasks",
    tags=["Dashboard"],
)
async def list_campaigns() -> List[Dict[str, Any]]:
    """Return a list of all campaign tasks from database."""
    from sqlalchemy import select
    from ..core.database import async_session_factory
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        result = await session.execute(
            select(CampaignTask).order_by(CampaignTask.created_at.desc())
        )
        tasks = result.scalars().all()
        return [
            {
                "campaignId": t.task_id,
                "status": t.status,
                "progress": t.progress,
                "message": t.message,
                "createdAt": t.created_at.isoformat() if t.created_at else None,
                "updatedAt": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in tasks
        ]


@app.get(
    "/api/campaigns/{campaign_id}",
    summary="Retrieve a specific campaign task details",
    tags=["Dashboard"],
)
async def get_campaign(campaign_id: str) -> Dict[str, Any]:
    """Return the campaign task brief, status, progress and messages."""
    from sqlalchemy import select
    from ..core.database import async_session_factory
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        result = await session.execute(
            select(CampaignTask).where(CampaignTask.task_id == campaign_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "campaignId": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "message": task.message,
            "brief": json.loads(task.brief_json) if task.brief_json else None,
            "errorMessage": task.error_message,
            "createdAt": task.created_at.isoformat() if task.created_at else None,
            "updatedAt": task.updated_at.isoformat() if task.updated_at else None,
        }


@app.delete(
    "/api/campaigns/{campaign_id}",
    summary="Delete a campaign task",
    tags=["Dashboard"],
)
async def delete_campaign(campaign_id: str) -> Dict[str, str]:
    """Delete a campaign task from the database."""
    from sqlalchemy import select
    from ..core.database import async_session_factory
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        result = await session.execute(
            select(CampaignTask).where(CampaignTask.task_id == campaign_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        await session.delete(task)
        await session.commit()
        return {"status": "deleted", "campaignId": campaign_id}


@app.get(
    "/api/campaigns/{campaign_id}/assets",
    summary="Get generated assets for a campaign",
    tags=["Dashboard"],
)
async def get_campaign_assets(campaign_id: str) -> Dict[str, Any]:
    """Return ads, social posts, emails, design briefs, generated visuals from campaign context."""
    from sqlalchemy import select
    from ..core.database import async_session_factory
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        result = await session.execute(
            select(CampaignTask).where(CampaignTask.task_id == campaign_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Campaign not found")
        if not task.content_json:
            raise HTTPException(status_code=202, detail="Campaign is still running or failed")

        content = json.loads(task.content_json)
        return {
            "campaignId": campaign_id,
            "ads": content.get("ads", []),
            "emailSequences": content.get("emailSequences", []),
            "socialPosts": content.get("socialPosts", []),
            "designBriefs": content.get("designBriefs", []),
            "visuals": content.get("visuals", []),
        }


@app.get(
    "/api/campaigns/{campaign_id}/status",
    summary="Get detailed agent status and run records",
    tags=["Dashboard"],
)
async def get_campaign_status(campaign_id: str) -> Dict[str, Any]:
    """Return task progress and status breakdown of run records."""
    from sqlalchemy import select
    from ..core.database import async_session_factory
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        result = await session.execute(
            select(CampaignTask).where(CampaignTask.task_id == campaign_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Campaign not found")

        agent_records = []
        if task.content_json:
            try:
                content = json.loads(task.content_json)
                pipeline_data = content.get("pipeline", {})
                agent_records = pipeline_data.get("agent_run_records", [])
            except Exception:
                pass

        return {
            "campaignId": campaign_id,
            "status": task.status,
            "progress": task.progress,
            "message": task.message,
            "agentRunRecords": agent_records,
        }


@app.get(
    "/api/campaigns/{campaign_id}/analytics",
    summary="Get analytics for a campaign",
    tags=["Dashboard"],
)
async def get_campaign_analytics(campaign_id: str) -> Dict[str, Any]:
    """Return campaign health score and predicted metrics."""
    from sqlalchemy import select
    from ..core.database import async_session_factory
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        result = await session.execute(
            select(CampaignTask).where(CampaignTask.task_id == campaign_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Campaign not found")
        if not task.content_json:
            raise HTTPException(status_code=202, detail="Campaign content not ready")

        content = json.loads(task.content_json)
        pipeline_data = content.get("pipeline", {})
        analytics_data = pipeline_data.get("analytics", {})
        
        health_score = analytics_data.get("health_score", {}).get("overall", 85.0)
        predicted_metrics = analytics_data.get("predicted_metrics", [
            {"metric": "ctr", "predicted_value": 4.5, "confidence": 85.0, "basis": "Demo historical"},
            {"metric": "cpc", "predicted_value": 1.5, "confidence": 90.0, "basis": "Demo historical"},
        ])
        kpi_targets = analytics_data.get("kpi_targets", None)

        return {
            "campaignId": campaign_id,
            "overallHealthScore": health_score,
            "predictedMetrics": predicted_metrics,
            "kpiTargets": kpi_targets,
        }


@app.get(
    "/api/campaigns/{campaign_id}/reports",
    summary="Get campaign reports and optimization suggestions",
    tags=["Dashboard"],
)
async def get_campaign_reports(campaign_id: str) -> Dict[str, Any]:
    """Return campaign executive summary and improvement suggestions."""
    from sqlalchemy import select
    from ..core.database import async_session_factory
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        result = await session.execute(
            select(CampaignTask).where(CampaignTask.task_id == campaign_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Campaign not found")
        if not task.content_json:
            raise HTTPException(status_code=202, detail="Campaign content not ready")

        content = json.loads(task.content_json)
        pipeline_data = content.get("pipeline", {})
        analytics_data = pipeline_data.get("analytics", {})
        
        executive_summary = analytics_data.get("executive_summary", "Campaign roadmap ready.")
        suggestions = analytics_data.get("improvement_suggestions", [])
        ab_tests = analytics_data.get("ab_test_recommendations", [])

        return {
            "campaignId": campaign_id,
            "executiveSummary": executive_summary,
            "improvementSuggestions": suggestions,
            "abTestRecommendations": ab_tests,
        }


@app.post(
    "/api/knowledge/upload",
    summary="Upload company knowledge documents for RAG",
    tags=["Dashboard"],
)
async def upload_document(
    campaign_id: str = Form(...),
    doc_type: Optional[str] = Form(None),
    file: UploadFile = File(...),
) -> Dict[str, str]:
    """Upload PDF, brand guidelines, or marketing document, parse it and store in ChromaDB."""
    os.makedirs("./data/uploads", exist_ok=True)
    file_path = f"./data/uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        rag_service = get_container().rag_service
        await rag_service.process_file(file_path, campaign_id, file.filename)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and index file in RAG: {exc}",
        )

    return {
        "status": "success",
        "message": f"Successfully indexed '{file.filename}' into campaign '{campaign_id}' context.",
        "campaignId": campaign_id,
        "docType": doc_type or "unspecified",
    }


@app.post(
    "/api/optimizer/evaluate",
    summary="Evaluate campaign metrics against targets",
    tags=["Optimizer"],
)
async def evaluate_optimizer(
    metrics: CampaignMetrics,
    targets: CampaignTargets,
) -> Dict[str, Any]:
    """Run the rule engine on campaign metrics and return optimization recommendations."""
    optimizer = AIOptimizer()
    recommendations = optimizer.evaluate(metrics, targets)
    return {
        "metrics": metrics.model_dump(),
        "targets": targets.model_dump(),
        "recommendations": [r.model_dump() for r in recommendations],
    }


# ---------------------------------------------------------------------------
# Phase 4 SaaS REST & Workspace Endpoints
# ---------------------------------------------------------------------------



class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "viewer"
    organizationName: Optional[str] = None
    organizationId: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class PublishRequest(BaseModel):
    channel: str
    scheduledAt: Optional[str] = None  # ISO-8601 string


@app.post(
    "/api/auth/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a SaaS user and tenant organization",
    tags=["SaaS Auth"],
)
async def register_user(payload: RegisterRequest) -> Dict[str, Any]:
    """Create a new user account and optional tenant organization workspace."""
    from ..core.database import async_session_factory
    from sqlalchemy import select

    async with async_session_factory() as session:
        # Check if user already exists
        dup_res = await session.execute(
            select(UserORM).where(UserORM.email == payload.email)
        )
        if dup_res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User email already registered")

        org_id = payload.organizationId
        if payload.organizationName:
            org_id = f"org-{uuid4().hex[:12]}"
            new_org = OrgORM(id=org_id, name=payload.organizationName)
            session.add(new_org)
            logger.info("Created organization: %s", payload.organizationName)

        user_id = f"user-{uuid4().hex[:12]}"
        # Mock password hashing
        hashed = f"mock_hash_{payload.password}"
        
        new_user = UserORM(
            id=user_id,
            email=payload.email,
            hashed_password=hashed,
            role=payload.role,
            organization_id=org_id,
        )
        session.add(new_user)
        
        await session.commit()
        logger.info("Registered user %s with role %s", payload.email, payload.role)
        
        return {
            "userId": user_id,
            "email": payload.email,
            "role": payload.role,
            "organizationId": org_id,
        }


@app.post(
    "/api/auth/login",
    summary="User authentication login",
    tags=["SaaS Auth"],
)
async def login_user(payload: LoginRequest) -> Dict[str, Any]:
    """Authenticate credentials and exchange for a Bearer session token."""
    from ..core.database import async_session_factory
    from sqlalchemy import select

    async with async_session_factory() as session:
        result = await session.execute(
            select(UserORM).where(UserORM.email == payload.email)
        )
        user = result.scalar_one_or_none()
        if not user or user.hashed_password != f"mock_hash_{payload.password}":
            raise HTTPException(status_code=401, detail="Invalid email or password")

        await log_action(
            session=session,
            user_id=user.id,
            organization_id=user.organization_id,
            action="user_login",
            entity_type="user",
            entity_id=user.id,
        )
        await session.commit()

        return {
            "token": user.id,
            "email": user.email,
            "role": user.role,
            "organizationId": user.organization_id,
        }


@app.post(
    "/api/campaigns/{campaign_id}/publish",
    summary="Publish or schedule campaign creative assets",
    tags=["SaaS Publishing"],
)
async def publish_campaign_asset(
    campaign_id: str,
    payload: PublishRequest,
    user: UserORM = Depends(require_role(["admin", "marketer"])),
) -> Dict[str, Any]:
    """Publish generated ad copy or schedule posts for a specific platform channel."""
    from ..core.database import async_session_factory
    from sqlalchemy import select
    from ..models.campaign_task import CampaignTask

    async with async_session_factory() as session:
        # Fetch target campaign task
        task_res = await session.execute(
            select(CampaignTask).where(CampaignTask.task_id == campaign_id)
        )
        task = task_res.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Campaign not found")

        pub_id = f"pub-{uuid4().hex[:12]}"
        
        # Parse scheduled_at if provided
        scheduled_at = None
        if payload.scheduledAt:
            try:
                # Basic ISO string parsing, strip 'Z' if present
                clean_iso = payload.scheduledAt.replace("Z", "+00:00")
                scheduled_at = datetime.fromisoformat(clean_iso)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {exc}")

        if scheduled_at:
            # Add to schedule queue
            new_pub = PublishORM(
                id=pub_id,
                campaign_id=campaign_id,
                channel=payload.channel,
                status="scheduled",
                scheduled_at=scheduled_at,
            )
            session.add(new_pub)
            await log_action(
                session=session,
                user_id=user.id,
                organization_id=user.organization_id,
                action="schedule_publish",
                entity_type="publication",
                entity_id=pub_id,
                payload={"channel": payload.channel, "scheduledAt": payload.scheduledAt},
            )
            await session.commit()
            return {
                "publicationId": pub_id,
                "status": "scheduled",
                "channel": payload.channel,
                "scheduledAt": payload.scheduledAt,
            }
        
        # Publish instantly
        if not task.content_json:
            raise HTTPException(status_code=400, detail="Campaign assets are not ready for publishing.")

        content = json.loads(task.content_json)
        
        # Locate asset
        asset = {}
        clean_channel = payload.channel.lower()
        if "facebook" in clean_channel or "instagram" in clean_channel or "meta" in clean_channel:
            ads = content.get("ads", [])
            asset = next((ad for ad in ads if ad.get("platform", "").lower() in ("facebook", "instagram")), ads[0] if ads else {})
        elif "google" in clean_channel:
            ads = content.get("ads", [])
            asset = next((ad for ad in ads if "google" in ad.get("platform", "").lower()), ads[0] if ads else {})
        else:
            posts = content.get("socialPosts", [])
            asset = next((p for p in posts if p.get("platform", "").lower() == clean_channel), posts[0] if posts else {})

        res = await dispatch_publish(payload.channel, campaign_id, asset)
        
        new_pub = PublishORM(
            id=pub_id,
            campaign_id=campaign_id,
            channel=payload.channel,
            status="published" if res.get("status") == "success" else "failed",
            published_at=datetime.now(timezone.utc) if res.get("status") == "success" else None,
            platform_post_id=res.get("platform_post_id"),
            error_message=res.get("error"),
        )
        session.add(new_pub)
        
        if res.get("status") == "success":
            await log_action(
                session=session,
                user_id=user.id,
                organization_id=user.organization_id,
                action="publish_campaign",
                entity_type="publication",
                entity_id=pub_id,
                payload={"channel": payload.channel, "platform_post_id": res.get("platform_post_id")},
            )
        
        await session.commit()
        return {
            "publicationId": pub_id,
            "status": new_pub.status,
            "platformPostId": new_pub.platform_post_id,
            "errorMessage": new_pub.error_message,
        }


@app.get(
    "/api/campaigns/{campaign_id}/analytics/live",
    summary="Get real-time marketing metrics from social feeds",
    tags=["SaaS Analytics"],
)
async def get_live_analytics(
    campaign_id: str,
    platform: str = "meta",
    user: UserORM = Depends(get_current_user),
) -> Dict[str, Any]:
    """Fetch live time-series performance dashboards from Google, Meta, or LinkedIn."""
    connector = LiveAnalyticsConnector()
    try:
        return connector.fetch_live_metrics(campaign_id, platform)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get(
    "/api/audit-logs",
    summary="List tenant audit trail logs",
    tags=["SaaS Security"],
)
async def list_audit_logs(
    user: UserORM = Depends(require_role(["admin"])),
) -> List[Dict[str, Any]]:
    """Retrieve database log actions (Admin only)."""
    from ..core.database import async_session_factory
    from sqlalchemy import select

    async with async_session_factory() as session:
        result = await session.execute(
            select(AuditORM).order_by(AuditORM.created_at.desc())
        )
        logs = result.scalars().all()
        return [
            {
                "id": log_entry.id,
                "userId": log_entry.user_id,
                "organizationId": log_entry.organization_id,
                "action": log_entry.action,
                "entityType": log_entry.entity_type,
                "entityId": log_entry.entity_id,
                "payload": json.loads(log_entry.payload_json) if log_entry.payload_json else None,
                "createdAt": log_entry.created_at.isoformat() if log_entry.created_at else None,
            }
            for log_entry in logs
        ]


@app.get(
    "/health",
    summary="SaaS Health Check",
    tags=["System"],
)
async def health_check() -> Dict[str, Any]:
    """Verify uvicorn runtime and database connection availability."""
    from ..core.database import async_session_factory
    from sqlalchemy import text

    db_healthy = False
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_healthy = True
    except Exception as exc:
        logger.error("Health check database error: %s", exc)

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

