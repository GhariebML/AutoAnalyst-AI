"""Audit log ORM model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class AuditLog(Base):
    """Represents a security and operational audit log record."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100))  # e.g., run_campaign, publish_campaign, user_login
    entity_type: Mapped[str] = mapped_column(String(100))  # e.g., campaign, user, publication
    entity_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
