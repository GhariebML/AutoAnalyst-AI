"""Token cost tracking service."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from ..core.config import get_config

logger = logging.getLogger(__name__)

# Rough estimates for pricing per 1K tokens (input, output)
MODEL_PRICING = {
    "gpt-4o": (0.005, 0.015),
    "claude-3-5-sonnet-latest": (0.003, 0.015),
    "openrouter/free": (0.0, 0.0),
}


class CostTrackingCallbackHandler(AsyncCallbackHandler):
    """Async callback handler that tracks and stores LLM token costs in MongoDB."""

    def __init__(self, campaign_id: str, agent_name: str, provider_name: str, model_name: str) -> None:
        self.campaign_id = campaign_id
        self.agent_name = agent_name
        self.provider_name = provider_name
        self.model_name = model_name
        
        self.start_time: Optional[datetime] = None
        self.config = get_config()

        # Connect to MongoDB
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self.client = AsyncIOMotorClient(self.config.mongodb_url)
            self.db = self.client["adpilot"]
            self.collection = self.db["token_costs"]
        except ImportError:
            logger.warning("motor package not installed. Cost tracking disabled.")
            self.collection = None

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], *, run_id: UUID, parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.start_time = datetime.now(timezone.utc)

    async def on_llm_end(
        self, response: LLMResult, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> None:
        """Run when LLM finishes running."""
        if not self.collection:
            return

        end_time = datetime.now(timezone.utc)
        latency_ms = int((end_time - self.start_time).total_seconds() * 1000) if self.start_time else 0

        input_tokens = 0
        output_tokens = 0

        # Extract token usage
        if response.llm_output and "token_usage" in response.llm_output:
            token_usage = response.llm_output["token_usage"]
            input_tokens = token_usage.get("prompt_tokens", 0)
            output_tokens = token_usage.get("completion_tokens", 0)

        # Calculate estimated cost
        in_rate, out_rate = MODEL_PRICING.get(self.model_name, (0.0, 0.0))
        estimated_cost = (input_tokens / 1000.0 * in_rate) + (output_tokens / 1000.0 * out_rate)

        document = {
            "campaign_id": self.campaign_id,
            "agent": self.agent_name,
            "provider": self.provider_name,
            "model": self.model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "estimated_cost": estimated_cost,
            "timestamp": end_time.isoformat()
        }

        try:
            await self.collection.insert_one(document)
        except Exception as e:
            logger.error(f"Failed to save cost tracking data to MongoDB: {e}")
