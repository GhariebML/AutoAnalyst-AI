"""Service layer for dataset management and profiling."""

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from autoanalyst.data_loading.loader import load_dataset
from autoanalyst.data_profiling.profiler import profile_dataframe
from backend.app.core.config import settings
from backend.app.models.database import DatasetModel
from backend.app.schemas.dataset import DatasetPreviewResponse


class DatasetService:
    """Handles dataset ingestion, validation, profiling, and storage."""

    @staticmethod
    def save_and_register_dataset(file: UploadFile, db: Session) -> DatasetModel:
        dataset_id = f"ds_{uuid.uuid4().hex[:12]}"
        filename = file.filename or "dataset.csv"
        suffix = Path(filename).suffix.lower()

        dataset_dir = settings.STORAGE_DIR / "datasets" / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)
        file_path = dataset_dir / filename

        with open(file_path, "wb") as f_out:
            shutil.copyfileobj(file.file, f_out)

        file_size = file_path.stat().st_size
        df = load_dataset(str(file_path))
        profile = profile_dataframe(df)
        schema_info = {
            "columns": list(df.columns),
            "dtypes": {str(c): str(t) for c, t in df.dtypes.items()},
            "column_profiles": {
                k: (
                    asdict(v)
                    if hasattr(v, "__dataclass_fields__")
                    else (v.to_dict() if hasattr(v, "to_dict") else str(v))
                )
                for k, v in profile.column_profiles.items()
            },
        }

        dataset_record = DatasetModel(
            id=dataset_id,
            filename=filename,
            file_path=str(file_path.resolve()),
            file_size_bytes=file_size,
            file_format=suffix.lstrip("."),
            rows=int(df.shape[0]),
            columns=int(df.shape[1]),
            health_score=float(profile.quality_report.health_score),
            schema_json=json.dumps(schema_info),
        )

        db.add(dataset_record)
        db.commit()
        db.refresh(dataset_record)
        return dataset_record

    @staticmethod
    def get_dataset_preview(dataset_id: str, db: Session) -> DatasetPreviewResponse:
        record = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
        if not record:
            raise ValueError(f"Dataset '{dataset_id}' not found.")

        df = load_dataset(record.file_path)
        preview_records = df.head(15).to_dict(orient="records")
        schema_data = json.loads(record.schema_json) if record.schema_json else {}

        return DatasetPreviewResponse(
            id=record.id,
            filename=record.filename,
            rows=record.rows or len(df),
            columns=record.columns or len(df.columns),
            column_names=list(df.columns),
            health_score=record.health_score or 100.0,
            data_preview=preview_records,
            column_profiles=schema_data.get("column_profiles", {}),
        )
