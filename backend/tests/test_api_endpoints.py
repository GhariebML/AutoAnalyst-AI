"""Integration and endpoint tests for FastAPI backend."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


class TestBackendAPI:
    def test_health_check(self) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_dataset_upload_and_preview(self, tmp_path: Path) -> None:
        df = pd.DataFrame(
            {
                "age": [25, 35, 45, 55],
                "salary": [50000.0, 75000.0, 100000.0, 125000.0],
                "target": [0, 1, 0, 1],
            }
        )
        csv_file = tmp_path / "test_api_data.csv"
        df.to_csv(csv_file, index=False)

        with open(csv_file, "rb") as f:
            upload_resp = client.post(
                "/api/v1/datasets",
                files={"file": ("test_api_data.csv", f, "text/csv")},
            )

        assert upload_resp.status_code == 201
        ds_data = upload_resp.json()
        assert ds_data["filename"] == "test_api_data.csv"
        assert ds_data["rows"] == 4
        assert ds_data["columns"] == 3
        dataset_id = ds_data["id"]

        # Preview
        preview_resp = client.get(f"/api/v1/datasets/{dataset_id}/preview")
        assert preview_resp.status_code == 200
        p_data = preview_resp.json()
        assert len(p_data["data_preview"]) == 4

        # List
        list_resp = client.get("/api/v1/datasets")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

    def test_analysis_creation_and_chat(self, tmp_path: Path) -> None:
        df = pd.DataFrame(
            {
                "feature_a": [10, 20, 30, 40, 50, 60],
                "feature_b": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
                "target": [0, 1, 0, 1, 0, 1],
            }
        )
        csv_file = tmp_path / "analysis_data.csv"
        df.to_csv(csv_file, index=False)

        with open(csv_file, "rb") as f:
            upload_resp = client.post(
                "/api/v1/datasets",
                files={"file": ("analysis_data.csv", f, "text/csv")},
            )
        dataset_id = upload_resp.json()["id"]

        # Start analysis
        create_resp = client.post(
            "/api/v1/analyses",
            json={
                "dataset_id": dataset_id,
                "target_column": "target",
                "model_task": "classification",
            },
        )
        assert create_resp.status_code == 201
        anl_data = create_resp.json()
        analysis_id = anl_data["id"]

        # Fetch status
        get_resp = client.get(f"/api/v1/analyses/{analysis_id}")
        assert get_resp.status_code == 200

        # Chat query
        chat_resp = client.post(
            "/api/v1/chat",
            json={
                "analysis_id": analysis_id,
                "query": "What is the data health score?",
            },
        )
        assert chat_resp.status_code == 200
        assert "response" in chat_resp.json()
