"""Data loading and schema inspection tools for AutoAnalyst AI."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from autoanalyst.data_loading.loader import (
    estimate_memory_usage,
    load_dataset,
    preview_dataset,
)
from autoanalyst.tools.base import BaseAnalyticalTool, ToolMetadata


# ---------------------------------------------------------------------------
# 1. LoadDatasetTool
# ---------------------------------------------------------------------------
class LoadDatasetInput(BaseModel):
    file_path: str = Field(..., description="Path to CSV, Excel, Parquet, JSON, or SQLite dataset")
    max_file_size_bytes: int = Field(500 * 1024 * 1024, description="Maximum allowed file size in bytes")


class LoadDatasetOutput(BaseModel):
    file_path: str
    rows: int
    columns: int
    column_names: list[str]
    estimated_memory_bytes: int
    data_preview: list[dict[str, Any]]
    df: Any = Field(None, exclude=True)


class LoadDatasetTool(BaseAnalyticalTool[LoadDatasetInput, LoadDatasetOutput]):
    metadata = ToolMetadata(
        name="load_dataset",
        description="Load tabular datasets from CSV, Excel, Parquet, JSON, or SQLite files.",
        category="data_loading",
        tags=["io", "loader", "ingestion"],
    )

    def _run(self, params: LoadDatasetInput) -> LoadDatasetOutput:
        df = load_dataset(params.file_path, max_file_size_bytes=params.max_file_size_bytes)
        mem = estimate_memory_usage(df)
        preview = df.head(10).to_dict(orient="records")
        return LoadDatasetOutput(
            file_path=str(params.file_path),
            rows=int(df.shape[0]),
            columns=int(df.shape[1]),
            column_names=[str(c) for c in df.columns],
            estimated_memory_bytes=mem,
            data_preview=preview,
            df=df,
        )


# ---------------------------------------------------------------------------
# 2. PreviewDatasetTool
# ---------------------------------------------------------------------------
class PreviewDatasetInput(BaseModel):
    file_path: str = Field(..., description="Path to dataset file")
    n_rows: int = Field(10, ge=1, le=100, description="Number of preview rows to inspect")


class PreviewDatasetOutput(BaseModel):
    n_rows: int
    column_names: list[str]
    preview_records: list[dict[str, Any]]


class PreviewDatasetTool(BaseAnalyticalTool[PreviewDatasetInput, PreviewDatasetOutput]):
    metadata = ToolMetadata(
        name="preview_dataset",
        description="Fast preview inspection of initial dataset rows without full memory load.",
        category="data_loading",
        tags=["preview", "inspection"],
    )

    def _run(self, params: PreviewDatasetInput) -> PreviewDatasetOutput:
        preview_df = preview_dataset(params.file_path, n_rows=params.n_rows)
        return PreviewDatasetOutput(
            n_rows=len(preview_df),
            column_names=[str(c) for c in preview_df.columns],
            preview_records=preview_df.to_dict(orient="records"),
        )
