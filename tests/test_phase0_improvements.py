"""Tests for Phase 0 stabilization improvements.

Covers:
- High-cardinality detection in feature_builder
- Skewness-aware imputation in cleaner
- Structured logging (smoke test)
- Pandas deprecation fix in pipeline
"""

import logging

import numpy as np
import pandas as pd
import pytest

from autoanalyst.feature_engineering.feature_builder import (
    DEFAULT_HIGH_CARDINALITY_THRESHOLD,
    detect_high_cardinality_columns,
    encode_categorical_columns,
)
from autoanalyst.pipeline import PipelineConfig, run_analysis_pipeline
from autoanalyst.preprocessing.cleaner import handle_missing_values, remove_duplicates


# ======================================================================
# High-Cardinality Detection Tests
# ======================================================================


class TestHighCardinalityDetection:
    """Tests for detect_high_cardinality_columns."""

    def test_normal_categorical_column(self) -> None:
        """A column with few unique values should be flagged as normal."""
        df = pd.DataFrame({"city": ["Cairo", "Giza", "Alexandria", "Cairo", "Giza"]})
        results = detect_high_cardinality_columns(df, columns=["city"])
        assert len(results) == 1
        assert results[0]["column"] == "city"
        assert results[0]["unique_count"] == 3
        assert results[0]["status"] == "normal"

    def test_high_cardinality_column(self) -> None:
        """A column with many unique values should be flagged as high_cardinality."""
        values = [f"cat_{i}" for i in range(100)]
        df = pd.DataFrame({"category": values})
        results = detect_high_cardinality_columns(df, columns=["category"])
        assert len(results) == 1
        assert results[0]["column"] == "category"
        assert results[0]["unique_count"] == 100
        assert results[0]["status"] == "high_cardinality"

    def test_configurable_threshold(self) -> None:
        """A column should be normal with a high threshold, high_cardinality with a low one."""
        # 30 unique values in 100 rows = 0.3 ratio (below 0.9 default)
        values = [f"cat_{i % 30}" for i in range(100)]
        df = pd.DataFrame({"category": values})

        # With high absolute threshold (50), 30 unique values is normal
        results_high = detect_high_cardinality_columns(df, threshold=50, ratio=1.0)
        assert results_high[0]["status"] == "normal"

        # With low absolute threshold (10), 30 unique values is high_cardinality
        results_low = detect_high_cardinality_columns(df, threshold=10, ratio=1.0)
        assert results_low[0]["status"] == "high_cardinality"

    def test_ratio_threshold(self) -> None:
        """A column where nearly every row is unique should be flagged by ratio."""
        values = [f"item_{i}" for i in range(50)]
        df = pd.DataFrame({"id": values})
        # With ratio=0.5, 50/50 = 1.0 > 0.5 → high_cardinality
        results = detect_high_cardinality_columns(df, ratio=0.5)
        assert results[0]["status"] == "high_cardinality"

    def test_auto_detect_categorical(self) -> None:
        """When columns=None, should auto-detect categorical columns."""
        df = pd.DataFrame({
            "num": [1, 2, 3, 4, 5],
            "cat": ["a", "b", "c", "a", "b"],
        })
        results = detect_high_cardinality_columns(df)
        column_names = [r["column"] for r in results]
        assert "cat" in column_names
        assert "num" not in column_names

    def test_empty_dataframe(self) -> None:
        """Should handle empty DataFrame gracefully."""
        df = pd.DataFrame({"cat": pd.Series([], dtype="object")})
        results = detect_high_cardinality_columns(df, columns=["cat"])
        assert len(results) == 1
        assert results[0]["unique_count"] == 0
        assert results[0]["cardinality_ratio"] == 0.0

    def test_missing_column_skipped(self) -> None:
        """Non-existent columns should be skipped silently."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        results = detect_high_cardinality_columns(df, columns=["nonexistent"])
        assert len(results) == 0

    def test_encode_logs_high_cardinality(self, caplog) -> None:
        """encode_categorical_columns should log warnings for high-cardinality columns."""
        values = [f"cat_{i}" for i in range(100)]
        df = pd.DataFrame({"category": values, "value": range(100)})
        with caplog.at_level(logging.WARNING):
            encode_categorical_columns(df, columns=["category"])
        assert any("High-cardinality" in record.message for record in caplog.records)


# ======================================================================
# Skewness-Aware Imputation Tests
# ======================================================================


class TestSkewnessAwareImputation:
    """Tests for handle_missing_values with skewness awareness."""

    def test_normal_distribution_uses_mean(self) -> None:
        """For a roughly symmetric distribution, mean should be used when requested."""
        # Symmetric data: [10, 20, 30, 40, 50] — skewness ≈ 0
        df = pd.DataFrame({"val": [10, 20, None, 40, 50]})
        result = handle_missing_values(df, strategy="mean")
        assert result["val"].isna().sum() == 0
        # Mean of [10, 20, 40, 50] = 30.0
        assert result["val"][2] == pytest.approx(30.0)

    def test_skewed_distribution_uses_median(self) -> None:
        """For a heavily skewed distribution, median should be used even if mean requested."""
        # Highly right-skewed: most values small, one huge outlier
        df = pd.DataFrame({"val": [1, 2, 2, 2, 3, None, 1000]})
        result = handle_missing_values(df, strategy="mean")
        assert result["val"].isna().sum() == 0
        # Median of [1, 2, 2, 2, 3, 1000] = 2.0
        # Mean would be ~145 — but skewness should force median
        assert result["val"][5] == pytest.approx(2.0)

    def test_median_strategy_with_skew(self) -> None:
        """Median strategy should always use median regardless of skewness."""
        df = pd.DataFrame({"val": [1, 2, 2, 2, 3, None, 1000]})
        result = handle_missing_values(df, strategy="median")
        assert result["val"].isna().sum() == 0
        assert result["val"][5] == pytest.approx(2.0)

    def test_all_null_numeric_column(self) -> None:
        """An all-null column (detected as object dtype) should be filled with 'Unknown'."""
        # An all-null column has object dtype, so it's treated as categorical
        df = pd.DataFrame({"all_null": [None, None, None], "ok": [1, 2, 3]})
        result = handle_missing_values(df, strategy="mean")
        assert result["all_null"].isna().sum() == 0
        assert (result["all_null"] == "Unknown").all()

    def test_empty_dataframe(self) -> None:
        """Empty DataFrame should be returned unchanged."""
        df = pd.DataFrame({"a": pd.Series([], dtype="float64")})
        result = handle_missing_values(df, strategy="median")
        assert len(result) == 0

    def test_categorical_mode_preserved(self) -> None:
        """Categorical columns should still use mode imputation."""
        df = pd.DataFrame({"cat": ["a", "a", "b", None, "a"]})
        result = handle_missing_values(df, strategy="median")
        assert result["cat"].isna().sum() == 0
        assert result["cat"][3] == "a"  # mode

    def test_no_missing_values(self) -> None:
        """DataFrame with no missing values should be returned unchanged."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        result = handle_missing_values(df, strategy="median")
        assert len(result) == 3
        assert result.isna().sum().sum() == 0

    def test_drop_strategy(self) -> None:
        """Drop strategy should remove rows with any missing value."""
        df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", None]})
        result = handle_missing_values(df, strategy="drop")
        assert len(result) == 1
        assert result["a"][0] == 1

    def test_invalid_strategy_raises(self) -> None:
        """Invalid strategy should raise ValueError."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        with pytest.raises(ValueError, match="strategy must be one of"):
            handle_missing_values(df, strategy="invalid")

    def test_deterministic_output(self) -> None:
        """Running imputation twice should produce identical results."""
        df = pd.DataFrame({"val": [1, 2, None, 4, 5, None, 100]})
        result1 = handle_missing_values(df, strategy="mean")
        result2 = handle_missing_values(df, strategy="mean")
        pd.testing.assert_frame_equal(result1, result2)


# ======================================================================
# Logging Smoke Tests
# ======================================================================


class TestLoggingSmoke:
    """Verify that logging does not crash during preprocessing."""

    def test_handle_missing_values_logs(self, caplog) -> None:
        """handle_missing_values should emit log messages without errors."""
        df = pd.DataFrame({"a": [1, None, 3], "b": ["x", None, "z"]})
        with caplog.at_level(logging.INFO):
            handle_missing_values(df, strategy="median")
        assert any("Handling missing values" in record.message for record in caplog.records)
        assert any("complete" in record.message.lower() for record in caplog.records)

    def test_remove_duplicates_logs(self, caplog) -> None:
        """remove_duplicates should emit log messages without errors."""
        df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
        with caplog.at_level(logging.INFO):
            remove_duplicates(df)
        assert any("duplicate" in record.message.lower() for record in caplog.records)

    def test_pipeline_logs(self, caplog) -> None:
        """The full pipeline should emit structured log messages."""
        df = pd.DataFrame({
            "age": [25, 32, 32, None],
            "income": [50000, 65000, 65000, 80000],
            "city": ["Cairo", "Giza", "Giza", None],
        })
        with caplog.at_level(logging.INFO):
            run_analysis_pipeline(df)
        log_messages = [r.message for r in caplog.records]
        assert any("Starting AutoAnalyst AI pipeline" in msg for msg in log_messages)
        assert any("Dataset loaded" in msg for msg in log_messages)
        assert any("Pipeline complete" in msg for msg in log_messages)


# ======================================================================
# Pandas Deprecation Fix Tests
# ======================================================================


class TestPandasDeprecationFix:
    """Verify that the select_dtypes deprecation warning is resolved."""

    def test_pipeline_no_select_dtypes_warning(self) -> None:
        """Pipeline should not emit Pandas4Warning about select_dtypes."""
        df = pd.DataFrame({
            "age": [25, 32, 41, 29, 36, 45],
            "income": [50000, 65000, 80000, 52000, 70000, 90000],
            "city": ["Cairo", "Giza", "Alexandria", "Cairo", "Giza", "Alexandria"],
            "purchased": ["yes", "no", "yes", "no", "yes", "no"],
        })
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            run_analysis_pipeline(df, PipelineConfig(target_column="purchased", model_task="classification"))
        pandas_warnings = [x for x in w if "select_dtypes" in str(x.message)]
        assert len(pandas_warnings) == 0, f"Got unexpected pandas warnings: {pandas_warnings}"

    def test_encode_categorical_with_string_dtype(self) -> None:
        """encode_categorical_columns should handle string dtype columns without warnings."""
        df = pd.DataFrame({
            "num": [1, 2, 3, 4],
            "cat": pd.array(["a", "b", "a", "b"], dtype="string"),
        })
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = encode_categorical_columns(df, columns=["cat"])
        pandas_warnings = [x for x in w if "select_dtypes" in str(x.message)]
        assert len(pandas_warnings) == 0
        assert "cat_b" in result.columns or "cat_a" in result.columns
