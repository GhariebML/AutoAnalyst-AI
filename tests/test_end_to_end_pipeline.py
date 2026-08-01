"""Integration tests for the AutoAnalyst AI end-to-end pipeline."""

import pandas as pd

from autoanalyst.pipeline import PipelineConfig, run_analysis_pipeline


def test_run_analysis_pipeline_without_modeling(tmp_path) -> None:
    df = pd.DataFrame({
        "age": [25, 32, 32, None],
        "income": [50000, 65000, 65000, 80000],
        "city": ["Cairo", "Giza", "Giza", None],
    })
    report_path = tmp_path / "report.md"

    result = run_analysis_pipeline(df, PipelineConfig(report_path=str(report_path)))

    assert result.profile["rows"] == 4
    assert result.cleaned_df.isna().sum().sum() == 0
    assert len(result.cleaned_df) == 3
    assert "numeric_summary" in result.eda_results
    assert result.insights
    assert result.report_path == report_path
    assert report_path.exists()


def test_run_analysis_pipeline_with_classification_target() -> None:
    df = pd.DataFrame({
        "age": [25, 32, 41, 29, 36, 45],
        "income": [50000, 65000, 80000, 52000, 70000, 90000],
        "city": ["Cairo", "Giza", "Alexandria", "Cairo", "Giza", "Alexandria"],
        "purchased": ["yes", "no", "yes", "no", "yes", "no"],
    })

    result = run_analysis_pipeline(df, PipelineConfig(target_column="purchased", model_task="classification"))

    assert result.model_results is not None
    assert result.model_results["task"] == "classification"
    assert result.evaluation_results is not None
    assert "accuracy" in result.evaluation_results
