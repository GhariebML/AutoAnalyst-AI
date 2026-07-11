"""AgentMemory for tracking individual agent runs and outputs."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..schemas.memory_schemas import AgentRunRecord

logger = logging.getLogger(__name__)

class AgentMemory:
    """
    Handles logging of agent executions, inputs, and raw outputs to the agent_runs collection.
    """

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = self.db["agent_runs"]

    async def start_run(self, campaign_id: str, agent_name: str, inputs: Dict[str, Any]) -> str:
        """Log the start of an agent run and return the run ID."""
        record = AgentRunRecord(
            campaign_id=campaign_id,
            agent_name=agent_name,
            status="running",
            inputs=inputs
        )
        try:
            await self.collection.insert_one(record.model_dump(mode="json"))
            return record.id
        except Exception as e:
            logger.error(f"Failed to start agent run for {agent_name}: {e}")
            return record.id

    async def end_run(self, run_id: str, status: str, outputs: Optional[Dict[str, Any]] = None, error_message: Optional[str] = None) -> None:
        """Update an agent run with its final status and outputs."""
        try:
            update_data = {
                "status": status,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            if outputs is not None:
                update_data["outputs"] = outputs
            if error_message is not None:
                update_data["error_message"] = error_message
                
            await self.collection.update_one(
                {"id": run_id},
                {"$set": update_data}
            )
        except Exception as e:
            logger.error(f"Failed to end agent run {run_id}: {e}")

    async def get_runs(self, campaign_id: str, agent_name: Optional[str] = None) -> List[AgentRunRecord]:
        """Fetch past runs for a campaign (optionally filtered by agent)."""
        query = {"campaign_id": campaign_id}
        if agent_name:
            query["agent_name"] = agent_name
            
        try:
            cursor = self.collection.find(query).sort("created_at", 1)
            results = await cursor.to_list(length=100)
            return [AgentRunRecord.model_validate(r) for r in results]
        except Exception as e:
            logger.error(f"Failed to fetch agent runs for {campaign_id}: {e}")
            return []
