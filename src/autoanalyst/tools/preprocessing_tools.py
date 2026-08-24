"""Preprocessing, data cleaning, and feature engineering tools for AutoAnalyst AI."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, Field

from autoanalyst.feature_engineering.feature_builder import (
    detect_high_cardinality_columns,
    encode_categorical_columns,
)
from autoanalyst.preprocessing.cleaner import (
    clean_dataset,
)
from autoanalyst.tools.base import BaseAnalyticalTool, ToolMetadata


# ---------------------------------------------------------------------------
# 1. GenerateTransformationPlanTool
# ---------------------------------------------------------------------------
class TransformationPlanInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to assess for preprocessing")
    target_column: str | None = Field(None, description="Optional target column for ML modeling")


class PlannedAction(BaseModel):
    step: str
    column: str | None
    action: str
    reason: str
    impact_estimate: str
    requires_approval: bool = False


class TransformationPlanOutput(BaseModel):
    total_actions: int
    plan: list[PlannedAction]


class GenerateTransformationPlanTool(BaseAnalyticalTool[TransformationPlanInput, TransformationPlanOutput]):
    metadata = ToolMetadata(
        name="generate_preprocessing_plan",
        description="Inspect data issues and formulate a prioritized transformation plan before execution.",
        category="preprocessing",
        tags=["planning", "imputation", "audit", "hitl"],
    )

    def _run(self, params: TransformationPlanInput) -> TransformationPlanOutput:
        df: pd.DataFrame = params.df
        actions: list[PlannedAction] = []

        # 1. Check Duplicates
        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            actions.append(
                PlannedAction(
                    step="deduplication",
                    column=None,
                    action="remove_duplicates",
                    reason=f"{dup_count} duplicate row(s) identified.",
                    impact_estimate=f"Dataset size will decrease by {dup_count} rows.",
                )
            )

        # 2. Check Missingness per column
        for col in df.columns:
            missing = int(df[col].isna().sum())
            if missing > 0:
                pct = (missing / len(df)) * 100.0
                if pd.api.types.is_numeric_dtype(df[col]):
                    skew = float(df[col].dropna().skew()) if len(df[col].dropna()) > 2 else 0.0
                    action = "median" if abs(skew) > 1.0 else "mean"
                    reason = (
                        f"Distribution is skewed (skewness = {skew:.2f}); median imputation is robust."
                        if abs(skew) > 1.0
                        else "Distribution is symmetric; mean imputation preserves expected value."
                    )
                else:
                    action = "mode"
                    reason = "Categorical variable; mode represents the most frequent category."

                actions.append(
                    PlannedAction(
                        step="imputation",
                        column=str(col),
                        action=action,
                        reason=reason,
                        impact_estimate=f"{missing} missing cell(s) ({pct:.1f}%) will be imputed.",
                        requires_approval=pct >= 25.0,
                    )
                )

        # 3. Check High Cardinality
        card_cols = detect_high_cardinality_columns(df)
        for card in card_cols:
            col_name = str(card.get("column"))
            if col_name != params.target_column:
                actions.append(
                    PlannedAction(
                        step="encoding",
                        column=col_name,
                        action="frequency_or_target_encoding",
                        reason=f"High cardinality ({card.get('unique_values')} unique categories).",
                        impact_estimate="Prevents feature explosion compared to one-hot encoding.",
                    )
                )

        return TransformationPlanOutput(
            total_actions=len(actions),
            plan=actions,
        )


# ---------------------------------------------------------------------------
# 2. ExecuteCleaningTool
# ---------------------------------------------------------------------------
class ExecuteCleaningInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to clean")
    missing_strategy: str = Field("median", description="Strategy: median, mean, mode, knn, forward_fill, drop")
    handle_outliers: Literal["none", "winsorize"] = Field("winsorize", description="Outlier handling strategy")
    drop_duplicates: bool = Field(True, description="Whether to deduplicate rows")


class ExecuteCleaningOutput(BaseModel):
    cleaned_rows: int
    cleaned_columns: int
    duplicates_removed: int
    imputations_performed: int
    cleaning_logs: list[dict[str, Any]]
    cleaned_df: Any = Field(None, exclude=True)


class ExecuteCleaningTool(BaseAnalyticalTool[ExecuteCleaningInput, ExecuteCleaningOutput]):
    metadata = ToolMetadata(
        name="execute_cleaning",
        description="Execute end-to-end data cleaning with missing value imputation, deduplication, and winsorization.",
        category="preprocessing",
        tags=["cleaning", "imputation", "deduplication", "winsorization"],
    )

    def _run(self, params: ExecuteCleaningInput) -> ExecuteCleaningOutput:
        result = clean_dataset(
            params.df,
            missing_strategy=params.missing_strategy,
            handle_outliers=params.handle_outliers,
            drop_duplicate_rows=params.drop_duplicates,
        )
        return ExecuteCleaningOutput(
            cleaned_rows=len(result.cleaned_df),
            cleaned_columns=len(result.cleaned_df.columns),
            duplicates_removed=result.total_duplicates_removed,
            imputations_performed=result.total_missing_imputed,
            cleaning_logs=[entry.to_dict() for entry in result.log],
            cleaned_df=result.cleaned_df,
        )


# ---------------------------------------------------------------------------
# 3. EncodeFeaturesTool
# ---------------------------------------------------------------------------
class EncodeFeaturesInput(BaseModel):
    df: Any = Field(..., description="Pandas DataFrame to encode")
    target_column: str | None = Field(None, description="Target column to exclude from feature encoding")
    method: Literal["onehot", "frequency"] = Field("onehot", description="Encoding method")


class EncodeFeaturesOutput(BaseModel):
    original_columns: int
    encoded_columns: int
    encoded_column_names: list[str]
    encoded_df: Any = Field(None, exclude=True)


class EncodeFeaturesTool(BaseAnalyticalTool[EncodeFeaturesInput, EncodeFeaturesOutput]):
    metadata = ToolMetadata(
        name="encode_features",
        description="Encode categorical features using one-hot or frequency encoding contracts.",
        category="feature_engineering",
        tags=["encoding", "onehot", "features"],
    )

    def _run(self, params: EncodeFeaturesInput) -> EncodeFeaturesOutput:
        df: pd.DataFrame = params.df.copy()
        cat_cols = list(df.select_dtypes(include=["object", "category", "string"]).columns)
        if params.target_column and params.target_column in cat_cols:
            cat_cols.remove(params.target_column)

        if not cat_cols:
            return EncodeFeaturesOutput(
                original_columns=df.shape[1],
                encoded_columns=df.shape[1],
                encoded_column_names=list(df.columns),
                encoded_df=df,
            )

        encoded_df = encode_categorical_columns(df, columns=cat_cols)
        return EncodeFeaturesOutput(
            original_columns=df.shape[1],
            encoded_columns=encoded_df.shape[1],
            encoded_column_names=[str(c) for c in encoded_df.columns],
            encoded_df=encoded_df,
        )
