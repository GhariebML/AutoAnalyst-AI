"""Unit tests for the dedicated analytical Tool Layer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from autoanalyst.tools import (
    ALL_ANALYTICAL_TOOLS,
    BenchmarkModelsInput,
    BenchmarkModelsTool,
    CompileReportInput,
    CompileReportTool,
    CorrelationAnalysisTool,
    CorrelationInput,
    DistributionAnalysisTool,
    DistributionInput,
    EncodeFeaturesInput,
    EncodeFeaturesTool,
    EvaluateModelInput,
    EvaluateModelTool,
    ExecuteCleaningInput,
    ExecuteCleaningTool,
    GenerateTransformationPlanTool,
    InferMLTaskInput,
    InferMLTaskTool,
    LoadDatasetInput,
    LoadDatasetTool,
    MissingnessReportInput,
    MissingnessReportTool,
    OutlierDetectionInput,
    OutlierDetectionTool,
    PreviewDatasetInput,
    PreviewDatasetTool,
    ProfileDatasetInput,
    ProfileDatasetTool,
    TransformationPlanInput,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
            "income": [50000.0, 60000.0, 75000.0, None, 90000.0, 105000.0, 120000.0, 135000.0, 150000.0, 500000.0],
            "category": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
            "default": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        }
    )


class TestToolLayer:
    def test_all_tools_registry(self) -> None:
        assert len(ALL_ANALYTICAL_TOOLS) >= 10
        names = [t.metadata.name for t in ALL_ANALYTICAL_TOOLS]
        assert len(names) == len(set(names))

    def test_data_loading_tools(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        csv_file = tmp_path / "data.csv"
        sample_df.to_csv(csv_file, index=False)

        load_tool = LoadDatasetTool()
        res = load_tool.execute(LoadDatasetInput(file_path=str(csv_file)))
        assert res.is_success
        assert res.data.rows == 10
        assert res.data.columns == 4

        preview_tool = PreviewDatasetTool()
        p_res = preview_tool.execute(PreviewDatasetInput(file_path=str(csv_file), n_rows=5))
        assert p_res.is_success
        assert len(p_res.data.preview_records) == 5

    def test_profiling_tools(self, sample_df: pd.DataFrame) -> None:
        prof_tool = ProfileDatasetTool()
        res = prof_tool.execute(ProfileDatasetInput(df=sample_df))
        assert res.is_success
        assert res.data.rows == 10
        assert res.data.health_score > 0

        miss_tool = MissingnessReportTool()
        m_res = miss_tool.execute(MissingnessReportInput(df=sample_df))
        assert m_res.is_success
        assert m_res.data.has_missing_values

    def test_eda_tools(self, sample_df: pd.DataFrame) -> None:
        corr_tool = CorrelationAnalysisTool()
        c_res = corr_tool.execute(CorrelationInput(df=sample_df, method="pearson"))
        assert c_res.is_success
        assert "age" in c_res.data.matrix

        dist_tool = DistributionAnalysisTool()
        d_res = dist_tool.execute(DistributionInput(df=sample_df))
        assert d_res.is_success
        assert len(d_res.data.distributions) > 0

        out_tool = OutlierDetectionTool()
        o_res = out_tool.execute(OutlierDetectionInput(df=sample_df, method="iqr"))
        assert o_res.is_success
        assert o_res.data.total_outliers_detected >= 0

    def test_preprocessing_and_ml_tools(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        plan_tool = GenerateTransformationPlanTool()
        p_res = plan_tool.execute(TransformationPlanInput(df=sample_df, target_column="default"))
        assert p_res.is_success
        assert p_res.data.total_actions > 0

        clean_tool = ExecuteCleaningTool()
        c_res = clean_tool.execute(ExecuteCleaningInput(df=sample_df, missing_strategy="median"))
        assert c_res.is_success
        assert c_res.data.cleaned_rows == 10

        enc_tool = EncodeFeaturesTool()
        e_res = enc_tool.execute(EncodeFeaturesInput(df=c_res.data.cleaned_df, target_column="default"))
        assert e_res.is_success

        infer_tool = InferMLTaskTool()
        i_res = infer_tool.execute(InferMLTaskInput(y=sample_df["default"]))
        assert i_res.is_success
        assert i_res.data.task == "classification"

        X = e_res.data.encoded_df.drop(columns=["default"])
        y = e_res.data.encoded_df["default"]

        bench_tool = BenchmarkModelsTool()
        b_res = bench_tool.execute(BenchmarkModelsInput(X=X, y=y, task="classification", cv=2))
        assert b_res.is_success
        assert len(b_res.data.leaderboard) >= 2

        eval_tool = EvaluateModelTool()
        ev_res = eval_tool.execute(EvaluateModelInput(y_true=[0, 1, 0, 1], y_pred=[0, 1, 0, 0], task="classification"))
        assert ev_res.is_success
        assert "accuracy" in ev_res.data.scalar_metrics

        report_file = tmp_path / "tool_report.html"
        rep_tool = CompileReportTool()
        rep_res = rep_tool.execute(
            CompileReportInput(
                output_path=str(report_file),
                title="Test Report",
                format="html",
                profile={"rows": 10},
                insights=["Test insight"],
            )
        )
        assert rep_res.is_success
        assert report_file.exists()
