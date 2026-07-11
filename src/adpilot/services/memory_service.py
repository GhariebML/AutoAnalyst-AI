"""Memory service abstraction for campaign context storage."""

from __future__ import annotations

import abc
from typing import Dict, Optional

from ..schemas.agent_schemas import CampaignContext


class MemoryStorageEngine(abc.ABC):
    """Abstract base class for storage engines."""

    @abc.abstractmethod
    async def get(self, campaign_id: str) -> Optional[CampaignContext]:
        """Retrieve the campaign context by campaign_id."""
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, campaign_id: str, context: CampaignContext) -> None:
        """Save the campaign context by campaign_id."""
        raise NotImplementedError


class InMemoryStorageEngine(MemoryStorageEngine):
    """In-memory storage engine."""

    def __init__(self) -> None:
        self._storage: Dict[str, CampaignContext] = {}

    async def get(self, campaign_id: str) -> Optional[CampaignContext]:
        return self._storage.get(campaign_id)

    async def save(self, campaign_id: str, context: CampaignContext) -> None:
        self._storage[campaign_id] = context


class MongoStorageEngine(MemoryStorageEngine):
    """MongoDB-backed storage engine."""

    def __init__(self, mongodb_url: str, db_name: str = "adpilot", collection_name: str = "campaign_contexts") -> None:
        from motor.motor_asyncio import AsyncIOMotorClient
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def get(self, campaign_id: str) -> Optional[CampaignContext]:
        import json
        doc = await self.collection.find_one({"campaign_id": campaign_id})
        if not doc or "context_json" not in doc:
            return None
        try:
            data = json.loads(doc["context_json"])
            return CampaignContext.model_validate(data)
        except Exception:
            return None

    async def save(self, campaign_id: str, context: CampaignContext) -> None:
        import json
        data_json = json.dumps(context.model_dump(mode="json"))
        await self.collection.update_one(
            {"campaign_id": campaign_id},
            {"$set": {"context_json": data_json}},
            upsert=True
        )


class MemoryService:
    """Service to load and store campaign contexts. Backwards compatible wrapper around MemoryManager."""

    def __init__(self, engine: Optional[MemoryStorageEngine] = None, manager: Optional['MemoryManager'] = None) -> None:
        if manager:
            self.manager = manager
            self.engine = None
        else:
            self.engine = engine or InMemoryStorageEngine()
            self.manager = None

    async def get_context(self, campaign_id: str) -> Optional[CampaignContext]:
        if self.manager:
            return await self.manager.campaign.get(campaign_id)
        elif self.engine:
            return await self.engine.get(campaign_id)
        return None

    async def save_context(self, campaign_id: str, context: CampaignContext) -> None:
        if self.manager:
            await self.manager.campaign.save(campaign_id, context)
        elif self.engine:
            await self.engine.save(campaign_id, context)
