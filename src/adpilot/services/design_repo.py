"""Repository for managing DesignAsset persistence."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.design_asset import DesignAsset


class DesignRepository:
    """Handles CRUD operations for DesignAsset models."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_asset(self, campaign_id: str, task_id: str, prompt: str, **kwargs) -> DesignAsset:
        """Create and persist a new DesignAsset."""
        asset = DesignAsset(campaign_id=campaign_id, task_id=task_id, prompt=prompt, **kwargs)
        self.session.add(asset)
        await self.session.flush()  # To get the ID back
        return asset

    async def get_asset_by_id(self, asset_id: int) -> Optional[DesignAsset]:
        """Retrieve an asset by its primary key."""
        result = await self.session.execute(select(DesignAsset).where(DesignAsset.id == asset_id))
        return result.scalar_one_or_none()

    async def get_assets_by_campaign(self, campaign_id: str) -> Sequence[DesignAsset]:
        """Retrieve all assets for a specific campaign."""
        result = await self.session.execute(
            select(DesignAsset).where(DesignAsset.campaign_id == campaign_id).order_by(DesignAsset.created_at.desc())
        )
        return result.scalars().all()

    async def update_asset_status(
        self,
        asset_id: str,
        status: str,
        image_url: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[DesignAsset]:
        """Update the status and results of an asset."""
        asset = await self.get_asset_by_id(asset_id)
        if asset:
            asset.status = status
            if image_url:
                asset.image_url = image_url
            if error_message:
                asset.error_message = error_message
            await self.session.flush()
        return asset
