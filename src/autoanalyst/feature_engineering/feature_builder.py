"""Feature engineering helpers for AutoAnalyst AI."""

import pandas as pd


def add_datetime_features(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """Create year, month, and day-of-week features from a date column."""
    if date_column not in df.columns:
        raise KeyError(f"Column not found: {date_column}")

    enhanced = df.copy()
    dates = pd.to_datetime(enhanced[date_column], errors="coerce")
    enhanced[f"{date_column}_year"] = dates.dt.year
    enhanced[f"{date_column}_month"] = dates.dt.month
    enhanced[f"{date_column}_dayofweek"] = dates.dt.dayofweek
    return enhanced


def encode_categorical_columns(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """One-hot encode selected categorical columns."""
    selected = columns or list(df.select_dtypes(include=["object", "category"]).columns)
    missing = [column for column in selected if column not in df.columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}")
    return pd.get_dummies(df, columns=selected, drop_first=True)
