"""Campaign publish ORM model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class CampaignPublish(Base):
    """Represents a scheduled or published campaign channel asset."""

    __tablename__ = "campaign_publishes"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(100), index=True)
    channel: Mapped[str] = mapped_column(String(50))  # facebook, google, linkedin, instagram, buffer
    platform_post_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, scheduled, published, failed
    
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<CampaignPublish(id={self.id}, campaign_id={self.campaign_id}, status={self.status})>"
