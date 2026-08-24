"""Model evaluation, diagnostics, and explainability tools for AutoAnalyst AI."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, Field

from autoanalyst.evaluation.evaluator import (
    calculate_permutation_importance,
    evaluate_classification,
    evaluate_regression,
)
from autoanalyst.tools.base import BaseAnalyticalTool, ToolMetadata


# ---------------------------------------------------------------------------
# 1. EvaluateModelTool
# ---------------------------------------------------------------------------
class EvaluateModelInput(BaseModel):
    y_true: Any = Field(..., description="Ground truth target values")
    y_pred: Any = Field(..., description="Predicted target values")
    y_proba: Any = Field(None, description="Optional predicted probabilities for classification")
    task: Literal["classification", "regression"] = Field("classification", description="ML task type")


class EvaluateModelOutput(BaseModel):
    task: str
    scalar_metrics: dict[str, float]
    detailed_metrics: dict[str, Any]


class EvaluateModelTool(BaseAnalyticalTool[EvaluateModelInput, EvaluateModelOutput]):
    metadata = ToolMetadata(
        name="evaluate_model",
        description="Compute comprehensive model evaluation metrics, confusion matrices, or residual diagnostics.",
        category="evaluation",
        tags=["evaluation", "metrics", "diagnostics"],
    )

    def _run(self, params: EvaluateModelInput) -> EvaluateModelOutput:
        if params.task == "classification":
            raw_metrics = evaluate_classification(
                y_true=params.y_true,
                y_pred=params.y_pred,
                y_proba=params.y_proba,
            )
            scalars = {
                k: round(float(v), 4)
                for k, v in raw_metrics.items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)
            }
            return EvaluateModelOutput(
                task="classification",
                scalar_metrics=scalars,
                detailed_metrics=raw_metrics,
            )

        raw_metrics = evaluate_regression(
            y_true=params.y_true,
            y_pred=params.y_pred,
        )
        scalars = {
            k: round(float(v), 4)
            for k, v in raw_metrics.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        return EvaluateModelOutput(
            task="regression",
            scalar_metrics=scalars,
            detailed_metrics=raw_metrics,
        )


# ---------------------------------------------------------------------------
# 2. PermutationImportanceTool
# ---------------------------------------------------------------------------
class PermutationImportanceInput(BaseModel):
    estimator: Any = Field(..., description="Trained model estimator object")
    X_val: Any = Field(..., description="Validation features DataFrame")
    y_val: Any = Field(..., description="Validation ground truth Series")


class PermutationImportanceOutput(BaseModel):
    feature_importances: dict[str, float]
    top_driver_features: list[str]


class PermutationImportanceTool(BaseAnalyticalTool[PermutationImportanceInput, PermutationImportanceOutput]):
    metadata = ToolMetadata(
        name="calculate_feature_importances",
        description="Compute model-agnostic permutation feature importances on holdout validation data.",
        category="evaluation",
        tags=["explainability", "feature_importance", "drivers"],
    )

    def _run(self, params: PermutationImportanceInput) -> PermutationImportanceOutput:
        X = pd.DataFrame(params.X_val)
        y = pd.Series(params.y_val)
        importances = calculate_permutation_importance(params.estimator, X, y)
        top_features = list(importances.keys())[:5]
        return PermutationImportanceOutput(
            feature_importances=importances,
            top_driver_features=top_features,
        )
