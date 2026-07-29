"""Unit tests for autoanalyst/eda/visualizer.py"""

import pandas as pd
import pytest

from autoanalyst.eda.visualizer import (
    plot_category_breakdown,
    plot_correlation_heatmap,
    plot_distribution,
    plot_histogram,
    plot_scatter,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "age": [25, 30, 35, 40, 45, 50],
            "income": [50000, 60000, 75000, 80000, 95000, 40000],
            "loan_grade": ["A", "B", "A", "C", "B", "A"],
            "loan_status": [0, 1, 0, 1, 0, 1],
            "city": ["Cairo", "Giza", "Cairo", "Alex", "Giza", "Cairo"],
        }
    )


def _assert_valid_plotly_metadata(fig_dict):
    assert isinstance(fig_dict, dict)
    assert "data" in fig_dict
    assert "layout" in fig_dict


class TestPlotHistogram:
    def test_returns_valid_plotly_metadata(self, sample_df):
        result = plot_histogram(sample_df, "age")
        _assert_valid_plotly_metadata(result)

    def test_raises_key_error_on_none_dataframe(self):
        with pytest.raises(KeyError):
            plot_histogram(None, "age")

    def test_raises_key_error_on_missing_column(self, sample_df):
        with pytest.raises(KeyError):
            plot_histogram(sample_df, "not_a_column")

    def test_raises_value_error_on_non_numeric_column(self, sample_df):
        with pytest.raises(ValueError):
            plot_histogram(sample_df, "city")

    def test_raises_value_error_on_empty_dataframe(self):
        with pytest.raises(ValueError):
            plot_histogram(pd.DataFrame({"age": []}), "age")


class TestPlotDistribution:
    def test_returns_valid_plotly_metadata(self, sample_df):
        result = plot_distribution(sample_df, "income")
        _assert_valid_plotly_metadata(result)

    def test_raises_value_error_on_non_numeric_column(self, sample_df):
        with pytest.raises(ValueError):
            plot_distribution(sample_df, "loan_grade")


class TestPlotCorrelationHeatmap:
    def test_returns_valid_plotly_metadata(self, sample_df):
        result = plot_correlation_heatmap(sample_df)
        _assert_valid_plotly_metadata(result)

    def test_supports_spearman_method(self, sample_df):
        result = plot_correlation_heatmap(sample_df, method="spearman")
        _assert_valid_plotly_metadata(result)

    def test_raises_value_error_when_fewer_than_two_numeric_columns(self):
        df = pd.DataFrame({"age": [25, 30, 35], "city": ["Cairo", "Giza", "Alex"]})
        with pytest.raises(ValueError):
            plot_correlation_heatmap(df)

    def test_raises_key_error_on_none_dataframe(self):
        with pytest.raises(KeyError):
            plot_correlation_heatmap(None)


class TestPlotScatter:
    def test_returns_valid_plotly_metadata(self, sample_df):
        result = plot_scatter(sample_df, "age", "income")
        _assert_valid_plotly_metadata(result)

    def test_supports_color_column(self, sample_df):
        result = plot_scatter(sample_df, "age", "income", color_column="loan_grade")
        _assert_valid_plotly_metadata(result)

    def test_raises_key_error_on_missing_color_column(self, sample_df):
        with pytest.raises(KeyError):
            plot_scatter(sample_df, "age", "income", color_column="not_a_column")

    def test_raises_value_error_on_non_numeric_axis(self, sample_df):
        with pytest.raises(ValueError):
            plot_scatter(sample_df, "age", "city")


class TestPlotCategoryBreakdown:
    def test_returns_counts_when_no_target_given(self, sample_df):
        result = plot_category_breakdown(sample_df, "loan_grade")
        _assert_valid_plotly_metadata(result)

    def test_returns_rate_when_target_given(self, sample_df):
        result = plot_category_breakdown(sample_df, "loan_grade", target_column="loan_status")
        _assert_valid_plotly_metadata(result)

    def test_raises_key_error_on_missing_category_column(self, sample_df):
        with pytest.raises(KeyError):
            plot_category_breakdown(sample_df, "not_a_column")

    def test_raises_key_error_on_missing_target_column(self, sample_df):
        with pytest.raises(KeyError):
            plot_category_breakdown(sample_df, "loan_grade", target_column="not_a_column")

    def test_raises_value_error_on_non_numeric_target(self, sample_df):
        with pytest.raises(ValueError):
            plot_category_breakdown(sample_df, "loan_grade", target_column="city")

    def test_raises_key_error_on_none_dataframe(self):
        with pytest.raises(KeyError):
            plot_category_breakdown(None, "loan_grade")
