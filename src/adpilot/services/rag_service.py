"""RAG (Retrieval-Augmented Generation) service for company knowledge retrieval."""

import logging
from typing import Optional, List
from langchain_core.documents import Document

from .knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)

class RAGService:
    """Handles upload parsing, chunking, embedding, indexing, and retrieval of documents using Qdrant."""

    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    async def process_file(self, file_path: str, campaign_id: str, filename: str) -> None:
        """Parse file content (TXT, MD, PDF), chunk it, embed, and store in Qdrant."""
        
        # We index all uploaded campaign files into the 'campaign_files' collection
        collection_name = "campaign_files"
        
        metadata = {
            "campaign_id": campaign_id,
            "source": filename
        }
        
        try:
            await self.knowledge_service.ingest_document(
                collection_name=collection_name,
                file_path=file_path,
                metadata=metadata
            )
            logger.info(f"Successfully processed file {filename} for campaign {campaign_id}")
        except Exception as e:
            logger.error(f"Failed to process file {filename}: {e}")
            raise e

    async def retrieve_relevant_context(
        self, query: str, campaign_id: Optional[str] = None, k: int = 3
    ) -> str:
        """Query Qdrant and return a formatted string of context."""
        collection_name = "campaign_files"
        
        filter_dict = {}
        if campaign_id:
            filter_dict["campaign_id"] = campaign_id

        try:
            docs = await self.knowledge_service.search(
                collection_name=collection_name,
                query=query,
                k=k,
                filter=filter_dict or None
            )
            
            if not docs:
                return ""

            context_parts = []
            for doc in docs:
                source = doc.metadata.get("source", "Unknown Source")
                context_parts.append(f"--- Context from {source} ---\n{doc.page_content}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}")
            return ""

    async def clear_campaign_data(self, campaign_id: str) -> None:
        """Remove all indexed documents for a specific campaign.
        Note: Currently Qdrant langchain implementation doesn't support async delete easily by metadata.
        This would require using the raw Qdrant client.
        """
        logger.warning("clear_campaign_data not fully implemented for Qdrant yet.")
        # store = self.knowledge_service.vector_store.get_store("campaign_files")
        # Needs direct qdrant_client call
        pass
