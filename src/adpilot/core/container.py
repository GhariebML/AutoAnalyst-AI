"""Dependency Injection container."""

from __future__ import annotations

import logging
from typing import Optional

from .config import get_config
from ..services.campaign_repo import CampaignRepository
from ..services.memory_service import MemoryService, InMemoryStorageEngine, MongoStorageEngine

logger = logging.getLogger(__name__)


class Container:
    """Simple dependency registry managing singleton instances."""

    def __init__(self) -> None:
        self.config = get_config()
        self._repo: Optional[CampaignRepository] = None
        self._memory_service: Optional[MemoryService] = None

    @property
    def campaign_repo(self) -> CampaignRepository:
        if self._repo is None:
            self._repo = CampaignRepository()
        return self._repo

    @property
    def memory_manager(self) -> 'MemoryManager':
        from ..memory.manager import MemoryManager
        if getattr(self, "_memory_manager", None) is None:
            self._memory_manager = MemoryManager()
        return self._memory_manager

    @property
    def memory_service(self) -> MemoryService:
        if self._memory_service is None:
            backend = self.config.memory_backend.strip().lower()
            if backend == "mongodb":
                try:
                    # Use the new shared memory manager instead of just the isolated storage engine
                    manager = self.memory_manager
                    self._memory_service = MemoryService(manager=manager)
                    logger.info("Configured MemoryService with Phase 5 MemoryManager.")
                except ImportError:
                    logger.warning("motor package not installed, falling back to InMemoryStorageEngine.")
                    engine = InMemoryStorageEngine()
                    self._memory_service = MemoryService(engine=engine)
            else:
                engine = InMemoryStorageEngine()
                logger.info("Configured MemoryService with InMemoryStorageEngine.")
                self._memory_service = MemoryService(engine=engine)
        return self._memory_service


    @property
    def vector_store(self) -> 'VectorStore':
        from ..services.qdrant_store import QdrantLocalStore, QdrantCloudStore
        if getattr(self, "_vector_store", None) is None:
            if self.config.qdrant_mode.lower() == "cloud":
                self._vector_store = QdrantCloudStore(url=self.config.qdrant_url, api_key=self.config.qdrant_api_key)
            else:
                self._vector_store = QdrantLocalStore(path=self.config.qdrant_path)
        return self._vector_store

    @property
    def document_loader(self) -> 'DocumentLoaderService':
        from ..services.document_loader import DocumentLoaderService
        if getattr(self, "_document_loader", None) is None:
            self._document_loader = DocumentLoaderService()
        return self._document_loader

    @property
    def chunking_service(self) -> 'ChunkingService':
        from ..services.chunking_service import ChunkingService
        if getattr(self, "_chunking_service", None) is None:
            self._chunking_service = ChunkingService()
        return self._chunking_service

    @property
    def knowledge_service(self) -> 'KnowledgeService':
        from ..services.knowledge_service import KnowledgeService
        if getattr(self, "_knowledge_service", None) is None:
            self._knowledge_service = KnowledgeService(
                vector_store=self.vector_store,
                document_loader=self.document_loader,
                chunking_service=self.chunking_service
            )
        return self._knowledge_service

    @property
    def rag_service(self) -> 'RAGService':
        from ..services.rag_service import RAGService
        if getattr(self, "_rag_service", None) is None:
            self._rag_service = RAGService(knowledge_service=self.knowledge_service)
        return self._rag_service

_global_container = Container()

def get_container() -> Container:
    """FastAPI dependency for retrieving the global container."""
    return _global_container
