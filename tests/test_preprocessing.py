"""Unit tests for the preprocessing and cleaning engine."""

from __future__ import annotations

import pandas as pd
import pytest

from autoanalyst.preprocessing.cleaner import (
    CleaningResult,
    clean_dataset,
    handle_missing_values,
    remove_duplicates,
    winsorize_outliers,
)


@pytest.fixture
def dirty_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 5],  # 1 duplicate row
            "age": [25.0, 30.0, None, 45.0, 150.0, 150.0],  # 1 missing, 1 extreme outlier
            "income": [50000.0, None, 70000.0, 80000.0, 500000.0, 500000.0],
            "category": ["A", "B", None, "A", "B", "B"],
        }
    )


class TestDataCleaningEngine:
    def test_remove_duplicates(self, dirty_dataset: pd.DataFrame) -> None:
        cleaned = remove_duplicates(dirty_dataset)
        assert len(cleaned) == 5

    def test_imputation_strategies(self, dirty_dataset: pd.DataFrame) -> None:
        # Median
        med_df = handle_missing_values(dirty_dataset, strategy="median")
        assert med_df.isna().sum().sum() == 0

        # Mode
        mode_df = handle_missing_values(dirty_dataset, strategy="mode")
        assert mode_df.isna().sum().sum() == 0

        # KNN
        knn_df = handle_missing_values(dirty_dataset, strategy="knn", n_neighbors=2)
        assert knn_df.isna().sum().sum() == 0

        # Forward fill
        ffill_df = handle_missing_values(dirty_dataset, strategy="forward_fill")
        assert ffill_df.isna().sum().sum() == 0

        # Drop
        drop_df = handle_missing_values(dirty_dataset, strategy="drop")
        assert len(drop_df) < len(dirty_dataset)

    def test_winsorize_outliers(self) -> None:
        df = pd.DataFrame({"age": [20.0, 25.0, 30.0, 35.0, 40.0, 200.0]})
        cleaned, logs = winsorize_outliers(df, columns=["age"], lower_percentile=0.05, upper_percentile=0.90)
        assert cleaned["age"].max() < 200.0

    def test_clean_dataset_end_to_end(self, dirty_dataset: pd.DataFrame) -> None:
        result = clean_dataset(
            dirty_dataset,
            missing_strategy="median",
            handle_outliers="winsorize",
            drop_duplicate_rows=True,
        )
        assert isinstance(result, CleaningResult)
        assert len(result.cleaned_df) == 5
        assert result.cleaned_df.isna().sum().sum() == 0
        assert result.total_duplicates_removed == 1
        assert len(result.log) > 0
        assert len(result.log_messages) > 0
