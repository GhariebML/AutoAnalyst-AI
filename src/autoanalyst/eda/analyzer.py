"""Exploratory data analysis and statistical diagnostics utilities."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for all numeric columns."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        raise ValueError("No numeric columns found for summary.")
    return numeric_df.describe().T


def get_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Return a correlation matrix for numeric columns.

    Supported methods: 'pearson', 'spearman', 'kendall'.
    """
    valid_methods = {"pearson", "spearman", "kendall"}
    if method not in valid_methods:
        raise ValueError(f"Method '{method}' is not supported. Must be one of: {valid_methods}")

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        raise ValueError("At least two numeric columns are required for correlation.")
    return numeric_df.corr(method=method)


def get_distribution_overview(df: pd.DataFrame) -> pd.DataFrame:
    """Return comprehensive distribution statistics and shape classifications for numeric columns."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        raise ValueError("No numeric columns found for distribution overview.")

    rows: list[dict[str, Any]] = []
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        n = len(series)
        if n == 0:
            continue

        mean_val = float(series.mean())
        std_val = float(series.std()) if n > 1 else 0.0
        min_val = float(series.min())
        max_val = float(series.max())
        skew_val = float(series.skew()) if n > 2 else 0.0
        kurt_val = float(series.kurtosis()) if n > 3 else 0.0

        # Distribution classification
        classification, normality_p = _classify_distribution(series)

        rows.append(
            {
                "column": str(col),
                "count": n,
                "mean": round(mean_val, 4),
                "std": round(std_val, 4),
                "min": round(min_val, 4),
                "median": round(float(series.median()), 4),
                "max": round(max_val, 4),
                "skewness": round(skew_val, 4),
                "kurtosis": round(kurt_val, 4),
                "normality_p_value": round(normality_p, 4) if normality_p is not None else None,
                "distribution_type": classification,
            }
        )

    return pd.DataFrame(rows).set_index("column")


def _classify_distribution(series: pd.Series) -> tuple[str, float | None]:
    """Test and classify the empirical distribution shape of a numeric series."""
    n = len(series)
    if n < 8:
        return "Small Sample (<8)", None

    if series.nunique() <= 1:
        return "Constant", None

    p_value: float | None = None
    try:
        if 8 <= n <= 5000:
            stat, p_val = stats.shapiro(series)
            p_value = float(p_val)
        else:
            stat, p_val = stats.normaltest(series)
            p_value = float(p_val)
    except Exception:
        p_value = None

    skewness = float(series.skew())
    kurtosis = float(series.kurtosis())

    if p_value is not None and p_value > 0.05 and abs(skewness) < 0.5:
        return "Normal (Gaussian)", p_value
    elif skewness > 1.0:
        return "Right-Skewed (Positive Tail)", p_value
    elif skewness < -1.0:
        return "Left-Skewed (Negative Tail)", p_value
    elif abs(skewness) < 0.5 and kurtosis < -1.0:
        return "Uniform / Flat", p_value
    elif kurtosis > 3.0:
        return "Heavy-Tailed (Leptokurtic)", p_value
    else:
        return "Moderate Skew / Non-Normal", p_value


def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> dict[str, Any]:
    """Count and locate outliers in a numeric column using the IQR rule.

    A value is an outlier when it falls outside [Q1 - factor * IQR, Q3 + factor * IQR].
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
        "method": "IQR",
        "count": count,
        "total_rows": int(non_null.count()),
        "fraction": round(count / max(len(non_null), 1), 4),
        "lower_bound": round(lower, 6),
        "upper_bound": round(upper, 6),
    }


def detect_outliers_zscore(df: pd.DataFrame, column: str, threshold: float = 3.0) -> dict[str, Any]:
    """Count and locate outliers in a numeric column using the standard Z-score rule.

    A value is an outlier when |(x - mean) / std| > threshold.
    """
    if column not in df.columns:
        raise KeyError(f"Column not found: {column}")
    series = df[column]
    if not pd.api.types.is_numeric_dtype(series):
        raise ValueError(f"Outlier detection requires a numeric column, got '{column}'.")
    non_null = series.dropna()
    if non_null.empty:
        raise ValueError(f"Column '{column}' contains no values to analyze.")

    mean_val = float(non_null.mean())
    std_val = float(non_null.std())

    if std_val == 0.0:
        return {
            "column": column,
            "method": "Z-Score",
            "count": 0,
            "total_rows": int(non_null.count()),
            "fraction": 0.0,
            "lower_bound": mean_val,
            "upper_bound": mean_val,
        }

    z_scores = (non_null - mean_val) / std_val
    outlier_mask = np.abs(z_scores) > threshold
    count = int(outlier_mask.sum())

    lower_bound = mean_val - (threshold * std_val)
    upper_bound = mean_val + (threshold * std_val)

    return {
        "column": column,
        "method": "Z-Score",
        "count": count,
        "total_rows": int(non_null.count()),
        "fraction": round(count / max(len(non_null), 1), 4),
        "lower_bound": round(lower_bound, 6),
        "upper_bound": round(upper_bound, 6),
    }


def get_outliers_summary(df: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
    """Generate a summary table of outliers across all numeric columns in a DataFrame."""
    numeric_cols = df.select_dtypes(include="number").columns
    results: list[dict[str, Any]] = []

    for col in numeric_cols:
        try:
            if method.lower() == "zscore":
                res = detect_outliers_zscore(df, str(col))
            else:
                res = detect_outliers_iqr(df, str(col))
            results.append(res)
        except Exception as exc:
            logger.warning("Could not analyze outliers for '%s': %s", col, exc)

    return pd.DataFrame(results) if results else pd.DataFrame()


def get_categorical_frequencies(df: pd.DataFrame, column: str, top_n: int | None = None) -> pd.DataFrame:
    """Return value counts and percentages for a column, sorted most frequent first."""
    if column not in df.columns:
        raise KeyError(f"Column not found: {column}")
    counts = df[column].value_counts(dropna=False)
    if top_n is not None and top_n > 0:
        counts = counts.head(top_n)
    total = int(df[column].shape[0])
    return pd.DataFrame(
        {
            "value": counts.index.astype(str),
            "count": counts.values,
            "percent": [round(count / total * 100.0, 2) if total else 0.0 for count in counts.values],
        }
    )
