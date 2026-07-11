"""Vector store abstraction for RAG pipeline."""

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore as LangchainVectorStore


class VectorStore(ABC):
    """Abstract interface for all vector stores (Qdrant, Milvus, etc.)."""
    
    @abstractmethod
    def get_store(self, collection_name: str) -> LangchainVectorStore:
        """Returns the underlying LangChain VectorStore for a given collection."""
        pass
    
    @abstractmethod
    async def add_documents(self, collection_name: str, documents: List[Document]) -> None:
        """Adds documents to the specified collection."""
        pass
        
    @abstractmethod
    async def similarity_search(
        self, 
        collection_name: str, 
        query: str, 
        k: int = 4, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Searches the specified collection for similar documents."""
        pass
