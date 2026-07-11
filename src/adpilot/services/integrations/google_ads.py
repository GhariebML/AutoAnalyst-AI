"""Google Ads API integration client mockup."""

from __future__ import annotations

import asyncio
from uuid import uuid4
from typing import Any, Dict
from ...utils.logging_utils import logger
from .base import IntegrationClient


class GoogleAdsClient(IntegrationClient):
    """Mock API client for Google Ads."""

    async def publish_asset(self, campaign_id: str, asset: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(
            "GoogleAdsClient | Publishing creative to Google Ads. Campaign=%s, Headline=%s",
            campaign_id,
            asset.get("headline", "Default Headline"),
        )
        await asyncio.sleep(0.05)
        
        post_id = f"gads_campaign_{uuid4().hex[:12]}"
        return {
            "status": "success",
            "platform_post_id": post_id,
            "channel": "google",
        }
