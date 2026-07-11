"""Document loading service for RAG."""

import logging
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader

logger = logging.getLogger(__name__)

class DocumentLoaderService:
    """Service to load various types of documents."""
    
    def load_pdf(self, file_path: str) -> List[Document]:
        logger.info(f"Loading PDF document from {file_path}")
        loader = PyPDFLoader(file_path)
        return loader.load()

    def load_text(self, file_path: str) -> List[Document]:
        logger.info(f"Loading text document from {file_path}")
        loader = TextLoader(file_path)
        return loader.load()

    def load_markdown(self, file_path: str) -> List[Document]:
        logger.info(f"Loading markdown document from {file_path}")
        loader = UnstructuredMarkdownLoader(file_path)
        return loader.load()
    
    def load_document(self, file_path: str) -> List[Document]:
        """Auto-detects document type and loads it."""
        if file_path.lower().endswith(".pdf"):
            return self.load_pdf(file_path)
        elif file_path.lower().endswith(".md"):
            return self.load_markdown(file_path)
        else:
            # Fallback to text loader
            return self.load_text(file_path)
