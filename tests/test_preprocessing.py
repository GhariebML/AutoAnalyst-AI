"""Unit tests for the preprocessing module."""

import pytest
import numpy as np
import pandas as pd
from ml_engine.preprocessing import clean_data, encode_features, scale_features, split_data


def test_clean_data_duplicates() -> None:
    df = pd.DataFrame({
        "a": [1, 2, 2, 4],
        "b": [5, 6, 6, 8]
    })
    cleaned = clean_data(df, drop_duplicates=True)
    assert len(cleaned) == 3
    assert list(cleaned["a"]) == [1, 2, 4]


def test_clean_data_missing_median() -> None:
    df = pd.DataFrame({
        "a": [1.0, 2.0, np.nan, 4.0],
        "b": ["x", "y", "y", np.nan]
    })
    # Median of [1, 2, 4] is 2.0. Mode of ["x", "y", "y"] is "y".
    cleaned = clean_data(df, fill_strategy="median")
    assert cleaned["a"].isna().sum() == 0
    assert cleaned["b"].isna().sum() == 0
    assert cleaned.loc[2, "a"] == 2.0
    assert cleaned.loc[3, "b"] == "y"


def test_clean_data_missing_dict() -> None:
    df = pd.DataFrame({
        "a": [1.0, np.nan, 3.0],
        "b": ["x", np.nan, "z"]
    })
    # Impute a with mean, b with drop
    cleaned = clean_data(df, fill_strategy={"a": "mean", "b": "drop"})
    assert len(cleaned) == 2
    assert cleaned["a"].isna().sum() == 0
    assert cleaned["b"].isna().sum() == 0


def test_clean_data_outliers_iqr() -> None:
    # 10 is an outlier if we have [1, 1.1, 1.2, 1.3, 10]
    df = pd.DataFrame({
        "a": [1.0, 1.1, 1.2, 1.3, 10.0]
    })
    cleaned = clean_data(df, outlier_method="iqr")
    assert cleaned.loc[4, "a"] < 10.0
    assert cleaned.loc[4, "a"] > 1.3


def test_clean_data_outliers_z_score() -> None:
    # 100.0 is an outlier when compared to fifteen 1.0 values
    df = pd.DataFrame({
        "a": [1.0] * 15 + [100.0]
    })
    cleaned = clean_data(df, drop_duplicates=False, outlier_method="z_score")
    assert cleaned.loc[15, "a"] < 100.0


def test_clean_data_invalid_args() -> None:
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(ValueError):
        clean_data(df, fill_strategy="invalid_strat")
    with pytest.raises(ValueError):
        clean_data(df, outlier_method="invalid_method")  # type: ignore
    with pytest.raises(KeyError):
        clean_data(df, fill_strategy={"nonexistent_col": "mean"})


def test_encode_features_onehot() -> None:
    df = pd.DataFrame({
        "cat": ["A", "B", "A"],
        "num": [10, 20, 30]
    })
    encoded = encode_features(df, method="onehot")
    assert "cat_A" in encoded.columns
    assert "cat_B" in encoded.columns
    assert "num" in encoded.columns
    assert encoded["cat_A"].iloc[0] == 1
    assert encoded["cat_B"].iloc[0] == 0


def test_encode_features_label() -> None:
    df = pd.DataFrame({
        "cat": ["A", "B", "A"],
        "num": [10, 20, 30]
    })
    encoded = encode_features(df, method="label")
    assert "cat" in encoded.columns
    assert encoded["cat"].iloc[0] == 0
    assert encoded["cat"].iloc[1] == 1


def test_encode_features_invalid() -> None:
    df = pd.DataFrame({"cat": ["A", "B"]})
    with pytest.raises(ValueError):
        encode_features(df, method="invalid_method")  # type: ignore
    with pytest.raises(KeyError):
        encode_features(df, categorical_cols=["nonexistent"])


def test_scale_features() -> None:
    df = pd.DataFrame({
        "a": [1.0, 2.0, 3.0],
        "b": [10.0, 20.0, 30.0]
    })
    scaled_std = scale_features(df, method="standard")
    assert np.allclose(scaled_std["a"].mean(), 0.0)
    
    scaled_minmax = scale_features(df, method="minmax")
    assert scaled_minmax["a"].min() == 0.0
    assert scaled_minmax["a"].max() == 1.0


def test_split_data() -> None:
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [10, 20, 30, 40, 50],
        "target": [0, 1, 0, 1, 0]
    })
    X_train, X_test, y_train, y_test = split_data(df, target_col="target", test_size=0.4, random_state=42)
    assert len(X_train) == 3
    assert len(X_test) == 2
    assert len(y_train) == 3
    assert len(y_test) == 2
    assert "target" not in X_train.columns
