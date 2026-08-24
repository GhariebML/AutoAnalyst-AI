"""Unit tests for the exploratory data analysis and statistical diagnostics module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from autoanalyst.eda.analyzer import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    get_categorical_frequencies,
    get_correlation_matrix,
    get_distribution_overview,
    get_numeric_summary,
    get_outliers_summary,
)


@pytest.fixture
def numeric_df() -> pd.DataFrame:
    np.random.seed(42)
    # Generate 100 samples from standard normal, plus one extreme outlier in x
    x = np.random.normal(loc=0, scale=1, size=100)
    x[0] = 50.0  # Extreme outlier
    y = 2 * x + np.random.normal(loc=0, scale=0.5, size=100)
    z = np.random.exponential(scale=2, size=100)  # Skewed
    return pd.DataFrame({"x": x, "y": y, "z": z, "category": ["A", "B"] * 50})


class TestExploratoryAnalysis:
    def test_numeric_summary(self, numeric_df: pd.DataFrame) -> None:
        summary = get_numeric_summary(numeric_df)
        assert isinstance(summary, pd.DataFrame)
        assert set(summary.index) == {"x", "y", "z"}
        assert "mean" in summary.columns

    def test_correlation_methods(self, numeric_df: pd.DataFrame) -> None:
        p_corr = get_correlation_matrix(numeric_df, method="pearson")
        s_corr = get_correlation_matrix(numeric_df, method="spearman")
        k_corr = get_correlation_matrix(numeric_df, method="kendall")

        assert p_corr.shape == (3, 3)
        assert s_corr.shape == (3, 3)
        assert k_corr.shape == (3, 3)

        with pytest.raises(ValueError, match="not supported"):
            get_correlation_matrix(numeric_df, method="invalid_method")

    def test_distribution_overview(self, numeric_df: pd.DataFrame) -> None:
        dist = get_distribution_overview(numeric_df)
        assert isinstance(dist, pd.DataFrame)
        assert "skewness" in dist.columns
        assert "kurtosis" in dist.columns
        assert "distribution_type" in dist.columns
        assert len(dist) == 3

    def test_outlier_detection_iqr(self, numeric_df: pd.DataFrame) -> None:
        outliers = detect_outliers_iqr(numeric_df, "x")
        assert outliers["method"] == "IQR"
        assert outliers["count"] >= 1
        assert outliers["upper_bound"] < 50.0

    def test_outlier_detection_zscore(self, numeric_df: pd.DataFrame) -> None:
        outliers = detect_outliers_zscore(numeric_df, "x", threshold=3.0)
        assert outliers["method"] == "Z-Score"
        assert outliers["count"] >= 1

    def test_outliers_summary(self, numeric_df: pd.DataFrame) -> None:
        summary = get_outliers_summary(numeric_df, method="iqr")
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == 3

    def test_categorical_frequencies(self, numeric_df: pd.DataFrame) -> None:
        freq = get_categorical_frequencies(numeric_df, "category")
        assert len(freq) == 2
        assert set(freq["value"]) == {"A", "B"}
        assert freq["percent"].sum() == pytest.approx(100.0)
