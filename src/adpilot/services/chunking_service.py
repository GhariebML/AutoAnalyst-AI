"""Document chunking service for RAG."""

import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class ChunkingService:
    """Service to chunk documents for vector store ingestion."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks."""
        logger.info(f"Chunking {len(documents)} documents (size={self.chunk_size}, overlap={self.chunk_overlap})")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Produced {len(chunks)} chunks.")
        return chunks
