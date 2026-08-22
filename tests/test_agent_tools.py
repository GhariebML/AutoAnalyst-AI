"""Unit tests for the agent tool layer (M1).

Tools wrap deterministic modules and must work with no LLM configured.
Each tool is exercised through ``.invoke()`` the same way a LangGraph
node would call it, plus schema and error-path checks.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from autoanalyst.agents.tools import (
    ALL_TOOLS,
    clean_missing_values_tool,
    correlation_matrix_tool,
    create_report_tool,
    detect_high_cardinality_tool,
    encode_categoricals_tool,
    generate_insights_tool,
    load_dataset_tool,
    missing_values_report_tool,
    numeric_summary_tool,
    profile_dataset_tool,
)


def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "age": [20, 30, 30, None],
        "income": [1000, 2000, 2000, 3000],
        "city": ["Cairo", "Giza", "Giza", None],
    })


class TestToolRegistry:
    def test_all_tools_are_unique_base_tools(self) -> None:
        names = [t.name for t in ALL_TOOLS]
        assert len(names) == len(set(names))
        assert all(getattr(t, "name", None) for t in ALL_TOOLS)

    def test_expected_tool_names_registered(self) -> None:
        names = {t.name for t in ALL_TOOLS}
        assert {
            "load_dataset_tool",
            "profile_dataset_tool",
            "missing_values_report_tool",
            "numeric_summary_tool",
            "correlation_matrix_tool",
            "detect_high_cardinality_tool",
            "clean_missing_values_tool",
            "encode_categoricals_tool",
            "generate_insights_tool",
            "create_report_tool",
        } <= names


class TestLoadDatasetTool:
    def test_loads_csv(self, tmp_path: Path) -> None:
        path = tmp_path / "data.csv"
        sample_dataframe().to_csv(path, index=False)
        result = load_dataset_tool.invoke({"file_path": str(path)})
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["age", "income", "city"]

    def test_loads_excel(self, tmp_path: Path) -> None:
        pytest.importorskip("openpyxl")
        path = tmp_path / "data.xlsx"
        sample_dataframe().to_excel(path, index=False)
        result = load_dataset_tool.invoke({"file_path": str(path)})
        assert list(result.columns) == ["age", "income", "city"]

    def test_rejects_unsupported_extension(self) -> None:
        with pytest.raises(ValueError, match="Unsupported file type"):
            load_dataset_tool.invoke({"file_path": "table.parquet"})

    def test_rejects_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(Exception):
            load_dataset_tool.invoke({"file_path": str(tmp_path / "nope.csv")})


class TestProfilingTools:
    def test_profile_dataset_tool(self) -> None:
        profile = profile_dataset_tool.invoke({"df": sample_dataframe()})
        assert profile["rows"] == 4
        assert profile["columns"] == 3
        assert profile["duplicate_rows"] == 1
        assert profile["missing_values_total"] == 2

    def test_profile_empty_df_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            profile_dataset_tool.invoke({"df": pd.DataFrame()})

    def test_missing_values_report_sorted(self) -> None:
        report = missing_values_report_tool.invoke({"df": sample_dataframe()})
        assert report.iloc[0]["column"] in {"age", "city"}
        assert report["missing_count"].sum() == 2


class TestEdaTools:
    def test_numeric_summary(self) -> None:
        summary = numeric_summary_tool.invoke({"df": sample_dataframe()})
        assert set(summary.index) == {"age", "income"}

    def test_numeric_summary_no_numeric_columns_raises(self) -> None:
        df = pd.DataFrame({"city": ["a", "b"]})
        with pytest.raises(ValueError, match="[Nn]o numeric"):
            numeric_summary_tool.invoke({"df": df})

    def test_correlation_matrix_default_method(self) -> None:
        corr = correlation_matrix_tool.invoke({"df": sample_dataframe()})
        assert corr.shape == (2, 2)

    def test_correlation_matrix_spearman(self) -> None:
        corr = correlation_matrix_tool.invoke({"df": sample_dataframe(), "method": "spearman"})
        assert float(corr.loc["age", "age"]) == pytest.approx(1.0)


class TestFeatureTools:
    def test_detect_high_cardinality_auto_detect(self) -> None:
        results = detect_high_cardinality_tool.invoke({"df": sample_dataframe()})
        columns = {r["column"] for r in results}
        assert columns == {"city"}

    def test_encode_categoricals_one_hot(self) -> None:
        df = pd.DataFrame({"num": [1, 2], "cat": ["a", "b"]})
        encoded = encode_categoricals_tool.invoke({"df": df})
        assert "num" in encoded.columns
        assert "cat_b" in encoded.columns
        assert "cat" not in [column for column in encoded.columns if not column.startswith("cat_")]


class TestCleaningTools:
    def test_clean_dedupes_and_imputes(self) -> None:
        cleaned = clean_missing_values_tool.invoke({"df": sample_dataframe()})
        assert len(cleaned) == 3
        assert cleaned.isna().sum().sum() == 0

    def test_clean_drop_strategy(self) -> None:
        cleaned = clean_missing_values_tool.invoke({"df": sample_dataframe(), "strategy": "drop"})
        assert cleaned.isna().sum().sum() == 0

    def test_clean_invalid_strategy_raises(self) -> None:
        with pytest.raises(ValueError, match="strategy must be one of"):
            clean_missing_values_tool.invoke({"df": sample_dataframe(), "strategy": "invalid"})


class TestInsightAndReportTools:
    def test_generate_insights(self) -> None:
        insights = generate_insights_tool.invoke({"df": sample_dataframe()})
        assert insights
        assert any("4" in insight for insight in insights)

    def test_create_report_writes_file(self, tmp_path: Path) -> None:
        output = tmp_path / "report.md"
        result = create_report_tool.invoke({
            "insights": ["Row count is 4."],
            "output_path": str(output),
            "title": "T",
        })
        assert Path(result).exists()
        assert "# T" in output.read_text(encoding="utf-8")
