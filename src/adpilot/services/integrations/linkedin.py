"""LinkedIn API integration client mockup."""

from __future__ import annotations

import asyncio
from uuid import uuid4
from typing import Any, Dict
from ...utils.logging_utils import logger
from .base import IntegrationClient


class LinkedInClient(IntegrationClient):
    """Mock API client for LinkedIn posts and updates."""

    async def publish_asset(self, campaign_id: str, asset: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(
            "LinkedInClient | Publishing post to LinkedIn. Campaign=%s, ContentSnippet=%s",
            campaign_id,
            asset.get("content", "Default Content")[:30] + "...",
        )
        await asyncio.sleep(0.05)
        
        post_id = f"urn:li:share:{uuid4().hex[:12]}"
        return {
            "status": "success",
            "platform_post_id": post_id,
            "channel": "linkedin",
        }
