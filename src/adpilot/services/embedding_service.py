"""Embedding service provider abstraction."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from ..core.config import get_config

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Base abstraction for embedding providers."""
    
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        """Return a LangChain Embeddings instance."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embeddings provider using text-embedding-3-large."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_embeddings(self) -> Embeddings:
        return OpenAIEmbeddings(
            api_key=self.api_key,
            model="text-embedding-3-large",
        )


class FastEmbedProvider(EmbeddingProvider):
    """Local offline embeddings provider using fastembed."""
    
    def get_embeddings(self) -> Embeddings:
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
        return FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")


def get_embedding_model() -> Embeddings:
    """
    Selection priority:
    1. If OPENAI_API_KEY exists -> OpenAIEmbeddingProvider
    2. Else -> FastEmbedProvider
    The system must never fail because embeddings are unavailable.
    """
    settings = get_config()
    
    # Check if a valid OpenAI key exists (not mock)
    if settings.openai_api_key and settings.openai_api_key.strip() and settings.openai_api_key != "mock":
        try:
            logger.info("Initializing OpenAI embeddings (text-embedding-3-large)")
            return OpenAIEmbeddingProvider(settings.openai_api_key).get_embeddings()
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI embeddings: {e}. Falling back to FastEmbed.")
            
    try:
        logger.info("Initializing FastEmbed local embeddings")
        return FastEmbedProvider().get_embeddings()
    except Exception as e:
        logger.error(f"Failed to initialize FastEmbed: {e}. Using DeterministicFakeEmbeddings as fallback.")
        
        class DeterministicFakeEmbeddings(Embeddings):
            def __init__(self, size: int = 384):
                self.size = size
                
            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                vectors = []
                for text in texts:
                    vec = [0.0] * self.size
                    words = text.lower().split()
                    for w in words:
                        # Strip punctuation
                        clean_w = "".join(c for c in w if c.isalnum())
                        if clean_w:
                            idx = sum(ord(c) for c in clean_w) % self.size
                            vec[idx] += 1.0
                    norm = sum(v*v for v in vec) ** 0.5
                    if norm > 0:
                        vec = [v / norm for v in vec]
                    vectors.append(vec)
                return vectors
                
            def embed_query(self, text: str) -> list[float]:
                return self.embed_documents([text])[0]
                
        return DeterministicFakeEmbeddings(size=384)
