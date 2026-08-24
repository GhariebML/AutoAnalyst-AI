"""Analysis initiation and history API endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models.database import AnalysisRunModel, get_db
from backend.app.schemas.analysis import AnalysisCreateRequest, AnalysisResponse
from backend.app.services.orchestrator_service import OrchestratorService

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _format_analysis_response(record: AnalysisRunModel) -> AnalysisResponse:
    profile = json.loads(record.profile_json) if record.profile_json else None
    eval_res = json.loads(record.evaluation_json) if record.evaluation_json else None
    eda_res = json.loads(record.eda_json) if getattr(record, "eda_json", None) else None
    model_res = json.loads(record.model_results_json) if getattr(record, "model_results_json", None) else None
    findings = json.loads(record.findings_json) if getattr(record, "findings_json", None) else []
    insights = json.loads(record.insights_json) if record.insights_json else []

    return AnalysisResponse(
        id=record.id,
        dataset_id=record.dataset_id,
        target_column=record.target_column,
        model_task=record.model_task or "auto",
        status=record.status or "pending",
        champion_model_name=record.champion_model_name,
        champion_score=record.champion_score,
        executive_summary=record.executive_summary,
        insights=insights,
        findings=findings,
        profile=profile,
        eda_results=eda_res,
        model_results=model_res,
        evaluation_results=eval_res,
        evaluation=eval_res,
        duration_ms=record.duration_ms or 0.0,
        report_path=record.report_path,
        created_at=record.created_at,
    )


@router.post("", response_model=AnalysisResponse, status_code=201)
def create_analysis(payload: AnalysisCreateRequest, db: Session = Depends(get_db)) -> AnalysisResponse:
    """Create and start an autonomous multi-agent analysis run."""
    try:
        record = OrchestratorService.start_analysis_async(
            dataset_id=payload.dataset_id,
            target_column=payload.target_column,
            model_task=payload.model_task,
            missing_strategy=payload.missing_strategy,
            require_approval=payload.require_approval,
            db=db,
        )
        return _format_analysis_response(record)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[AnalysisResponse])
def list_analyses(db: Session = Depends(get_db)) -> list[AnalysisResponse]:
    """List all analysis runs."""
    records = db.query(AnalysisRunModel).order_by(AnalysisRunModel.created_at.desc()).all()
    return [_format_analysis_response(r) for r in records]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)) -> AnalysisResponse:
    """Get full status and findings for an analysis run."""
    record = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _format_analysis_response(record)
