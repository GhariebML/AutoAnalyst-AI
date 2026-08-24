"""Service layer for multi-agent analysis execution and lifecycle coordination."""

from __future__ import annotations

import concurrent.futures
import json
import logging
import math
import uuid
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from autoanalyst.agents.orchestrator import MasterOrchestrator, OrchestratorEvent
from backend.app.core.config import settings
from backend.app.core.events import GLOBAL_EVENT_BROKER
from backend.app.models.database import AnalysisRunModel, ArtifactModel, DatasetModel, SessionLocal

logger = logging.getLogger(__name__)
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def to_json_serializable(val: Any) -> Any:
    """Recursively convert arbitrary objects (Pydantic, dataclasses, numpy, timestamps) to JSON-compatible data."""
    if val is None:
        return None
    if isinstance(val, (str, int, bool)):
        return val
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    if hasattr(val, "model_dump"):
        return to_json_serializable(val.model_dump())
    if hasattr(val, "dict") and callable(val.dict):
        return to_json_serializable(val.dict())
    if is_dataclass(val):
        return to_json_serializable(asdict(val))
    if hasattr(val, "to_dict") and callable(val.to_dict):
        return to_json_serializable(val.to_dict())
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if hasattr(val, "tolist") and callable(val.tolist):
        return to_json_serializable(val.tolist())
    if hasattr(val, "item") and callable(val.item):
        return to_json_serializable(val.item())
    if isinstance(val, dict):
        return {str(k): to_json_serializable(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [to_json_serializable(item) for item in val]
    return str(val)


class OrchestratorService:
    """Manages background multi-agent execution, event publication, and state persistence."""

    @staticmethod
    def start_analysis_async(
        dataset_id: str,
        target_column: str | None,
        model_task: str,
        missing_strategy: str,
        require_approval: bool,
        db: Session,
    ) -> AnalysisRunModel:
        dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset '{dataset_id}' does not exist.")

        analysis_id = f"anl_{uuid.uuid4().hex[:12]}"
        run_record = AnalysisRunModel(
            id=analysis_id,
            dataset_id=dataset_id,
            target_column=target_column,
            model_task=model_task,
            status="running",
        )
        db.add(run_record)
        db.commit()
        db.refresh(run_record)

        # Launch in background executor
        _EXECUTOR.submit(
            OrchestratorService._execute_run_worker,
            analysis_id=analysis_id,
            file_path=dataset.file_path,
            target_column=target_column,
            model_task=model_task,
            missing_strategy=missing_strategy,
            require_approval=require_approval,
        )

        return run_record

    @staticmethod
    def _execute_run_worker(
        analysis_id: str,
        file_path: str,
        target_column: str | None,
        model_task: str,
        missing_strategy: str,
        require_approval: bool,
        approvals: dict[str, bool] | None = None,
    ) -> None:
        db = SessionLocal()
        try:
            run = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == analysis_id).first()
            if not run:
                return

            def on_event(event: OrchestratorEvent) -> None:
                GLOBAL_EVENT_BROKER.publish_event(event)

            report_dir = settings.STORAGE_DIR / "reports" / analysis_id
            report_dir.mkdir(parents=True, exist_ok=True)
            report_target = str((report_dir / "executive_report.html").resolve())

            orchestrator = MasterOrchestrator(event_callback=on_event)
            res = orchestrator.run_analysis(
                dataset=file_path,
                target_column=target_column,
                model_task=model_task,
                missing_strategy=missing_strategy,
                require_approval=require_approval,
                approvals=approvals,
                run_id=analysis_id,
            )

            # Update DB with results
            run.status = res.get("status", "completed")
            run.duration_ms = res.get("duration_ms", 0.0)
            run.executive_summary = res.get("executive_summary")
            run.insights_json = json.dumps(to_json_serializable(res.get("insights", [])))
            run.report_path = res.get("report_path") or report_target

            raw_findings = res.get("all_findings") or []
            run.findings_json = json.dumps(to_json_serializable(raw_findings))

            if res.get("profile"):
                run.profile_json = json.dumps(to_json_serializable(res.get("profile")))
            if res.get("eda_results"):
                run.eda_json = json.dumps(to_json_serializable(res.get("eda_results")))
            if res.get("model_results"):
                run.model_results_json = json.dumps(to_json_serializable(res.get("model_results")))
                run.champion_model_name = res["model_results"].get("champion_model_name") or res["model_results"].get("model_name")
                run.champion_score = (
                    res["model_results"].get("champion_score")
                    or res["model_results"].get("f1_macro_mean")
                    or res["model_results"].get("rmse_mean")
                )
            if res.get("evaluation_results"):
                run.evaluation_json = json.dumps(to_json_serializable(res.get("evaluation_results")))

            # Register generated artifacts
            if res.get("report_path") and Path(res["report_path"]).exists():
                art = ArtifactModel(
                    id=f"art_{uuid.uuid4().hex[:12]}",
                    analysis_id=analysis_id,
                    artifact_type="html_report",
                    filename="executive_report.html",
                    file_path=res["report_path"],
                    file_size_bytes=Path(res["report_path"]).stat().st_size,
                )
                db.add(art)

            db.commit()

        except Exception as exc:
            logger.error("Run %s failed: %s", analysis_id, exc, exc_info=True)
            run = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == analysis_id).first()
            if run:
                run.status = "failed"
                run.executive_summary = f"Execution failed: {exc}"
                db.commit()
            GLOBAL_EVENT_BROKER.publish_event(
                OrchestratorEvent(event_type="RUN_FAILED", run_id=analysis_id, data={"error": str(exc)})
            )
        finally:
            db.close()

    @staticmethod
    def resume_analysis_with_approval(
        analysis_id: str,
        step: str,
        approved: bool,
        db: Session,
    ) -> AnalysisRunModel:
        run = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == analysis_id).first()
        if not run:
            raise ValueError(f"Analysis '{analysis_id}' not found.")

        dataset = db.query(DatasetModel).filter(DatasetModel.id == run.dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset for analysis '{analysis_id}' not found.")

        run.status = "running"
        db.commit()

        _EXECUTOR.submit(
            OrchestratorService._execute_run_worker,
            analysis_id=analysis_id,
            file_path=dataset.file_path,
            target_column=run.target_column,
            model_task=run.model_task or "auto",
            missing_strategy="median",
            require_approval=False,
            approvals={step: approved},
        )

        return run
