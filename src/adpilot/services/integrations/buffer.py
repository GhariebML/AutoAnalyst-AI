"""Buffer API integration client mockup."""

from __future__ import annotations

import asyncio
from uuid import uuid4
from typing import Any, Dict
from ...utils.logging_utils import logger
from .base import IntegrationClient


class BufferClient(IntegrationClient):
    """Mock API client for Buffer (queuing social updates)."""

    async def publish_asset(self, campaign_id: str, asset: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(
            "BufferClient | Queueing social post to Buffer. Campaign=%s",
            campaign_id,
        )
        await asyncio.sleep(0.05)
        
        post_id = f"buf_update_{uuid4().hex[:12]}"
        return {
            "status": "success",
            "platform_post_id": post_id,
            "channel": "buffer",
        }
