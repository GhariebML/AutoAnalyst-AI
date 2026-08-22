"""Feature engineering helpers for AutoAnalyst AI."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# Default threshold for high-cardinality detection.
# Columns with more unique values than this ratio (unique / total rows)
# are flagged as high-cardinality.
DEFAULT_HIGH_CARDINALITY_RATIO = 0.9

# Absolute threshold: columns with more unique values than this are flagged.
DEFAULT_HIGH_CARDINALITY_THRESHOLD = 50


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


def detect_high_cardinality_columns(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    threshold: int = DEFAULT_HIGH_CARDINALITY_THRESHOLD,
    ratio: float = DEFAULT_HIGH_CARDINALITY_RATIO,
) -> list[dict[str, int | float | str]]:
    """Detect categorical columns with unusually high cardinality.

    Parameters
    ----------
    df:
        Input DataFrame.
    columns:
        Columns to check. If None, auto-detects categorical columns.
    threshold:
        Absolute unique-value count above which a column is flagged.
    ratio:
        Relative threshold (unique_count / total_rows) above which
        a column is flagged. Range [0, 1].

    Returns
    -------
    list of dicts with keys: column, unique_count, cardinality_ratio, status.
    """
    selected = columns or list(df.select_dtypes(include=["object", "category", "string"]).columns)
    total_rows = len(df)
    results: list[dict[str, int | float | str]] = []

    for col in selected:
        if col not in df.columns:
            continue
        unique_count = int(df[col].nunique(dropna=True))
        cardinality_ratio = unique_count / total_rows if total_rows > 0 else 0.0
        is_high = unique_count > threshold or cardinality_ratio > ratio
        status = "high_cardinality" if is_high else "normal"
        if is_high:
            logger.warning(
                "High-cardinality column detected: '%s' has %d unique values "
                "(ratio=%.2f, threshold=%d, ratio_threshold=%.2f).",
                col, unique_count, cardinality_ratio, threshold, ratio,
            )
        else:
            logger.info(
                "Column '%s' cardinality OK: %d unique values (ratio=%.2f).",
                col, unique_count, cardinality_ratio,
            )
        results.append({
            "column": col,
            "unique_count": unique_count,
            "cardinality_ratio": round(cardinality_ratio, 4),
            "status": status,
        })
    return results


def encode_categorical_columns(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """One-hot encode selected categorical columns.

    Logs a warning for high-cardinality columns before encoding.
    """
    selected = columns or list(df.select_dtypes(include=["object", "category", "string"]).columns)
    missing = [column for column in selected if column not in df.columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}")

    # Detect and log high-cardinality columns before encoding
    detect_high_cardinality_columns(df, columns=selected)

    logger.info("One-hot encoding %d column(s): %s", len(selected), selected)
    return pd.get_dummies(df, columns=selected, drop_first=True)
