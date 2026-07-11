import pytest
import logging
from httpx import AsyncClient, ASGITransport
from adpilot.api.main import app
from adpilot.utils.logging_utils import JSONFormatter
from adpilot.core.database import async_session_factory
from adpilot.models.user import User
from adpilot.models.campaign_task import CampaignTask
import json


@pytest.mark.anyio
async def test_saas_role_based_access_control():
    """Verify that endpoints with require_role enforce proper access permissions."""
    # 1. Create a marketer user and a viewer user directly in the database
    async with async_session_factory() as session:
        marketer = User(id="marketer-token", email="marketer@acme.com", hashed_password="pw", role="marketer")
        viewer = User(id="viewer-token", email="viewer@acme.com", hashed_password="pw", role="viewer")
        campaign = CampaignTask(task_id="camp-readiness", status="completed", progress=100, content_json='{"ads": []}')
        
        session.add(marketer)
        session.add(viewer)
        session.add(campaign)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Test 1: Publish with Marketer Token (Success)
        headers = {"Authorization": "Bearer marketer-token"}
        res = await ac.post("/api/campaigns/camp-readiness/publish", json={"channel": "meta"}, headers=headers)
        assert res.status_code == 200
        assert res.json()["status"] == "published"

        # Test 2: Publish with Viewer Token (403 Forbidden)
        headers = {"Authorization": "Bearer viewer-token"}
        res = await ac.post("/api/campaigns/camp-readiness/publish", json={"channel": "meta"}, headers=headers)
        assert res.status_code == 403
        assert "requires one of the following roles" in res.json()["detail"]

        # Test 3: Publish with Missing Token (401 Unauthorized)
        res = await ac.post("/api/campaigns/camp-readiness/publish", json={"channel": "meta"})
        assert res.status_code == 401


@pytest.mark.anyio
async def test_api_health_check():
    """Verify health endpoint database connection ping check."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


def test_json_logging_formatter():
    """Verify JSONFormatter outputs log statements as single-line JSON strings."""
    formatter = JSONFormatter()
    log_record = logging.LogRecord(
        name="adpilot.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Structured logging event test",
        args=(),
        exc_info=None,
    )
    
    json_str = formatter.format(log_record)
    parsed = json.loads(json_str)
    
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "adpilot.test"
    assert parsed["message"] == "Structured logging event test"
    assert parsed["module"] == "test"
    assert parsed["line"] == 42
    assert "timestamp" in parsed
