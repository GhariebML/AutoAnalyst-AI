"""Unit tests for the hardened data loading module."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from autoanalyst.data_loading.loader import (
    estimate_memory_usage,
    load_csv,
    load_dataset,
    load_excel,
    load_json,
    load_parquet,
    load_sqlite,
    preview_dataset,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "score": [85.5, 92.0, 78.5, 95.0, 88.0],
        }
    )


class TestDataLoadingFormats:
    def test_load_csv_and_memory_estimation(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        csv_file = tmp_path / "test.csv"
        sample_df.to_csv(csv_file, index=False)

        loaded = load_csv(csv_file)
        assert loaded.shape == (5, 3)
        assert list(loaded.columns) == ["id", "name", "score"]

        mem_bytes = estimate_memory_usage(loaded)
        assert mem_bytes > 0

    def test_load_parquet(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        pq_file = tmp_path / "test.parquet"
        sample_df.to_parquet(pq_file, index=False)

        loaded = load_parquet(pq_file)
        assert loaded.shape == (5, 3)
        assert loaded["name"].tolist() == ["Alice", "Bob", "Charlie", "David", "Eve"]

    def test_load_json(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        sample_df.to_json(json_file, orient="records")

        loaded = load_json(json_file)
        assert loaded.shape == (5, 3)
        assert loaded["id"].tolist() == [1, 2, 3, 4, 5]

    def test_load_sqlite(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        db_file = tmp_path / "test.db"
        with sqlite3.connect(str(db_file)) as conn:
            sample_df.to_sql("students", conn, index=False)

        loaded = load_sqlite(db_file)
        assert loaded.shape == (5, 3)

        # Query custom SQL
        custom = load_sqlite(db_file, query="SELECT name, score FROM students WHERE score > 85")
        assert len(custom) == 4

    def test_load_excel(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        xlsx_file = tmp_path / "test.xlsx"
        sample_df.to_excel(xlsx_file, index=False)

        loaded = load_excel(xlsx_file)
        assert loaded.shape == (5, 3)

    def test_unified_load_dataset(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        csv_file = tmp_path / "unified.csv"
        sample_df.to_csv(csv_file, index=False)

        loaded = load_dataset(csv_file)
        assert loaded.shape == (5, 3)

        pq_file = tmp_path / "unified.parquet"
        sample_df.to_parquet(pq_file, index=False)
        loaded_pq = load_dataset(pq_file)
        assert loaded_pq.shape == (5, 3)

    def test_preview_dataset(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        csv_file = tmp_path / "preview.csv"
        sample_df.to_csv(csv_file, index=False)

        preview = preview_dataset(csv_file, n_rows=2)
        assert len(preview) == 2


class TestLoadingGuardrails:
    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_dataset("non_existent_file_path.csv")

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="empty"):
            load_dataset(empty_file)

    def test_size_guardrail_exceeded(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        csv_file = tmp_path / "oversized.csv"
        sample_df.to_csv(csv_file, index=False)

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            load_dataset(csv_file, max_file_size_bytes=10)  # 10 byte limit
