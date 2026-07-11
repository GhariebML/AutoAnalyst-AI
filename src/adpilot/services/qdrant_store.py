"""Qdrant vector store implementations."""

import logging
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore as LangchainVectorStore

from .vector_store import VectorStore
from .embedding_service import get_embedding_model

logger = logging.getLogger(__name__)


class BaseQdrantStore(VectorStore):
    """Base Qdrant logic shared by local and cloud stores."""
    
    def __init__(self, client: QdrantClient):
        self.client = client
        self.embeddings = get_embedding_model()
        self._stores: Dict[str, LangchainVectorStore] = {}
        
    def _ensure_collection(self, collection_name: str) -> None:
        """Ensure the collection exists in Qdrant before getting the store."""
        try:
            if not self.client.collection_exists(collection_name):
                logger.info(f"Creating Qdrant collection: {collection_name}")
                # We determine vector size by embedding a dummy text
                dummy_embed = self.embeddings.embed_query("dummy")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=len(dummy_embed), distance=Distance.COSINE),
                )
        except Exception as e:
            logger.warning(f"Error checking/creating collection {collection_name}: {e}")

    def get_store(self, collection_name: str) -> LangchainVectorStore:
        if collection_name not in self._stores:
            self._ensure_collection(collection_name)
            self._stores[collection_name] = QdrantVectorStore(
                client=self.client,
                collection_name=collection_name,
                embedding=self.embeddings,
            )
        return self._stores[collection_name]

    async def add_documents(self, collection_name: str, documents: List[Document]) -> None:
        store = self.get_store(collection_name)
        await store.aadd_documents(documents)

    async def similarity_search(
        self, 
        collection_name: str, 
        query: str, 
        k: int = 4, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        store = self.get_store(collection_name)
        
        qdrant_filter = None
        if filter:
            from qdrant_client.http import models as rest
            conditions = []
            for key, value in filter.items():
                conditions.append(
                    rest.FieldCondition(
                        key=f"metadata.{key}",
                        match=rest.MatchValue(value=value)
                    )
                )
            qdrant_filter = rest.Filter(must=conditions)

        return await store.asimilarity_search(query, k=k, filter=qdrant_filter)


class QdrantLocalStore(BaseQdrantStore):
    """Local Qdrant using disk storage."""
    def __init__(self, path: str):
        logger.info(f"Initializing local Qdrant at {path}")
        client = QdrantClient(path=path)
        super().__init__(client)


class QdrantCloudStore(BaseQdrantStore):
    """Cloud Qdrant."""
    def __init__(self, url: str, api_key: str):
        logger.info(f"Initializing cloud Qdrant at {url}")
        client = QdrantClient(url=url, api_key=api_key)
        super().__init__(client)
