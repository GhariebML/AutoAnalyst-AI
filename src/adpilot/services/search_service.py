"""Search service placeholder – e.g., SERPAPI or custom web search.

Only the interface is defined for now.
"""

from __future__ import annotations

from typing import List


class SearchService:
    """Simple async web‑search client abstraction."""

    async def search(self, query: str, top_n: int = 5) -> List[dict]:  # pragma: no cover
        raise NotImplementedError("Search service not implemented in Phase 1.")
