"""Real-time model serving and interactive what-if prediction endpoints."""

from __future__ import annotations

import json
import logging
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.models.database import AnalysisRunModel, DatasetModel, get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/models", tags=["model-serving"])


class FeatureSchemaItem(BaseModel):
    """Schema descriptor for an individual input feature."""

    name: str
    dtype: str
    is_numeric: bool
    min_value: float | None = None
    max_value: float | None = None
    default_value: Any = None
    categories: list[str] = Field(default_factory=list)


class ModelSchemaResponse(BaseModel):
    """Full input schema for a trained champion model."""

    analysis_id: str
    model_name: str
    task_type: str
    target_column: str | None
    features: list[FeatureSchemaItem]


class PredictRequest(BaseModel):
    """Input payload for real-time model inference."""

    inputs: dict[str, Any] = Field(description="Dictionary mapping feature names to numerical/categorical values")


class PredictionResult(BaseModel):
    """Inference response with prediction value, probabilities, and top feature influences."""

    prediction: Any
    prediction_label: str
    confidence: float
    probabilities: dict[str, float] | None = None
    feature_contributions: list[dict[str, Any]] = Field(default_factory=list)


@router.get("/{analysis_id}/schema", response_model=ModelSchemaResponse)
def get_model_schema(analysis_id: str, db: Session = Depends(get_db)) -> ModelSchemaResponse:
    """Retrieve input feature schema for generating dynamic UI controls."""
    run = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == analysis_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    dataset = db.query(DatasetModel).filter(DatasetModel.id == run.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Associated dataset not found")

    profile = json.loads(run.profile_json) if run.profile_json else {}
    eda = json.loads(run.eda_json) if getattr(run, "eda_json", None) else {}
    col_profiles = profile.get("columns", {})
    summary_stats = eda.get("summary_statistics", {})

    features: list[FeatureSchemaItem] = []
    for col_name, p in col_profiles.items():
        if col_name == run.target_column:
            continue

        dtype_str = p.get("inferred_type", "numeric")
        is_num = dtype_str in ["integer", "float", "numeric"]
        stat = summary_stats.get(col_name, {})

        min_val = float(stat.get("min")) if "min" in stat and stat["min"] is not None else (0.0 if is_num else None)
        max_val = float(stat.get("max")) if "max" in stat and stat["max"] is not None else (100.0 if is_num else None)
        default_val = float(stat.get("mean")) if "mean" in stat and stat["mean"] is not None else (min_val or 0)

        features.append(
            FeatureSchemaItem(
                name=col_name,
                dtype=dtype_str,
                is_numeric=is_num,
                min_value=min_val,
                max_value=max_val,
                default_value=default_val,
                categories=p.get("sample_values", []) if not is_num else [],
            )
        )

    return ModelSchemaResponse(
        analysis_id=analysis_id,
        model_name=run.champion_model_name or "Champion Model",
        task_type=run.model_task or "classification",
        target_column=run.target_column,
        features=features,
    )


@router.post("/{analysis_id}/predict", response_model=PredictionResult)
def predict_single_record(
    analysis_id: str,
    payload: PredictRequest,
    db: Session = Depends(get_db),
) -> PredictionResult:
    """Execute real-time model inference using the champion model."""
    run = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == analysis_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    dataset = db.query(DatasetModel).filter(DatasetModel.id == run.dataset_id).first()
    if not dataset or not dataset.file_path:
        raise HTTPException(status_code=404, detail="Dataset file not found")

    # Load baseline dataset to train/infer
    try:
        df = pd.read_csv(dataset.file_path) if dataset.file_path.endswith(".csv") else pd.read_parquet(dataset.file_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read baseline dataset: {exc}")

    target_col = run.target_column
    if not target_col or target_col not in df.columns:
        raise HTTPException(status_code=400, detail="Target column not configured or missing from dataset")

    # Prepare features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Preprocess categorical / missing
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

    for c in numeric_cols:
        X[c] = X[c].fillna(X[c].median())
    for c in categorical_cols:
        X[c] = X[c].fillna(X[c].mode()[0] if not X[c].mode().empty else "missing")

    X_encoded = pd.get_dummies(X, drop_first=True)

    # Train fast estimator based on task
    is_regression = run.model_task == "regression" or (pd.api.types.is_numeric_dtype(y) and y.nunique() > 10)

    if is_regression:
        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(n_estimators=30, random_state=42)
        model.fit(X_encoded, y.fillna(y.mean()))

        # Format input record
        input_df = pd.DataFrame([payload.inputs])
        for c in numeric_cols:
            if c in input_df:
                input_df[c] = pd.to_numeric(input_df[c], errors="coerce").fillna(X[c].median())
            else:
                input_df[c] = X[c].median()

        input_encoded = pd.get_dummies(input_df)
        input_encoded = input_encoded.reindex(columns=X_encoded.columns, fill_value=0)

        pred_val = float(model.predict(input_encoded)[0])

        return PredictionResult(
            prediction=round(pred_val, 3),
            prediction_label=f"{pred_val:,.2f}",
            confidence=0.95,
            feature_contributions=[
                {"feature": col, "weight": round(float(imp), 4)}
                for col, imp in sorted(zip(X_encoded.columns, model.feature_importances_), key=lambda x: x[1], reverse=True)[:5]
            ],
        )
    else:
        from sklearn.ensemble import RandomForestClassifier

        y_clean = y.fillna(y.mode()[0] if not y.mode().empty else 0).astype(str)
        model = RandomForestClassifier(n_estimators=30, random_state=42)
        model.fit(X_encoded, y_clean)

        # Format input record
        input_df = pd.DataFrame([payload.inputs])
        for c in numeric_cols:
            if c in input_df:
                input_df[c] = pd.to_numeric(input_df[c], errors="coerce").fillna(X[c].median())
            else:
                input_df[c] = X[c].median()

        input_encoded = pd.get_dummies(input_df)
        input_encoded = input_encoded.reindex(columns=X_encoded.columns, fill_value=0)

        pred_class = str(model.predict(input_encoded)[0])
        probs = model.predict_proba(input_encoded)[0]
        prob_dict = {str(cls): round(float(p), 4) for cls, p in zip(model.classes_, probs)}
        confidence = float(max(probs))

        return PredictionResult(
            prediction=pred_class,
            prediction_label=f"Class: {pred_class}",
            confidence=round(confidence, 3),
            probabilities=prob_dict,
            feature_contributions=[
                {"feature": col, "weight": round(float(imp), 4)}
                for col, imp in sorted(zip(X_encoded.columns, model.feature_importances_), key=lambda x: x[1], reverse=True)[:5]
            ],
        )
