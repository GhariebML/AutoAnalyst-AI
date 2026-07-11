"""MemoryManager orchestrating short-term, long-term, campaign, and agent memory subsystems."""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .agent import AgentMemory
from .campaign import CampaignMemory
from .long_term import LongTermMemory
from .short_term import ShortTermMemory
from ..core.config import get_config

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Central orchestration layer for the AdPilot memory architecture.
    """

    def __init__(self, mongodb_url: Optional[str] = None, db_name: str = "adpilot") -> None:
        self.config = get_config()
        self.mongodb_url = mongodb_url or self.config.mongodb_url
        
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db: AsyncIOMotorDatabase = self.client[db_name]
            
            # Initialize subsystems
            self.short_term = ShortTermMemory()
            self.long_term = LongTermMemory(self.db)
            self.campaign = CampaignMemory(self.db)
            self.agent = AgentMemory(self.db)
            
            logger.info("MemoryManager initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize MemoryManager: {e}")
            raise
