import pytest
from langchain_core.embeddings import Embeddings
from adpilot.services.embedding_service import get_embedding_model, FastEmbedProvider, OpenAIEmbeddingProvider
from adpilot.core.config import get_config

def test_embedding_provider_resolution(monkeypatch):
    # Test fallback to FastEmbed
    monkeypatch.setenv("OPENAI_API_KEY", "")
    config = get_config()
    config.openai_api_key = ""
    
    embeddings = get_embedding_model()
    assert embeddings is not None
    assert isinstance(embeddings, Embeddings)
