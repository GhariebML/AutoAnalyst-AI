import pytest
import os
import shutil
from langchain_core.documents import Document
from adpilot.services.qdrant_store import QdrantLocalStore

@pytest.mark.asyncio
async def test_qdrant_local_store():
    test_dir = "./data/test_qdrant_store"
    if os.path.exists(test_dir):
        try:
            shutil.rmtree(test_dir)
        except Exception:
            pass

    store = QdrantLocalStore(path=test_dir)
    docs = [
        Document(page_content="Apple is a fruit.", metadata={"type": "fruit"}),
        Document(page_content="Car is a vehicle.", metadata={"type": "vehicle"})
    ]

    try:
        await store.add_documents("test_collection", docs)
        
        results = await store.similarity_search("test_collection", "fruit", k=1)
        assert len(results) == 1
        assert "Apple" in results[0].page_content
        
        # Test filtering
        results_filtered = await store.similarity_search("test_collection", "fruit", k=1, filter={"type": "vehicle"})
        assert len(results_filtered) == 1
        assert "Car" in results_filtered[0].page_content
    finally:
        try:
            shutil.rmtree(test_dir)
        except Exception:
            pass
