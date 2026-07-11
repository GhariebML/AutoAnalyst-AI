"""LongTermMemory for semantic search across previous campaigns and knowledge base."""

import logging
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class LongTermMemory:
    """
    Foundational interface for semantic vector search. 
    In Phase 5, this acts as a stub over MongoDB. In Phase 6, this will integrate with Qdrant.
    """

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = self.db["memories"]

    async def add_memory(self, campaign_id: str, agent_name: str, memory_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store a new memory."""
        from ..schemas.memory_schemas import MemoryRecord
        
        record = MemoryRecord(
            campaign_id=campaign_id,
            agent_name=agent_name,
            memory_type=memory_type,
            content=content,
            metadata=metadata or {}
        )
        
        try:
            await self.collection.insert_one(record.model_dump(mode="json"))
        except Exception as e:
            logger.error(f"Failed to insert long-term memory: {e}")

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Placeholder for semantic search. Currently just returns recent memories.
        Phase 6 will upgrade this to true RAG.
        """
        try:
            # Stub: Just return the most recent memories as a mock for search
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Failed to search long-term memory: {e}")
            return []
