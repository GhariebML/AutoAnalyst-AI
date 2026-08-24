"""Unit tests for the insight generator module."""

from __future__ import annotations

import pandas as pd

from autoanalyst.insights.insight_generator import generate_dataset_insights


class TestInsightGenerator:
    def test_empty_dataframe(self) -> None:
        insights = generate_dataset_insights(pd.DataFrame())
        assert any("empty" in i.lower() for i in insights)

    def test_dataset_insights(self) -> None:
        df = pd.DataFrame(
            {
                "a": [1, 2, 3, 4, 5],
                "b": [10.0, 20.0, 30.0, 40.0, 50.0],
                "c": ["x", "y", "x", "y", "x"],
            }
        )
        insights = generate_dataset_insights(
            df,
            profile={"rows": 5, "columns": 3, "health_score": 100.0},
            model_results={"task": "classification", "model_name": "RandomForestClassifier"},
            evaluation_results={"accuracy": 0.95, "f1_macro": 0.94},
        )
        assert len(insights) >= 3
        assert any("Dataset Dimension" in i for i in insights)
        assert any("Model Benchmark" in i for i in insights)
