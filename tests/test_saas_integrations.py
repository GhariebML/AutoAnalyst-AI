import pytest
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import select
from adpilot.core.database import async_session_factory
from adpilot.models.campaign_task import CampaignTask
from adpilot.models.campaign_publish import CampaignPublish
from adpilot.models.audit_log import AuditLog
from adpilot.services.integrations import dispatch_publish
from adpilot.services.scheduler import PublishScheduler


@pytest.mark.anyio
async def test_integration_clients_dispatch():
    """Verify dispatch_publish maps to correct platform mock clients."""
    asset = {"headline": "Build faster with AI", "content": "AdPilot helps scale marketing"}
    
    # Meta Ads
    res = await dispatch_publish("meta", "campaign-123", asset)
    assert res["status"] == "success"
    assert "meta" in res["platform_post_id"]
    assert res["channel"] == "facebook"

    # Google Ads
    res = await dispatch_publish("google_ads", "campaign-123", asset)
    assert res["status"] == "success"
    assert "gads" in res["platform_post_id"]
    assert res["channel"] == "google"

    # LinkedIn
    res = await dispatch_publish("linkedin", "campaign-123", asset)
    assert res["status"] == "success"
    assert "urn:li:share" in res["platform_post_id"]
    assert res["channel"] == "linkedin"

    # Buffer
    res = await dispatch_publish("buffer", "campaign-123", asset)
    assert res["status"] == "success"
    assert "buf_update" in res["platform_post_id"]
    assert res["channel"] == "buffer"

    # Unknown
    res = await dispatch_publish("tiktok", "campaign-123", asset)
    assert res["status"] == "failed"
    assert "Unsupported publishing channel" in res["error"]


@pytest.mark.anyio
async def test_scheduler_background_publish():
    """Verify PublishScheduler pulls scheduled assets, publishes them, updates database, and audit logs."""
    campaign_id = f"camp-{uuid4().hex[:8]}"
    pub_id = f"pub-{uuid4().hex[:8]}"
    past_time = datetime.now(timezone.utc) - timedelta(minutes=1)

    async with async_session_factory() as session:
        # Create campaign with generated content
        task = CampaignTask(
            task_id=campaign_id,
            status="completed",
            progress=100,
            content_json=json.dumps({
                "ads": [{"platform": "Facebook", "headline": "Main Ad Title", "body": "Meta ad body"}],
                "socialPosts": [{"platform": "LinkedIn", "content": "LinkedIn post content"}],
            }),
            user_id="user-123",
            organization_id="org-456",
        )
        session.add(task)

        # Create scheduled publication
        pub = CampaignPublish(
            id=pub_id,
            campaign_id=campaign_id,
            channel="meta",
            status="scheduled",
            scheduled_at=past_time,
        )
        session.add(pub)
        await session.commit()

    # Trigger scheduler tick
    scheduler = PublishScheduler(session_factory=async_session_factory)
    await scheduler.check_and_publish()

    # Verify changes
    async with async_session_factory() as session:
        pub_res = await session.execute(
            select(CampaignPublish).where(CampaignPublish.id == pub_id)
        )
        db_pub = pub_res.scalar_one()
        assert db_pub.status == "published"
        assert db_pub.platform_post_id is not None
        assert db_pub.published_at is not None

        # Verify Audit Log
        audit_res = await session.execute(
            select(AuditLog).where(AuditLog.entity_id == pub_id)
        )
        db_audit = audit_res.scalar_one_or_none()
        assert db_audit is not None
        assert db_audit.action == "publish_campaign"
        assert db_audit.user_id == "user-123"
        assert db_audit.organization_id == "org-456"
