import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from adpilot.memory.manager import MemoryManager
from adpilot.schemas.agent_schemas import CampaignInput, CampaignContext

@pytest.fixture
def mock_db():
    # Mock motor client and db
    mock_db = MagicMock()
    
    mock_collection = AsyncMock()
    # Mock async methods on collection
    mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
    mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    
    mock_collection.find = MagicMock(return_value=mock_cursor)
    mock_collection.find_one = AsyncMock(return_value=None)
    
    # When dictionary access is used (e.g. self.db["agent_runs"]), return the mocked collection
    mock_db.__getitem__.return_value = mock_collection
    
    return mock_db

@pytest.fixture
def memory_manager(mock_db):
    with patch("adpilot.memory.manager.AsyncIOMotorClient"):
        manager = MemoryManager(mongodb_url="mongodb://localhost:27017", db_name="adpilot_test")
        # Overwrite the db with our mock so all collections get the mock
        manager.db = mock_db
        manager.agent.collection = mock_db["agent_runs"]
        manager.campaign.collection = mock_db["campaign_contexts"]
        manager.long_term.collection = mock_db["memories"]
        return manager

@pytest.mark.asyncio
async def test_short_term_memory(memory_manager):
    mem = memory_manager.short_term
    mem.set("campaign_1", "key1", "value1")
    assert mem.get("campaign_1", "key1") == "value1"
    
    mem.delete("campaign_1", "key1")
    assert mem.get("campaign_1", "key1") is None
    
    mem.set("campaign_1", "key2", "value2")
    mem.clear("campaign_1")
    assert mem.get("campaign_1", "key2") is None

@pytest.mark.asyncio
async def test_agent_memory(memory_manager):
    mem = memory_manager.agent
    run_id = await mem.start_run("camp_1", "StrategyAgent", {"input": "test"})
    assert run_id is not None
    assert isinstance(run_id, str)
    
    await mem.end_run(run_id, "success", {"output": "test_out"})
    
    runs = await mem.get_runs("camp_1")
    assert isinstance(runs, list)

