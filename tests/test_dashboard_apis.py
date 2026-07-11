import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from adpilot.api.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_optimizer_evaluate_endpoint():
    payload = {
        "metrics": {"ctr": 2.5, "cpa": 4.5, "roas": 2.0},
        "targets": {"ctr_target": 3.0, "cpa_target": 3.0, "roas_target": 3.5}
    }
    response = client.post("/api/optimizer/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    recs = data["recommendations"]
    assert len(recs) == 2
    action_types = {r["action_type"] for r in recs}
    assert "regenerate_content" in action_types
    assert "reduce_budget" in action_types


@pytest.mark.asyncio
async def test_dashboard_campaign_endpoints(monkeypatch):
    mock_task = {
        "task_id": "test-campaign-123",
        "status": "completed",
        "progress": 100,
        "message": "Campaign package ready",
        "brief_json": json.dumps({"businessName": "Test Corp"}),
        "content_json": json.dumps({
            "ads": [{"headline": "Test Ad", "body": "Ad body", "call_to_action": "Click", "funnel_stage": "awareness", "format": "text", "hashtags": []}],
            "emailSequences": [],
            "socialPosts": [],
            "pipeline": {
                "analytics": {
                    "health_score": {"overall": 88.0, "stage_scores": {"awareness": 88.0}},
                    "predicted_metrics": [],
                    "executive_summary": "Demo summary",
                    "improvement_suggestions": [],
                    "ab_test_recommendations": []
                },
                "agent_run_records": [{"agent_name": "strategy_agent", "status": "success", "started_at": "123", "finished_at": "456"}]
            }
        }),
        "error_message": None,
        "created_at": None,
        "updated_at": None
    }
    
    class MockResult:
        def __init__(self, task):
            self.task = task
        def scalars(self):
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [self.task] if self.task else []
            return mock_scalars
        def scalar_one_or_none(self):
            return self.task

    class MockSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def execute(self, statement):
            mock_orm_task = MagicMock()
            mock_orm_task.task_id = mock_task["task_id"]
            mock_orm_task.status = mock_task["status"]
            mock_orm_task.progress = mock_task["progress"]
            mock_orm_task.message = mock_task["message"]
            mock_orm_task.brief_json = mock_task["brief_json"]
            mock_orm_task.content_json = mock_task["content_json"]
            mock_orm_task.error_message = mock_task["error_message"]
            mock_orm_task.created_at = None
            mock_orm_task.updated_at = None
            return MockResult(mock_orm_task)
        async def delete(self, instance):
            pass
        async def commit(self):
            pass

    monkeypatch.setattr("adpilot.core.database.async_session_factory", MockSession)

    # Test GET /api/campaigns
    response = client.get("/api/campaigns")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["campaignId"] == "test-campaign-123"

    # Test GET /api/campaigns/{campaign_id}
    response = client.get("/api/campaigns/test-campaign-123")
    assert response.status_code == 200
    assert response.json()["campaignId"] == "test-campaign-123"

    # Test GET /api/campaigns/{campaign_id}/assets
    response = client.get("/api/campaigns/test-campaign-123/assets")
    assert response.status_code == 200
    assert response.json()["ads"][0]["headline"] == "Test Ad"

    # Test GET /api/campaigns/{campaign_id}/status
    response = client.get("/api/campaigns/test-campaign-123/status")
    assert response.status_code == 200
    assert len(response.json()["agentRunRecords"]) == 1

    # Test GET /api/campaigns/{campaign_id}/analytics
    response = client.get("/api/campaigns/test-campaign-123/analytics")
    assert response.status_code == 200
    assert response.json()["overallHealthScore"] == 88.0

    # Test GET /api/campaigns/{campaign_id}/reports
    response = client.get("/api/campaigns/test-campaign-123/reports")
    assert response.status_code == 200
    assert response.json()["executiveSummary"] == "Demo summary"

    # Test DELETE /api/campaigns/{campaign_id}
    response = client.delete("/api/campaigns/test-campaign-123")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_knowledge_upload_endpoint(monkeypatch):
    mock_process = AsyncMock()
    monkeypatch.setattr("adpilot.services.rag_service.RAGService.process_file", mock_process)

    file_content = b"Mock document content"
    files = {"file": ("test_doc.txt", file_content, "text/plain")}
    data = {"campaign_id": "test-campaign-rag", "doc_type": "brand_guidelines"}

    response = client.post("/api/knowledge/upload", files=files, data=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_process.assert_called_once()
