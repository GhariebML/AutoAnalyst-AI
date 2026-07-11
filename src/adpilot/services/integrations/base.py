"""Base integration interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class IntegrationClient(ABC):
    """Abstract base class for all marketing API platform integrations."""

    @abstractmethod
    async def publish_asset(self, campaign_id: str, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Publish the given campaign asset to the target platform.

        Returns a dictionary containing:
        - status: "success" or "failed"
        - platform_post_id: Unique string identifier from the platform
        - error: Error message if failed
        """
        pass
