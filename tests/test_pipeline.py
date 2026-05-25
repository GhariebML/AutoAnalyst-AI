"""Basic tests for the AutoAnalyst AI starter pipeline."""

import pandas as pd

from autoanalyst.data_profiling.profiler import generate_basic_profile, get_duplicate_count
from autoanalyst.eda.analyzer import get_numeric_summary
from autoanalyst.insights.insight_generator import generate_dataset_insights
from autoanalyst.preprocessing.cleaner import handle_missing_values, remove_duplicates
from autoanalyst.reporting.report_generator import create_markdown_report


def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "age": [20, 30, 30, None],
        "income": [1000, 2000, 2000, 3000],
        "city": ["Cairo", "Giza", "Giza", None],
    })


def test_generate_basic_profile() -> None:
    df = sample_dataframe()
    profile = generate_basic_profile(df)
    assert profile["rows"] == 4
    assert profile["columns"] == 3
    assert profile["missing_values_total"] == 2


def test_cleaning_helpers() -> None:
    df = sample_dataframe()
    no_duplicates = remove_duplicates(df)
    assert len(no_duplicates) == 3
    cleaned = handle_missing_values(df)
    assert cleaned.isna().sum().sum() == 0


def test_eda_and_insights() -> None:
    df = sample_dataframe()
    summary = get_numeric_summary(df)
    insights = generate_dataset_insights(df)
    assert "age" in summary.index
    assert get_duplicate_count(df) == 1
    assert insights


def test_create_markdown_report(tmp_path) -> None:
    output_path = tmp_path / "analysis_report.md"
    report_path = create_markdown_report(
        title="Sample Analysis",
        insights=["Dataset has 4 rows.", "No missing values after cleaning."],
        output_path=str(output_path),
    )

    assert report_path == output_path
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == (
        "# Sample Analysis\n"
        "\n"
        "## Key Insights\n"
        "\n"
        "- Dataset has 4 rows.\n"
        "- No missing values after cleaning.\n"
    )
