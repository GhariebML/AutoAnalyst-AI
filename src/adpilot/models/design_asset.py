"""Design asset ORM model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class DesignAsset(Base):
    """Represents a generated visual asset for a campaign."""

    __tablename__ = "design_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    campaign_id: Mapped[str] = mapped_column(String(100), index=True)
    task_id: Mapped[str] = mapped_column(String(100), index=True)

    # Content fields
    prompt: Mapped[str] = mapped_column(String(1000))
    negative_prompt: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    width: Mapped[int] = mapped_column(default=1024)
    height: Mapped[int] = mapped_column(default=1024)
    style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, COMPLETED, FAILED
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<DesignAsset(id={self.id}, status={self.status}, campaign_id={self.campaign_id})>"
