"""Integrations package exposing client wrappers and dispatch logic."""

from __future__ import annotations

from typing import Any, Dict

from .base import IntegrationClient as IntegrationClient
from .meta_ads import MetaAdsClient
from .google_ads import GoogleAdsClient
from .linkedin import LinkedInClient
from .buffer import BufferClient


async def dispatch_publish(channel: str, campaign_id: str, asset: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch campaign asset publication to the correct platform client."""
    client_map = {
        "facebook": MetaAdsClient,
        "instagram": MetaAdsClient,
        "meta": MetaAdsClient,
        "google": GoogleAdsClient,
        "google_ads": GoogleAdsClient,
        "linkedin": LinkedInClient,
        "buffer": BufferClient,
    }
    
    clean_channel = channel.strip().lower()
    client_cls = client_map.get(clean_channel)
    if not client_cls:
        return {
            "status": "failed",
            "error": f"Unsupported publishing channel '{channel}'",
        }
    
    client = client_cls()
    return await client.publish_asset(campaign_id, asset)
