"""Knowledge orchestrator service for RAG."""

import logging
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document

from .document_loader import DocumentLoaderService
from .chunking_service import ChunkingService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class KnowledgeService:
    """Service to orchestrate document ingestion and basic search."""
    
    def __init__(
        self, 
        vector_store: VectorStore,
        document_loader: DocumentLoaderService,
        chunking_service: ChunkingService
    ):
        self.vector_store = vector_store
        self.document_loader = document_loader
        self.chunking_service = chunking_service

    async def ingest_document(self, collection_name: str, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Loads, chunks, and adds a document to the vector store."""
        logger.info(f"Ingesting document from {file_path} into collection {collection_name}")
        
        # 1. Load
        documents = self.document_loader.load_document(file_path)
        
        # Enhance metadata if provided
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
                
        # 2. Chunk
        chunks = self.chunking_service.chunk_documents(documents)
        
        # 3. Store
        await self.vector_store.add_documents(collection_name, chunks)
        logger.info(f"Successfully ingested {len(chunks)} chunks into {collection_name}")

    async def add_texts(self, collection_name: str, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Adds raw texts to the knowledge base."""
        documents = []
        for i, text in enumerate(texts):
            meta = metadatas[i] if metadatas else {}
            documents.append(Document(page_content=text, metadata=meta))
            
        chunks = self.chunking_service.chunk_documents(documents)
        await self.vector_store.add_documents(collection_name, chunks)

    async def search(self, collection_name: str, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Perform a similarity search."""
        return await self.vector_store.similarity_search(collection_name, query, k, filter)
