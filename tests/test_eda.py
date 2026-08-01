"""Unit tests for autoanalyst/eda/analyzer.py"""

import numpy as np
import pandas as pd
import pytest

from autoanalyst.eda.analyzer import get_correlation_matrix, get_numeric_summary


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "age": [25, 30, 35, 40, 45],
            "income": [50000, 60000, 75000, 80000, 95000],
            "city": ["Cairo", "Giza", "Cairo", "Alex", "Giza"],
        }
    )


class TestGetNumericSummary:
    def test_returns_expected_index_and_columns(self, sample_df):
        summary = get_numeric_summary(sample_df)
        assert list(summary.index) == ["age", "income"]
        for stat in ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]:
            assert stat in summary.columns

    def test_ignores_non_numeric_columns(self, sample_df):
        summary = get_numeric_summary(sample_df)
        assert "city" not in summary.index

    def test_raises_key_error_on_none_input(self):
        with pytest.raises(KeyError):
            get_numeric_summary(None)

    def test_raises_value_error_on_empty_dataframe(self):
        with pytest.raises(ValueError):
            get_numeric_summary(pd.DataFrame())

    def test_raises_value_error_when_no_numeric_columns(self):
        df = pd.DataFrame({"city": ["Cairo", "Giza"]})
        with pytest.raises(ValueError):
            get_numeric_summary(df)

    def test_isolates_unexpected_pandas_error_as_value_error(self, sample_df, monkeypatch):
        def _broken_describe(self, *args, **kwargs):
            raise RuntimeError("simulated unexpected pandas failure")

        monkeypatch.setattr(pd.DataFrame, "describe", _broken_describe)
        with pytest.raises(ValueError):
            get_numeric_summary(sample_df)


class TestGetCorrelationMatrix:
    def test_returns_square_matrix_with_expected_labels(self, sample_df):
        corr = get_correlation_matrix(sample_df)
        assert corr.shape == (2, 2)
        assert list(corr.columns) == ["age", "income"]
        assert list(corr.index) == ["age", "income"]

    def test_diagonal_values_equal_one(self, sample_df):
        corr = get_correlation_matrix(sample_df)
        assert np.allclose(np.diag(corr.values), 1.0)

    def test_default_method_is_pearson(self, sample_df):
        default_corr = get_correlation_matrix(sample_df)
        explicit_corr = get_correlation_matrix(sample_df, method="pearson")
        assert np.allclose(default_corr.values, explicit_corr.values)

    def test_supports_spearman_method(self, sample_df):
        corr = get_correlation_matrix(sample_df, method="spearman")
        assert corr.shape == (2, 2)

    def test_supports_kendall_method(self, sample_df):
        corr = get_correlation_matrix(sample_df, method="kendall")
        assert corr.shape == (2, 2)

    def test_raises_value_error_on_invalid_method(self, sample_df):
        with pytest.raises(ValueError):
            get_correlation_matrix(sample_df, method="not_a_real_method")

    def test_raises_key_error_on_none_input(self):
        with pytest.raises(KeyError):
            get_correlation_matrix(None)

    def test_raises_value_error_on_empty_dataframe(self):
        with pytest.raises(ValueError):
            get_correlation_matrix(pd.DataFrame())

    def test_raises_value_error_when_fewer_than_two_numeric_columns(self):
        df = pd.DataFrame({"age": [25, 30, 35], "city": ["Cairo", "Giza", "Alex"]})
        with pytest.raises(ValueError):
            get_correlation_matrix(df)

    def test_isolates_unexpected_pandas_error_as_value_error(self, sample_df, monkeypatch):
        def _broken_corr(self, *args, **kwargs):
            raise RuntimeError("simulated unexpected pandas failure")

        monkeypatch.setattr(pd.DataFrame, "corr", _broken_corr)
        with pytest.raises(ValueError):
            get_correlation_matrix(sample_df)
