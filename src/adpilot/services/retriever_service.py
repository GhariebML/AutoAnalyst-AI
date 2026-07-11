"""Retriever service for RAG."""

import logging
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class RetrieverService:
    """Service to create and manage LangChain retrievers."""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def get_retriever(self, collection_name: str, k: int = 4, filter: Optional[Dict[str, Any]] = None) -> BaseRetriever:
        """Get a LangChain retriever for the specified collection."""
        logger.info(f"Creating retriever for collection {collection_name}")
        store = self.vector_store.get_store(collection_name)
        search_kwargs = {"k": k}
        if filter:
            search_kwargs["filter"] = filter
        return store.as_retriever(search_kwargs=search_kwargs)
