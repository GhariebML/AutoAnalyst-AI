"""Dataset profiling helpers for quick data understanding."""

from typing import Any

import pandas as pd


def generate_basic_profile(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a compact profile summary for a DataFrame."""
    if df.empty:
        raise ValueError("Cannot profile an empty DataFrame.")
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "missing_values_total": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def get_missing_values_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing-value counts and percentages per column."""
    total_rows = len(df)
    missing_count = df.isna().sum()
    if total_rows:
        missing_percent = missing_count / total_rows * 100
    else:
        missing_percent = missing_count * 0
    return pd.DataFrame({
        "column": missing_count.index,
        "missing_count": missing_count.values,
        "missing_percent": missing_percent.values,
    }).sort_values("missing_count", ascending=False)


def get_duplicate_count(df: pd.DataFrame) -> int:
    """Return the number of duplicated rows in a DataFrame."""
    return int(df.duplicated().sum())
