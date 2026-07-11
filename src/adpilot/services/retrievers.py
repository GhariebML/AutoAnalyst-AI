"""Specific retrievers for the RAG platform."""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class BrandGuidelinesRetriever:
    """Retriever for brand guidelines and tone of voice."""
    
    def __init__(self, vector_store: VectorStore, k: int = 3):
        self.vector_store = vector_store
        self.k = k
        self.collection_name = "brand_guidelines"

    async def retrieve(self, query: str, brand_name: Optional[str] = None) -> List[Document]:
        """Retrieve brand guidelines, optionally filtering by brand name."""
        logger.info(f"Retrieving brand guidelines for query: {query}")
        filter_dict = {}
        if brand_name:
            filter_dict["brand_name"] = brand_name
            
        return await self.vector_store.similarity_search(
            collection_name=self.collection_name,
            query=query,
            k=self.k,
            filter=filter_dict or None
        )

class PastCampaignRetriever:
    """Retriever for past successful campaigns."""
    
    def __init__(self, vector_store: VectorStore, k: int = 5):
        self.vector_store = vector_store
        self.k = k
        self.collection_name = "past_campaigns"

    async def retrieve(self, query: str, industry: Optional[str] = None) -> List[Document]:
        """Retrieve past campaigns, optionally filtering by industry."""
        logger.info(f"Retrieving past campaigns for query: {query}")
        filter_dict = {}
        if industry:
            filter_dict["industry"] = industry
            
        return await self.vector_store.similarity_search(
            collection_name=self.collection_name,
            query=query,
            k=self.k,
            filter=filter_dict or None
        )
