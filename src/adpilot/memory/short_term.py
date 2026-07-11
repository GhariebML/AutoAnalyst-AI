"""ShortTermMemory for transient scratchpads and intermediate outputs."""

from typing import Any, Dict, Optional


class ShortTermMemory:
    """
    Manages transient scratchpads and intermediate outputs within a single pipeline execution.
    Data stored here is ephemeral and will be lost if the service restarts.
    """

    def __init__(self) -> None:
        # dict mapping campaign_id -> dict of arbitrary keys/values
        self._memory: Dict[str, Dict[str, Any]] = {}

    def set(self, campaign_id: str, key: str, value: Any) -> None:
        """Store a value in short-term memory for a campaign."""
        if campaign_id not in self._memory:
            self._memory[campaign_id] = {}
        self._memory[campaign_id][key] = value

    def get(self, campaign_id: str, key: str) -> Optional[Any]:
        """Retrieve a value from short-term memory."""
        return self._memory.get(campaign_id, {}).get(key)

    def delete(self, campaign_id: str, key: str) -> None:
        """Delete a specific key from short-term memory."""
        if campaign_id in self._memory and key in self._memory[campaign_id]:
            del self._memory[campaign_id][key]

    def clear(self, campaign_id: str) -> None:
        """Clear all short-term memory for a campaign."""
        if campaign_id in self._memory:
            del self._memory[campaign_id]
