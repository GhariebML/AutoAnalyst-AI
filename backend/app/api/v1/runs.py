"""Runs and real-time Server-Sent Events (SSE) telemetry API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.events import GLOBAL_EVENT_BROKER
from backend.app.models.database import get_db
from backend.app.schemas.analysis import AnalysisApproveRequest, AnalysisResponse
from backend.app.services.orchestrator_service import OrchestratorService

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/{run_id}/events")
async def stream_run_events(run_id: str):
    """Subscribe to real-time Server-Sent Events (SSE) stream for a running analysis."""
    return StreamingResponse(
        GLOBAL_EVENT_BROKER.subscribe(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{run_id}/history")
def get_run_events_history(run_id: str) -> list[dict]:
    """Retrieve historical telemetry events for an analysis run."""
    return GLOBAL_EVENT_BROKER.get_run_history(run_id)


@router.post("/{run_id}/approve", response_model=AnalysisResponse)
def approve_hitl_step(
    run_id: str,
    payload: AnalysisApproveRequest,
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """Submit human approval or modifications to resume a paused analysis step."""
    try:
        record = OrchestratorService.resume_analysis_with_approval(
            analysis_id=run_id,
            step=payload.step,
            approved=payload.approved,
            db=db,
        )
        from backend.app.api.v1.analyses import _format_analysis_response

        return _format_analysis_response(record)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
