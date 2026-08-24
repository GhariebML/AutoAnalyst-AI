"""Unit tests for the hardened data profiling and quality assessment module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from autoanalyst.data_profiling.profiler import (
    DataProfile,
    generate_basic_profile,
    get_duplicate_count,
    get_missing_values_report,
    profile_dataframe,
)


@pytest.fixture
def clean_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [25, 30, 35, 40, 45, 50],
            "salary": [50000.0, 60000.0, 75000.0, 80000.0, 95000.0, 110000.0],
            "department": ["Sales", "Engineering", "Marketing", "Engineering", "HR", "Sales"],
        }
    )


@pytest.fixture
def dirty_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "a": [1, 2, None, 4, 1],  # 1 duplicate row, 1 missing
            "b": [10.0, 20.0, np.nan, 40.0, 10.0],
            "c": ["x", "x", "x", "x", "x"],  # Constant column
        }
    )


class TestDataProfiling:
    def test_profile_clean_dataframe(self, clean_df: pd.DataFrame) -> None:
        profile = profile_dataframe(clean_df)
        assert isinstance(profile, DataProfile)
        assert profile.rows == 6
        assert profile.columns == 3
        assert profile.missing_values_total == 0
        assert profile.duplicate_rows == 0
        assert len(profile.constant_columns) == 0
        assert profile.quality_report.health_score >= 95.0
        assert profile.quality_report.grade == "A"

    def test_profile_dirty_dataframe(self, dirty_df: pd.DataFrame) -> None:
        profile = profile_dataframe(dirty_df)
        assert profile.rows == 5
        assert profile.missing_values_total == 2
        assert profile.duplicate_rows == 1
        assert "c" in profile.constant_columns
        assert profile.quality_report.health_score < 90.0
        assert len(profile.quality_report.flags) > 0

    def test_empty_dataframe_raises(self) -> None:
        with pytest.raises(ValueError, match="empty DataFrame"):
            profile_dataframe(pd.DataFrame())

    def test_generate_basic_profile_compatibility(self, clean_df: pd.DataFrame) -> None:
        dict_profile = generate_basic_profile(clean_df)
        assert isinstance(dict_profile, dict)
        assert dict_profile["rows"] == 6
        assert dict_profile["health_score"] >= 95.0
        assert "quality_grade" in dict_profile

    def test_missing_values_report(self, dirty_df: pd.DataFrame) -> None:
        rep = get_missing_values_report(dirty_df)
        assert isinstance(rep, pd.DataFrame)
        assert list(rep.columns) == ["column", "missing_count", "missing_percent"]
        assert rep.iloc[0]["missing_count"] == 1

    def test_get_duplicate_count(self, dirty_df: pd.DataFrame) -> None:
        count = get_duplicate_count(dirty_df)
        assert count == 1
