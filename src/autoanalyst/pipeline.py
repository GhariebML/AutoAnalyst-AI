"""End-to-end analysis pipeline for AutoAnalyst AI.

This module is the central integration layer. Feature teams should keep their
module functions focused, then connect them here so the dashboard and future
agent workflows can run one consistent system workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from autoanalyst.data_loading.loader import load_csv, load_excel
from autoanalyst.data_profiling.profiler import generate_basic_profile, get_missing_values_report
from autoanalyst.eda.analyzer import get_correlation_matrix, get_numeric_summary
from autoanalyst.evaluation.evaluator import evaluate_classification, evaluate_regression
from autoanalyst.feature_engineering.feature_builder import encode_categorical_columns
from autoanalyst.insights.insight_generator import generate_dataset_insights
from autoanalyst.modeling.classification import ClassificationModel
from autoanalyst.modeling.regression import RegressionModel
from autoanalyst.preprocessing.cleaner import handle_missing_values, remove_duplicates
from autoanalyst.reporting.report_generator import create_markdown_report

ModelTask = Literal["classification", "regression", "auto"]


@dataclass
class PipelineConfig:
    """Configuration for the end-to-end analysis pipeline."""

    target_column: str | None = None
    model_task: ModelTask = "auto"
    missing_strategy: str = "median"
    encode_categoricals: bool = True
    model_test_size: float = 0.2
    random_state: int = 42
    report_path: str | None = None


@dataclass
class PipelineResult:
    """Structured output contract returned by the pipeline."""

    raw_df: pd.DataFrame
    cleaned_df: pd.DataFrame
    model_ready_df: pd.DataFrame
    profile: dict[str, Any]
    missing_values_report: pd.DataFrame
    eda_results: dict[str, Any] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)
    model_results: dict[str, Any] | None = None
    evaluation_results: dict[str, Any] | None = None
    report_path: Path | None = None
    warnings: list[str] = field(default_factory=list)


def load_dataset(file_path: str) -> pd.DataFrame:
    """Load a dataset from CSV or Excel using the project loading contract."""
    suffix = Path(file_path).suffix.lower()
    if suffix == ".csv":
        return load_csv(file_path)
    if suffix in {".xlsx", ".xls"}:
        return load_excel(file_path)
    raise ValueError("Unsupported file type. Use CSV or Excel files.")


def run_analysis_pipeline(
    dataset: str | pd.DataFrame,
    config: PipelineConfig | None = None,
) -> PipelineResult:
    """Run the AutoAnalyst AI workflow from dataset input to dashboard-ready output.

    Parameters
    ----------
    dataset:
        Either a path to a CSV/Excel file or an already loaded pandas DataFrame.
    config:
        Optional pipeline configuration.

    Returns
    -------
    PipelineResult
        A structured result object containing profile, EDA, cleaned data,
        optional model/evaluation outputs, insights, and optional report path.
    """
    config = config or PipelineConfig()
    warnings: list[str] = []

    raw_df = load_dataset(dataset) if isinstance(dataset, str) else dataset.copy()
    if raw_df.empty:
        raise ValueError("Cannot run analysis on an empty dataset.")

    profile = generate_basic_profile(raw_df)
    missing_report = get_missing_values_report(raw_df)
    eda_results = _build_eda_results(raw_df, warnings)

    cleaned_df = handle_missing_values(remove_duplicates(raw_df), strategy=config.missing_strategy)
    model_ready_df = _build_model_ready_df(cleaned_df, config, warnings)

    model_results: dict[str, Any] | None = None
    evaluation_results: dict[str, Any] | None = None
    if config.target_column:
        model_results, evaluation_results = _train_and_evaluate(model_ready_df, config, warnings)

    insights = generate_dataset_insights(cleaned_df)
    if evaluation_results:
        insights.append("Model evaluation results were generated for the selected target column.")

    report_path = None
    if config.report_path:
        report_path = create_markdown_report("AutoAnalyst AI Report", insights, config.report_path)

    return PipelineResult(
        raw_df=raw_df,
        cleaned_df=cleaned_df,
        model_ready_df=model_ready_df,
        profile=profile,
        missing_values_report=missing_report,
        eda_results=eda_results,
        insights=insights,
        model_results=model_results,
        evaluation_results=evaluation_results,
        report_path=report_path,
        warnings=warnings,
    )


def _build_eda_results(df: pd.DataFrame, warnings: list[str]) -> dict[str, Any]:
    """Create EDA outputs while keeping the pipeline resilient."""
    eda_results: dict[str, Any] = {}
    try:
        eda_results["numeric_summary"] = get_numeric_summary(df)
    except ValueError as exc:
        warnings.append(str(exc))

    try:
        eda_results["correlation_matrix"] = get_correlation_matrix(df)
    except ValueError as exc:
        warnings.append(str(exc))

    return eda_results


def _build_model_ready_df(df: pd.DataFrame, config: PipelineConfig, warnings: list[str]) -> pd.DataFrame:
    """Prepare model-ready data using the feature engineering contract."""
    if not config.encode_categoricals:
        return df.copy()

    try:
        categorical_columns = list(df.select_dtypes(include=["object", "category"]).columns)
        if config.target_column in categorical_columns:
            categorical_columns.remove(config.target_column)
        return encode_categorical_columns(df, columns=categorical_columns)
    except KeyError as exc:
        warnings.append(f"Categorical encoding skipped: {exc}")
        return df.copy()


def _train_and_evaluate(
    df: pd.DataFrame,
    config: PipelineConfig,
    warnings: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Train and evaluate a baseline model when a target column is configured."""
    if config.target_column not in df.columns:
        warnings.append(f"Target column not found after preprocessing: {config.target_column}")
        return None, None

    X = df.drop(columns=[config.target_column])
    y = df[config.target_column]
    if X.empty or y.empty:
        warnings.append("Modeling skipped because features or target are empty.")
        return None, None

    task = _detect_model_task(y, config.model_task)
    if task == "classification":
        model = ClassificationModel(random_state=config.random_state)
        test_size = _safe_classification_test_size(y, config.model_test_size)
        X_train, X_test, y_train, y_test = model.train(X, y, test_size=test_size)
        predictions = model.predict(X_test)
        return (
            {"task": task, "model_name": "RandomForestClassifier", "train_rows": len(X_train), "test_rows": len(X_test)},
            evaluate_classification(y_test, predictions),
        )

    model = RegressionModel(random_state=config.random_state)
    X_train, X_test, y_train, y_test = model.train(X, y, test_size=config.model_test_size)
    predictions = model.predict(X_test)
    return (
        {"task": task, "model_name": "RandomForestRegressor", "train_rows": len(X_train), "test_rows": len(X_test)},
        evaluate_regression(y_test, predictions),
    )


def _detect_model_task(y: pd.Series, configured_task: ModelTask) -> Literal["classification", "regression"]:
    """Infer a simple modeling task when configured as auto."""
    if configured_task in {"classification", "regression"}:
        return configured_task
    if pd.api.types.is_numeric_dtype(y) and y.nunique() > 10:
        return "regression"
    return "classification"


def _safe_classification_test_size(y: pd.Series, requested_test_size: float) -> float:
    """Choose a test size that works for small stratified classification datasets."""
    class_count = max(int(y.nunique()), 1)
    row_count = max(len(y), 1)
    minimum_fraction = min(0.5, class_count / row_count)
    return max(requested_test_size, minimum_fraction)
