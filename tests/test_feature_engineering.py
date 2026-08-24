"""Unit tests for the feature engineering and transformation module."""

from __future__ import annotations

import pandas as pd
import pytest

from autoanalyst.feature_engineering.feature_builder import (
    create_interaction_features,
    create_polynomial_features,
    encode_categorical_columns,
    encode_frequency,
    encode_target,
    extract_datetime_features,
    scale_features,
    select_features,
)


@pytest.fixture
def feature_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [20, 30, 40, 50, 60],
            "income": [20000.0, 40000.0, 60000.0, 80000.0, 100000.0],
            "city": ["Cairo", "Alex", "Cairo", "Giza", "Alex"],
            "date": ["2026-01-01", "2026-02-15", "2026-06-30", "2026-09-10", "2026-12-25"],
            "target": [0, 1, 0, 1, 1],
        }
    )


class TestFeatureEngineering:
    def test_one_hot_encoding(self, feature_df: pd.DataFrame) -> None:
        encoded = encode_categorical_columns(feature_df, columns=["city"])
        assert "city_Cairo" in encoded.columns
        assert "city_Alex" in encoded.columns

    def test_frequency_encoding(self, feature_df: pd.DataFrame) -> None:
        freq = encode_frequency(feature_df, columns=["city"])
        assert "city_freq" in freq.columns
        assert freq["city_freq"].iloc[0] == pytest.approx(0.4)  # Cairo appears 2/5 = 0.4

    def test_target_encoding(self, feature_df: pd.DataFrame) -> None:
        t_enc = encode_target(feature_df, target_column="target", columns=["city"])
        assert "city_target_enc" in t_enc.columns
        assert not t_enc["city_target_enc"].isna().any()

    def test_datetime_features(self, feature_df: pd.DataFrame) -> None:
        dt_df = extract_datetime_features(feature_df, columns=["date"])
        assert "date_year" in dt_df.columns
        assert "date_month" in dt_df.columns
        assert "date_is_weekend" in dt_df.columns
        assert dt_df["date_year"].iloc[0] == 2026

    def test_feature_scaling(self, feature_df: pd.DataFrame) -> None:
        scaled_std = scale_features(feature_df, columns=["age", "income"], method="standard")
        assert scaled_std["age"].mean() == pytest.approx(0.0, abs=1e-6)

        scaled_minmax = scale_features(feature_df, columns=["age", "income"], method="minmax")
        assert scaled_minmax["age"].min() == 0.0
        assert scaled_minmax["age"].max() == 1.0

    def test_feature_selection(self, feature_df: pd.DataFrame) -> None:
        selected_df, cols = select_features(feature_df, target_column="target", task="classification", k=2)
        assert "target" in selected_df.columns
        assert len(cols) <= 2

    def test_interactions_and_polynomials(self, feature_df: pd.DataFrame) -> None:
        inter = create_interaction_features(feature_df, numeric_columns=["age", "income"])
        assert "age_x_income" in inter.columns
        assert "age_div_income" in inter.columns

        poly = create_polynomial_features(feature_df, columns=["age", "income"], degree=2)
        assert "age^2" in poly.columns or "age 1" in poly.columns or len(poly.columns) > len(feature_df.columns)
