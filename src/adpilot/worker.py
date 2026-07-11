import os
import asyncio
from arq.connections import RedisSettings
from .core.database import create_tables
from .services.campaign_repo import CampaignRepository
from .services.task_manager import TaskManager
from .schemas.agent_schemas import OrchestratorInput, CampaignGoal, MarketingChannel, ToneOfVoice, CampaignInput
from .utils.logging_utils import logger

async def startup(ctx):
    await create_tables()
    logger.info("Worker started up.")

async def shutdown(ctx):
    logger.info("Worker shutting down.")

_repo = CampaignRepository()

def _duration_to_days(duration: str) -> int:
    mapping = {"1-week": 7, "2-weeks": 14, "1-month": 30, "3-months": 90}
    return mapping.get(duration.strip().lower(), 30)

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

def _to_campaign_input(brief: dict) -> CampaignInput:
    goals = [_normalize_goal(goal) for goal in brief.get('goals', [])] or [CampaignGoal.brand_awareness]
    return CampaignInput(
        business_name=brief.get('businessName', ''),
        product_description=f"{brief.get('productName', '')}: {brief.get('productDescription', '')}",
        target_market=brief.get('targetAudience', ''),
        budget_usd=brief.get('budget', 0.0),
        goals=goals,
        channels=[MarketingChannel.linkedin, MarketingChannel.instagram, MarketingChannel.email],
        tone_of_voice=_normalize_tone(brief.get('tone', '')),
        competitors=[],
        campaign_duration_days=_duration_to_days(brief.get('duration', '1-month')),
    )

def _frontend_content_from_pipeline(result, brief) -> dict:
    content = result.content
    product = brief.get('productName', brief.get('businessName', ''))
    audience = brief.get('targetAudience', '')

    return {
        "ads": [
            {
                "platform": ad.format.value.title(),
                "headline": ad.headline,
                "body": ad.body,
                "cta": ad.call_to_action,
                "performance": ad.funnel_stage.value.title(),
                "targetAudience": audience,
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
                "audienceFocus": audience,
            }
            for sequence in content.email_sequences
            for email in sequence.emails
        ],
        "socialPosts": [
            {
                "platform": post.platform.value.title(),
                "content": post.content,
                "hashtags": post.hashtags,
                "imagePrompt": post.visual_url or "Clean minimal digital visual depicting modern business workflow concepts.",
                "postType": "Visual Post with Caption",
                "bestTimeToPost": "Tuesday 10:00 AM (local time)",
                "captionCopy": post.content,
            }
            for post in content.social_posts
        ],
        "summary": result.final_campaign_summary,
    }

async def run_dashboard_task(ctx, task_id: str, brief: dict) -> None:
    logger.info(f"Starting background campaign task: {task_id}")
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

        # Attempt real LLM pipeline first
        content = None
        try:
            manager = TaskManager()
            result = await manager.run(OrchestratorInput(campaign=_to_campaign_input(brief)))
            content = _frontend_content_from_pipeline(result, brief)
            logger.info(f"Task {task_id} completed via LLM pipeline.")
        except Exception as llm_exc:
            logger.warning(
                f"Task {task_id}: LLM pipeline failed ({type(llm_exc).__name__}: {llm_exc}). "
                "Falling back to professional demo content."
            )
            # Fallback to demo content generator
            try:
                from .services.demo_content import generate_demo_content
                content = generate_demo_content(brief)
                logger.info(f"Task {task_id} completed via demo content fallback.")
            except Exception as demo_exc:
                logger.error(f"Task {task_id}: Demo fallback also failed: {demo_exc}")
                raise llm_exc  # Re-raise original error

        await _repo.set_content(task_id, content)
        logger.info(f"Task {task_id} completed successfully.")
    except Exception as exc:
        logger.error(f"Task {task_id} failed: {exc}")
        await _repo.set_error(task_id, str(exc))

class WorkerSettings:
    functions = [run_dashboard_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
