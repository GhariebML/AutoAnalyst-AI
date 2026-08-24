"""Pydantic schemas for dataset operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetResponse(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    file_format: str
    rows: int | None = None
    columns: int | None = None
    health_score: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetPreviewResponse(BaseModel):
    id: str
    filename: str
    rows: int
    columns: int
    column_names: list[str]
    health_score: float
    data_preview: list[dict[str, Any]]
    column_profiles: dict[str, Any] = Field(default_factory=dict)
