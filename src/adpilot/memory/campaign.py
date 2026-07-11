"""CampaignMemory for storing and retrieving holistic CampaignContext."""

import json
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..schemas.agent_schemas import CampaignContext

logger = logging.getLogger(__name__)

class CampaignMemory:
    """
    Manages loading and saving the holistic CampaignContext.
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "campaign_contexts") -> None:
        self.db = db
        self.collection = self.db[collection_name]

    async def get(self, campaign_id: str) -> Optional[CampaignContext]:
        """Retrieve the campaign context."""
        try:
            doc = await self.collection.find_one({"campaign_id": campaign_id})
            if not doc or "context_json" not in doc:
                return None
            data = json.loads(doc["context_json"])
            return CampaignContext.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to get campaign context for {campaign_id}: {e}")
            return None

    async def save(self, campaign_id: str, context: CampaignContext) -> None:
        """Save the campaign context."""
        try:
            data_json = json.dumps(context.model_dump(mode="json"))
            await self.collection.update_one(
                {"campaign_id": campaign_id},
                {"$set": {"context_json": data_json}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to save campaign context for {campaign_id}: {e}")
