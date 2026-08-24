"""Machine learning benchmarking and model training tools for AutoAnalyst AI."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, Field

from autoanalyst.modeling.classification import benchmark_classification_models
from autoanalyst.modeling.regression import benchmark_regression_models
from autoanalyst.tools.base import BaseAnalyticalTool, ToolMetadata


# ---------------------------------------------------------------------------
# 1. InferMLTaskTool
# ---------------------------------------------------------------------------
class InferMLTaskInput(BaseModel):
    y: Any = Field(..., description="Target variable Series or list")
    configured_task: Literal["auto", "classification", "regression"] = "auto"


class InferMLTaskOutput(BaseModel):
    task: Literal["classification", "regression"]
    unique_classes: int
    is_numeric: bool
    rationale: str


class InferMLTaskTool(BaseAnalyticalTool[InferMLTaskInput, InferMLTaskOutput]):
    metadata = ToolMetadata(
        name="infer_ml_task",
        description="Inspect target variable and determine whether problem is classification or regression.",
        category="modeling",
        tags=["task_detection", "ml"],
    )

    def _run(self, params: InferMLTaskInput) -> InferMLTaskOutput:
        s = pd.Series(params.y)
        is_num = bool(pd.api.types.is_numeric_dtype(s))
        nunique = int(s.nunique())

        if params.configured_task == "classification":
            if is_num and (pd.api.types.is_float_dtype(s) or nunique > 20):
                return InferMLTaskOutput(
                    task="regression",
                    unique_classes=nunique,
                    is_numeric=is_num,
                    rationale=f"Auto-corrected to regression: target is continuous numeric with {nunique} distinct values.",
                )
            return InferMLTaskOutput(
                task="classification",
                unique_classes=nunique,
                is_numeric=is_num,
                rationale="Explicitly configured as 'classification'.",
            )

        if params.configured_task == "regression":
            return InferMLTaskOutput(
                task="regression",
                unique_classes=nunique,
                is_numeric=is_num,
                rationale="Explicitly configured as 'regression'.",
            )

        if is_num and nunique > 10:
            return InferMLTaskOutput(
                task="regression",
                unique_classes=nunique,
                is_numeric=is_num,
                rationale=f"Numeric target with {nunique} distinct continuous values.",
            )
        return InferMLTaskOutput(
            task="classification",
            unique_classes=nunique,
            is_numeric=is_num,
            rationale=f"Categorical or low-cardinality target ({nunique} classes).",
        )


# ---------------------------------------------------------------------------
# 2. BenchmarkModelsTool
# ---------------------------------------------------------------------------
class BenchmarkModelsInput(BaseModel):
    X: Any = Field(..., description="Features DataFrame")
    y: Any = Field(..., description="Target Series")
    task: Literal["classification", "regression"] = Field("classification", description="ML task")
    cv: int = Field(3, ge=2, le=10, description="Cross-validation folds")


class BenchmarkModelsOutput(BaseModel):
    task: str
    leaderboard: list[dict[str, Any]]
    champion_model_name: str
    champion_score: float
    champion_metric: str
    champion_estimator: Any = Field(None, exclude=True)


class BenchmarkModelsTool(BaseAnalyticalTool[BenchmarkModelsInput, BenchmarkModelsOutput]):
    metadata = ToolMetadata(
        name="benchmark_models",
        description="Benchmark a zoo of candidate algorithms via cross-validation and determine the champion model.",
        category="modeling",
        tags=["benchmark", "leaderboard", "model_zoo"],
    )

    def _run(self, params: BenchmarkModelsInput) -> BenchmarkModelsOutput:
        X = pd.DataFrame(params.X)
        y = pd.Series(params.y)

        if params.task == "classification":
            leaderboard_df, champion = benchmark_classification_models(X, y, cv=params.cv)
            top_row = leaderboard_df.iloc[0]
            return BenchmarkModelsOutput(
                task=params.task,
                leaderboard=leaderboard_df.to_dict(orient="records"),
                champion_model_name=str(top_row["model_name"]),
                champion_score=float(top_row["f1_macro_mean"]),
                champion_metric="f1_macro",
                champion_estimator=champion,
            )

        leaderboard_df, champion = benchmark_regression_models(X, y, cv=params.cv)
        top_row = leaderboard_df.iloc[0]
        return BenchmarkModelsOutput(
            task=params.task,
            leaderboard=leaderboard_df.to_dict(orient="records"),
            champion_model_name=str(top_row["model_name"]),
            champion_score=float(top_row["rmse_mean"]),
            champion_metric="rmse",
            champion_estimator=champion,
        )
