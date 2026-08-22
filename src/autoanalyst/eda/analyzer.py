"""Exploratory data analysis utilities."""

from typing import Any

import pandas as pd


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        raise ValueError("No numeric columns found for summary.")
    return numeric_df.describe().T


def get_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Return a correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        raise ValueError("At least two numeric columns are required for correlation.")
    return numeric_df.corr(method=method)


def get_distribution_overview(df: pd.DataFrame) -> pd.DataFrame:
    """Return shape-of-distribution statistics for every numeric column.

    Extends ``describe`` with skewness and kurtosis so downstream agents can
    reason about symmetry and tail heaviness.
    """
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        raise ValueError("No numeric columns found for distribution overview.")
    return pd.DataFrame({
        "count": numeric_df.count(),
        "mean": numeric_df.mean(),
        "std": numeric_df.std(),
        "min": numeric_df.min(),
        "max": numeric_df.max(),
        "skewness": numeric_df.skew(),
        "kurtosis": numeric_df.kurtosis(),
    })


def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> dict[str, Any]:
    """Count outliers in a numeric column using the IQR rule.

    A value is an outlier when it falls outside
    ``[Q1 - factor * IQR, Q3 + factor * IQR]``.
    """
    if column not in df.columns:
        raise KeyError(f"Column not found: {column}")
    series = df[column]
    if not pd.api.types.is_numeric_dtype(series):
        raise ValueError(f"Outlier detection requires a numeric column, got '{column}'.")
    non_null = series.dropna()
    if non_null.empty:
        raise ValueError(f"Column '{column}' contains no values to analyze.")

    q1 = float(non_null.quantile(0.25))
    q3 = float(non_null.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    outlier_mask = (series < lower) | (series > upper)
    count = int(outlier_mask.sum())

    return {
        "column": column,
        "count": count,
        "total_rows": int(non_null.count()),
        "fraction": round(count / max(len(non_null), 1), 4),
        "lower_bound": round(lower, 6),
        "upper_bound": round(upper, 6),
    }


def get_categorical_frequencies(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return value counts and percentages for a column, most frequent first."""
    if column not in df.columns:
        raise KeyError(f"Column not found: {column}")
    counts = df[column].value_counts(dropna=False)
    total = int(counts.sum())
    return pd.DataFrame({
        "value": counts.index,
        "count": counts.values,
        "percent": [round(count / total * 100, 2) if total else 0.0 for count in counts.values],
    })
