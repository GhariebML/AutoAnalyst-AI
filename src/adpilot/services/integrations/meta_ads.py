"""Meta Ads API integration client mockup."""

from __future__ import annotations

import asyncio
from uuid import uuid4
from typing import Any, Dict
from ...utils.logging_utils import logger
from .base import IntegrationClient


class MetaAdsClient(IntegrationClient):
    """Mock API client for Meta Ads (Facebook/Instagram)."""

    async def publish_asset(self, campaign_id: str, asset: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(
            "MetaAdsClient | Publishing creative to Meta. Campaign=%s, AssetType=%s",
            campaign_id,
            asset.get("adFormat", "Unknown"),
        )
        await asyncio.sleep(0.05)  # Simulate network latency
        
        post_id = f"act_1084_meta_{uuid4().hex[:12]}"
        return {
            "status": "success",
            "platform_post_id": post_id,
            "channel": "facebook",
        }
