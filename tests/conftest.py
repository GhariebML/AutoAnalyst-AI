import os
os.environ["QDRANT_PATH"] = "./storage/test_qdrant_db"

import asyncio
import pytest
from adpilot.core.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Session-scoped fixture to cleanly drop and recreate all SQL tables."""
    async def _setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            
    asyncio.run(_setup())
    yield
