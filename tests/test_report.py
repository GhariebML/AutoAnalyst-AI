"""Unit tests for autoanalyst/eda/report.py"""

import pandas as pd
import pytest

from autoanalyst.eda.report import generate_eda_html_report


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "age": [25, 30, 35, 40, 45, 50],
            "income": [50000, 60000, 75000, 80000, 95000, 40000],
            "loan_grade": ["A", "B", "A", "C", "B", "A"],
            "loan_status": [0, 1, 0, 1, 0, 1],
        }
    )


class TestGenerateEdaHtmlReport:
    def test_creates_html_file(self, sample_df, tmp_path):
        output_path = tmp_path / "report.html"
        result_path = generate_eda_html_report(sample_df, str(output_path))

        assert result_path.exists()
        assert result_path == output_path

    def test_report_contains_key_sections(self, sample_df, tmp_path):
        output_path = tmp_path / "report.html"
        generate_eda_html_report(sample_df, str(output_path))
        html = output_path.read_text(encoding="utf-8")

        assert "Descriptive Statistics" in html
        assert "Correlation Heatmap" in html
        assert "Distributions" in html
        assert "plotly" in html.lower()

    def test_report_includes_category_breakdown_when_requested(self, sample_df, tmp_path):
        output_path = tmp_path / "report.html"
        generate_eda_html_report(
            sample_df,
            str(output_path),
            category_column="loan_grade",
            target_column="loan_status",
        )
        html = output_path.read_text(encoding="utf-8")

        assert "Breakdown by loan_grade" in html

    def test_creates_parent_directories(self, sample_df, tmp_path):
        output_path = tmp_path / "nested" / "dir" / "report.html"
        result_path = generate_eda_html_report(sample_df, str(output_path))

        assert result_path.exists()

    def test_report_still_succeeds_when_figures_dir_given(self, sample_df, tmp_path):
        """The HTML report must always succeed, whether or not the optional
        static PNG export works -- static export depends on Chrome/kaleido
        being available in the runtime environment, which isn't guaranteed."""
        output_path = tmp_path / "report.html"
        figures_dir = tmp_path / "figures"

        result_path = generate_eda_html_report(
            sample_df,
            str(output_path),
            category_column="loan_grade",
            target_column="loan_status",
            figures_dir=str(figures_dir),
        )

        assert result_path.exists()

    def test_report_still_generated_when_figures_dir_omitted(self, sample_df, tmp_path):
        output_path = tmp_path / "report.html"
        result_path = generate_eda_html_report(sample_df, str(output_path))

        assert result_path.exists()

    def test_skips_heatmap_gracefully_with_one_numeric_column(self, tmp_path):
        df = pd.DataFrame({"age": [25, 30, 35], "city": ["Cairo", "Giza", "Alex"]})
        output_path = tmp_path / "report.html"
        result_path = generate_eda_html_report(df, str(output_path))
        html = output_path.read_text(encoding="utf-8")

        assert result_path.exists()
        assert "Skipped" in html

    def test_raises_key_error_on_none_dataframe(self, tmp_path):
        with pytest.raises(KeyError):
            generate_eda_html_report(None, str(tmp_path / "report.html"))

    def test_raises_value_error_on_empty_dataframe(self, tmp_path):
        with pytest.raises(ValueError):
            generate_eda_html_report(pd.DataFrame(), str(tmp_path / "report.html"))
