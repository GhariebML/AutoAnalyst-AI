"""Tests for real-time model serving and Prometheus APM telemetry endpoints."""

import uuid

import pandas as pd
import pytest
from backend.app.main import app
from backend.app.models.database import AnalysisRunModel, DatasetModel, SessionLocal
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def setup_test_dataset_and_run(tmp_path):
    """Seed test SQLite database with a unique dataset file and an analysis run."""
    db = SessionLocal()
    ds_id = f"ds_test_{uuid.uuid4().hex[:8]}"
    anl_id = f"anl_test_{uuid.uuid4().hex[:8]}"

    df = pd.DataFrame(
        {
            "feature_x": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
            "feature_y": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
            "category_z": ["A", "B", "A", "B", "A", "B"],
            "target": [100.0, 200.0, 300.0, 400.0, 500.0, 600.0],
        }
    )
    csv_file = tmp_path / f"{ds_id}.csv"
    df.to_csv(csv_file, index=False)

    ds = DatasetModel(
        id=ds_id,
        filename="test_data.csv",
        file_path=str(csv_file),
        file_size_bytes=1024,
        file_format="csv",
        rows=6,
        columns=4,
        health_score=100.0,
    )
    db.add(ds)

    run = AnalysisRunModel(
        id=anl_id,
        dataset_id=ds_id,
        target_column="target",
        model_task="regression",
        status="completed",
        champion_model_name="RandomForestRegressor",
        champion_score=0.98,
        profile_json='{"columns": {"feature_x": {"inferred_type": "float", "sample_values": []}, "feature_y": {"inferred_type": "float", "sample_values": []}, "category_z": {"inferred_type": "category", "sample_values": ["A", "B"]}}}',
        eda_json='{"summary_statistics": {"feature_x": {"min": 10.0, "max": 60.0, "mean": 35.0}, "feature_y": {"min": 1.5, "max": 6.5, "mean": 4.0}}}',
    )
    db.add(run)
    db.commit()
    db.close()

    yield anl_id


def test_prometheus_metrics_endpoint():
    """Verify standard Prometheus plaintext endpoint returns expected metrics."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "autoanalyst_http_requests_total" in response.text
    assert "autoanalyst_active_runs" in response.text


def test_model_schema_endpoint(setup_test_dataset_and_run):
    """Verify model schema endpoint returns dynamic feature specifications."""
    analysis_id = setup_test_dataset_and_run
    response = client.get(f"/api/v1/models/{analysis_id}/schema")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == analysis_id
    assert data["target_column"] == "target"
    assert len(data["features"]) >= 3


def test_model_prediction_endpoint(setup_test_dataset_and_run):
    """Verify real-time model inference endpoint outputs predictions and feature influences."""
    analysis_id = setup_test_dataset_and_run
    payload = {
        "inputs": {
            "feature_x": 35.0,
            "feature_y": 4.0,
            "category_z": "A",
        }
    }
    response = client.post(f"/api/v1/models/{analysis_id}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "prediction_label" in data
    assert data["confidence"] > 0
    assert len(data["feature_contributions"]) > 0
