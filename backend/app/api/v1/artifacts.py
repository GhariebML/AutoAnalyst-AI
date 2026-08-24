"""Artifacts download and inspection endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from backend.app.models.database import AnalysisRunModel, ArtifactModel, DatasetModel, get_db

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("/{identifier}/download")
def download_artifact(
    identifier: str,
    format: str | None = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    """Download a generated artifact file by artifact ID or analysis run ID with format support."""
    # 1. Check if identifier is a direct ArtifactModel.id
    art = db.query(ArtifactModel).filter(ArtifactModel.id == identifier).first()
    if art and Path(art.file_path).exists():
        media_type = "text/html" if art.file_path.endswith(".html") else "application/octet-stream"
        return FileResponse(path=art.file_path, filename=art.filename, media_type=media_type)

    # 2. Check if identifier is an AnalysisRunModel.id
    run = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == identifier).first()
    if not run:
        # Also check if an artifact exists with analysis_id == identifier
        art = db.query(ArtifactModel).filter(ArtifactModel.analysis_id == identifier).first()
        if art and Path(art.file_path).exists():
            media_type = "text/html" if art.file_path.endswith(".html") else "application/octet-stream"
            return FileResponse(path=art.file_path, filename=art.filename, media_type=media_type)
        raise HTTPException(status_code=404, detail="Artifact or analysis run not found on server")

    # Format requested: html
    if format == "html" or (format is None and run.report_path):
        if run.report_path and Path(run.report_path).exists():
            return FileResponse(
                path=run.report_path,
                filename=f"AutoAnalyst_Report_{run.id[:8]}.html",
                media_type="text/html",
            )
        # Check artifact table for html_report
        art = (
            db.query(ArtifactModel)
            .filter(ArtifactModel.analysis_id == identifier, ArtifactModel.artifact_type == "html_report")
            .first()
        )
        if art and Path(art.file_path).exists():
            return FileResponse(path=art.file_path, filename=art.filename, media_type="text/html")

        # Compile dynamically on the fly if report was not persisted to disk
        from autoanalyst.tools.reporting_tools import CompileReportInput, CompileReportTool

        out_dir = Path("reports")
        out_dir.mkdir(parents=True, exist_ok=True)
        html_target = str(out_dir / f"AutoAnalyst_Report_{run.id[:8]}.html")
        tool = CompileReportTool()
        tool.execute(
            CompileReportInput(
                output_path=html_target,
                title="AutoAnalyst AI Autonomous Report",
                format="html",
                profile=json.loads(run.profile_json) if run.profile_json else {},
                insights=json.loads(run.insights_json) if run.insights_json else [],
                model_results=json.loads(run.model_results_json) if run.model_results_json else None,
                evaluation_results=json.loads(run.evaluation_json) if run.evaluation_json else None,
                executive_summary=run.executive_summary,
            )
        )
        if Path(html_target).exists():
            run.report_path = html_target
            db.commit()
            return FileResponse(
                path=html_target,
                filename=f"AutoAnalyst_Report_{run.id[:8]}.html",
                media_type="text/html",
            )

    # Format requested: json
    if format == "json":
        export_payload = {
            "analysis_id": run.id,
            "dataset_id": run.dataset_id,
            "target_column": run.target_column,
            "status": run.status,
            "champion_model": run.champion_model_name,
            "champion_score": run.champion_score,
            "executive_summary": run.executive_summary,
            "insights": json.loads(run.insights_json) if run.insights_json else [],
            "findings": json.loads(run.findings_json) if run.findings_json else [],
            "profile": json.loads(run.profile_json) if run.profile_json else None,
            "eda_results": json.loads(run.eda_json) if run.eda_json else None,
            "model_results": json.loads(run.model_results_json) if run.model_results_json else None,
            "evaluation_results": json.loads(run.evaluation_json) if run.evaluation_json else None,
            "duration_ms": run.duration_ms,
            "created_at": run.created_at.isoformat() if run.created_at else None,
        }
        return Response(
            content=json.dumps(export_payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=AutoAnalyst_Synthesis_{run.id[:8]}.json"},
        )

    # Format requested: csv (returns underlying dataset)
    if format == "csv":
        dataset = db.query(DatasetModel).filter(DatasetModel.id == run.dataset_id).first()
        if dataset and Path(dataset.file_path).exists():
            return FileResponse(
                path=dataset.file_path,
                filename=dataset.filename or f"cleaned_dataset_{run.id[:8]}.csv",
                media_type="text/csv",
            )

    # Default fallback: return report if exists
    if run.report_path and Path(run.report_path).exists():
        return FileResponse(
            path=run.report_path,
            filename=f"AutoAnalyst_Report_{run.id[:8]}.html",
            media_type="text/html",
        )

    raise HTTPException(status_code=404, detail="Requested artifact format not available for this run")


@router.get("/by-analysis/{analysis_id}")
def list_analysis_artifacts(analysis_id: str, db: Session = Depends(get_db)) -> list[dict]:
    """List all artifacts produced during an analysis run."""
    records = db.query(ArtifactModel).filter(ArtifactModel.analysis_id == analysis_id).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "artifact_type": r.artifact_type,
            "file_size_bytes": r.file_size_bytes,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
