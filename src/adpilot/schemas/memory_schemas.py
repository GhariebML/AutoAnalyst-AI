"""Pydantic v2 schemas for the Phase 5 Shared Memory architecture."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    """Represents a specific conversational context or derived insight."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    campaign_id: str
    agent_name: str
    memory_type: str = Field(..., description="e.g., 'insight', 'summary', 'context', 'feedback'")
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRunRecord(BaseModel):
    """Captures individual agent execution metrics, status, and raw outputs."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    campaign_id: str
    agent_name: str
    status: str = Field(default="pending", description="'pending', 'running', 'success', 'failed'")
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class ArtifactRecord(BaseModel):
    """Metadata for files/documents created by the pipeline."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    campaign_id: str
    agent_name: str
    file_name: str
    file_type: str = Field(..., description="e.g., 'pdf', 'image/png', 'csv'")
    storage_path: str = Field(..., description="Local path, S3 URI, or Cloudinary URL")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
