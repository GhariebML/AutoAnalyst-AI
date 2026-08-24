"""Dataset management API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.models.database import DatasetModel, get_db
from backend.app.schemas.dataset import DatasetPreviewResponse, DatasetResponse
from backend.app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetResponse, status_code=201)
def upload_dataset(file: UploadFile, db: Session = Depends(get_db)) -> DatasetResponse:
    """Upload and profile a dataset file (CSV, Excel, Parquet, JSON, SQLite)."""
    try:
        record = DatasetService.save_and_register_dataset(file, db)
        return DatasetResponse.model_validate(record)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)) -> list[DatasetResponse]:
    """List all registered datasets."""
    records = db.query(DatasetModel).order_by(DatasetModel.created_at.desc()).all()
    return [DatasetResponse.model_validate(r) for r in records]


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)) -> DatasetResponse:
    """Get metadata for a specific dataset."""
    record = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetResponse.model_validate(record)


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def get_dataset_preview(dataset_id: str, db: Session = Depends(get_db)) -> DatasetPreviewResponse:
    """Get data preview rows and schema metrics for a dataset."""
    try:
        return DatasetService.get_dataset_preview(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
