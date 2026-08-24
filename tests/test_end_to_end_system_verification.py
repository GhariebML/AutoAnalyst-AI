import time
from pathlib import Path

import pandas as pd
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_full_system_lifecycle_after_upload(tmp_path: Path) -> None:
    # 1. Prepare sample dataset
    df = pd.DataFrame(
        {
            "age": [22, 38, 26, 35, 54, 42, 31, 29, 60, 48, 25, 33],
            "income": [32000, 78000, 45000, 62000, 110000, 85000, 52000, 49000, 125000, 95000, 39000, 58000],
            "education": [
                "Bachelors",
                "Masters",
                "Bachelors",
                "PhD",
                "Masters",
                "Bachelors",
                "PhD",
                "Bachelors",
                "Masters",
                "PhD",
                "Bachelors",
                "Masters",
            ],
            "credit_score": [650, 720, 680, 710, 800, 740, 690, 670, 820, 760, 660, 705],
            "approved": [0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1],
        }
    )
    csv_file = tmp_path / "credit_customers.csv"
    df.to_csv(csv_file, index=False)

    # 2. Upload file
    with open(csv_file, "rb") as f:
        up_resp = client.post(
            "/api/v1/datasets",
            files={"file": ("credit_customers.csv", f, "text/csv")},
        )
    assert up_resp.status_code == 201
    ds_data = up_resp.json()
    assert ds_data["rows"] == 12
    assert ds_data["columns"] == 5
    assert ds_data["health_score"] >= 80.0
    dataset_id = ds_data["id"]

    # 3. Preview dataset
    prev_resp = client.get(f"/api/v1/datasets/{dataset_id}/preview")
    assert prev_resp.status_code == 200
    prev = prev_resp.json()
    assert len(prev["data_preview"]) >= 1
    assert "column_names" in prev

    # 4. Launch Autonomous Multi-Agent Analysis
    anl_resp = client.post(
        "/api/v1/analyses",
        json={
            "dataset_id": dataset_id,
            "target_column": "approved",
            "model_task": "classification",
            "missing_strategy": "median",
            "require_approval": False,
        },
    )
    assert anl_resp.status_code == 201
    anl_id = anl_resp.json()["id"]

    # 5. Poll for completion
    for _ in range(30):
        time.sleep(0.5)
        status_resp = client.get(f"/api/v1/analyses/{anl_id}")
        status_data = status_resp.json()
        if status_data["status"] in ("completed", "failed"):
            break

    assert status_data["status"] == "completed"
    assert status_data["executive_summary"] is not None
    assert len(status_data["findings"]) > 0
    assert status_data["champion_model_name"] is not None

    # 6. Test AI Copilot Chat
    chat_resp = client.post(
        "/api/v1/chat",
        json={"analysis_id": anl_id, "query": "What is the champion model and what was its performance?"},
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "response" in chat_data
    assert len(chat_data["response"]) > 10

    # 7. Test Artifact Download
    dl_resp = client.get(f"/api/v1/artifacts/{anl_id}/download?format=html")
    assert dl_resp.status_code == 200
    assert len(dl_resp.content) > 100
