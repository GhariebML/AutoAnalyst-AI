"""System health and telemetry status endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> dict[str, str]:
    """System health probe endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_enabled": str(settings.AUTOANALYST_LLM_ENABLED),
    }
