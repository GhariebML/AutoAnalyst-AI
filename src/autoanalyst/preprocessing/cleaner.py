"""Data cleaning functions for preprocessing datasets."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# Skewness threshold: if abs(skewness) exceeds this, use median instead of mean.
# A value of 1.0 is a common heuristic for moderate skewness.
SKEWNESS_THRESHOLD = 1.0


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with duplicate rows removed."""
    before = len(df)
    result = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(result)
    if removed > 0:
        logger.info("Removed %d duplicate row(s).", removed)
    else:
        logger.info("No duplicate rows found.")
    return result


def handle_missing_values(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Handle missing values using a simple strategy.

    Supported strategies: median, mean, mode, drop.

    For numeric columns with strategy='median' or 'mean', the actual method
    is chosen based on distribution skewness:
    - If abs(skewness) > SKEWNESS_THRESHOLD, median is used (robust to outliers).
    - Otherwise, the requested strategy (mean or median) is used.

    This prevents mean imputation from being distorted by heavily skewed data.
    """
    strategy = strategy.lower()
    cleaned = df.copy()

    if strategy == "drop":
        logger.info("Dropping rows with missing values.")
        return cleaned.dropna().reset_index(drop=True)

    if strategy not in {"median", "mean", "mode"}:
        raise ValueError("strategy must be one of: median, mean, mode, drop")

    total_missing = int(cleaned.isna().sum().sum())
    logger.info(
        "Handling missing values: strategy='%s', total_missing=%d, shape=%s",
        strategy, total_missing, cleaned.shape,
    )

    for column in cleaned.columns:
        if not cleaned[column].isna().any():
            continue

        missing_count = int(cleaned[column].isna().sum())

        if pd.api.types.is_numeric_dtype(cleaned[column]):
            # Skewness-aware imputation for numeric columns
            non_null = cleaned[column].dropna()
            if len(non_null) == 0:
                # All-null numeric column: fill with 0
                logger.warning(
                    "Column '%s' is entirely null. Filling with 0.", column,
                )
                cleaned[column] = cleaned[column].fillna(0)
                continue

            skewness = float(non_null.skew())
            if strategy in {"median", "mean"} and abs(skewness) > SKEWNESS_THRESHOLD:
                # Skewed distribution: always use median for robustness
                fill_value = cleaned[column].median()
                logger.info(
                    "Column '%s': skewed (skew=%.2f), using median=%.2f "
                    "(requested '%s'). Filling %d null(s).",
                    column, skewness, fill_value, strategy, missing_count,
                )
            elif strategy == "median":
                fill_value = cleaned[column].median()
                logger.info(
                    "Column '%s': using median=%.2f. Filling %d null(s).",
                    column, fill_value, missing_count,
                )
            else:  # mean
                fill_value = cleaned[column].mean()
                logger.info(
                    "Column '%s': using mean=%.2f. Filling %d null(s).",
                    column, fill_value, missing_count,
                )
        else:
            # Categorical/text columns: always use mode
            modes = cleaned[column].mode(dropna=True)
            fill_value = modes.iloc[0] if not modes.empty else "Unknown"
            logger.info(
                "Column '%s': using mode='%s'. Filling %d null(s).",
                column, fill_value, missing_count,
            )

        cleaned[column] = cleaned[column].fillna(fill_value)

    remaining = int(cleaned.isna().sum().sum())
    logger.info(
        "Missing value handling complete. Remaining nulls: %d.", remaining,
    )
    return cleaned
