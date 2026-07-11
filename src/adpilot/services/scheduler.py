"""Async background worker for scheduled publishing."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from typing import Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from ..utils.logging_utils import logger
from ..models.campaign_publish import CampaignPublish
from ..models.campaign_task import CampaignTask
from .integrations import dispatch_publish
from .audit_service import log_action


class PublishScheduler:
    """Manages background polling and publishing of scheduled campaign assets."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession], interval_seconds: float = 1.0) -> None:
        self.session_factory = session_factory
        self.interval_seconds = interval_seconds
        self._task: asyncio.Task[None] | None = None
        self._running = False

    def start(self) -> None:
        """Start the background scheduler task."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("PublishScheduler started background worker loop.")

    async def stop(self) -> None:
        """Stop the background scheduler task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("PublishScheduler background worker stopped.")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self.check_and_publish()
            except Exception as exc:
                logger.error("PublishScheduler loop error: %s", exc)
            await asyncio.sleep(self.interval_seconds)

    async def check_and_publish(self) -> None:
        """Query and execute pending scheduled publication items."""
        now = datetime.now(timezone.utc)
        async with self.session_factory() as session:
            # Fetch scheduled items due for publication
            result = await session.execute(
                select(CampaignPublish).where(
                    CampaignPublish.status == "scheduled",
                    CampaignPublish.scheduled_at <= now,
                )
            )
            publishes = result.scalars().all()
            if not publishes:
                return

            for pub in publishes:
                logger.info(
                    "Scheduler | Triggering publish for item %s, channel %s, campaign %s",
                    pub.id,
                    pub.channel,
                    pub.campaign_id,
                )
                
                # Fetch campaign task to get creative content JSON
                task_res = await session.execute(
                    select(CampaignTask).where(CampaignTask.task_id == pub.campaign_id)
                )
                task = task_res.scalar_one_or_none()
                if not task or not task.content_json:
                    pub.status = "failed"
                    pub.error_message = "Associated campaign content not found or generation not completed."
                    continue

                try:
                    content = json.loads(task.content_json)
                    # Find asset from generated content list corresponding to the channel
                    asset = self._find_asset_for_channel(content, pub.channel)
                    
                    # Execute publish client
                    res = await dispatch_publish(pub.channel, pub.campaign_id, asset)
                    
                    if res.get("status") == "success":
                        pub.status = "published"
                        pub.published_at = datetime.now(timezone.utc)
                        pub.platform_post_id = res.get("platform_post_id")
                        
                        # Log Audit Event
                        await log_action(
                            session=session,
                            user_id=task.user_id,
                            organization_id=task.organization_id,
                            action="publish_campaign",
                            entity_type="publication",
                            entity_id=pub.id,
                            payload={"channel": pub.channel, "platform_post_id": pub.platform_post_id},
                        )
                    else:
                        pub.status = "failed"
                        pub.error_message = res.get("error", "Unknown publishing error")
                except Exception as exc:
                    pub.status = "failed"
                    pub.error_message = str(exc)
                    logger.exception("Failed to execute scheduled publication: %s", exc)

            await session.commit()

    def _find_asset_for_channel(self, content: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """Extract suitable text/image payloads based on content schema and channels."""
        clean_channel = channel.lower()
        if "facebook" in clean_channel or "instagram" in clean_channel or "meta" in clean_channel:
            ads = content.get("ads", [])
            for ad in ads:
                if ad.get("platform", "").lower() in ("facebook", "instagram"):
                    return ad
            return ads[0] if ads else {}
        elif "google" in clean_channel:
            ads = content.get("ads", [])
            for ad in ads:
                if "google" in ad.get("platform", "").lower():
                    return ad
            return ads[0] if ads else {}
        else:
            posts = content.get("socialPosts", [])
            for post in posts:
                if post.get("platform", "").lower() == clean_channel:
                    return post
            return posts[0] if posts else {}
