"""Pydantic schemas for AI analyst chat interactions."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    analysis_id: str
    query: str


class ChatResponse(BaseModel):
    analysis_id: str
    query: str
    response: str
    source: str = "deterministic"
    suggested_followups: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
