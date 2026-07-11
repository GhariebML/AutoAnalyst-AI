"""Data cleaning functions for preprocessing datasets."""

import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with duplicate rows removed."""
    return df.drop_duplicates().reset_index(drop=True)


def handle_missing_values(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Handle missing values using a simple strategy.

    Supported strategies: median, mean, mode, drop.
    """
    strategy = strategy.lower()
    cleaned = df.copy()

    if strategy == "drop":
        return cleaned.dropna().reset_index(drop=True)

    if strategy not in {"median", "mean", "mode"}:
        raise ValueError("strategy must be one of: median, mean, mode, drop")

    for column in cleaned.columns:
        if not cleaned[column].isna().any():
            continue
        if strategy in {"median", "mean"} and pd.api.types.is_numeric_dtype(cleaned[column]):
            fill_value = cleaned[column].median() if strategy == "median" else cleaned[column].mean()
        else:
            modes = cleaned[column].mode(dropna=True)
            fill_value = modes.iloc[0] if not modes.empty else "Unknown"
        cleaned[column] = cleaned[column].fillna(fill_value)

    return cleaned
