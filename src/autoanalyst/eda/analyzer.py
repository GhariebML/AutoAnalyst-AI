"""
EDA Engine analyzer module.

Post-ingestion analysis layer for AutoAnalyst AI.
Provides descriptive statistics and correlation analysis utilities
for the numeric features of an ingested pandas DataFrame.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

VALID_CORRELATION_METHODS = {"pearson", "kendall", "spearman"}


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate descriptive statistics for all numeric columns (describe transpose).

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.

    Returns
    -------
    pd.DataFrame
        DataFrame with column names as the index and statistics
        (count, mean, std, min, 25%, 50%, 75%, max) as columns.

    Raises
    ------
    KeyError
        If df is None (i.e. missing from the pipeline call).
    ValueError
        If df is empty or contains no numeric columns.
    """
    if df is None:
        logger.warning("get_numeric_summary received None instead of a DataFrame.")
        raise KeyError("Input dataframe is missing (received None).")

    if df.empty:
        logger.warning("get_numeric_summary received an empty DataFrame.")
        raise ValueError("Input dataframe is empty; no summary can be generated.")

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] == 0:
        logger.warning("No numeric columns found in the provided DataFrame.")
        raise ValueError("No numeric columns found to summarize.")

    logger.info(
        "Generating numeric summary for %d numeric column(s) out of %d total.",
        numeric_df.shape[1],
        df.shape[1],
    )

    try:
        summary = numeric_df.describe().T
    except Exception as exc:
        logger.warning("Unexpected error while computing numeric summary: %s", exc)
        raise ValueError(f"Could not generate numeric summary due to a data issue: {exc}") from exc

    return summary


def get_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Generate a correlation matrix for numeric features.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.
    method : str, default "pearson"
        Correlation method to use: "pearson", "kendall", or "spearman".

    Returns
    -------
    pd.DataFrame
        Square correlation matrix indexed and labeled by numeric column names.

    Raises
    ------
    KeyError
        If df is None (i.e. missing from the pipeline call).
    ValueError
        If df is empty, method is not a supported correlation method,
        or fewer than 2 numeric columns are available.
    """
    if df is None:
        logger.warning("get_correlation_matrix received None instead of a DataFrame.")
        raise KeyError("Input dataframe is missing (received None).")

    if method not in VALID_CORRELATION_METHODS:
        logger.warning("Invalid correlation method requested: %s", method)
        raise ValueError(
            f"Invalid method '{method}'. Choose one of {sorted(VALID_CORRELATION_METHODS)}."
        )

    if df.empty:
        logger.warning("get_correlation_matrix received an empty DataFrame.")
        raise ValueError("Input dataframe is empty; no correlation matrix can be generated.")

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        logger.warning(
            "Not enough numeric columns (%d) to compute a correlation matrix.",
            numeric_df.shape[1],
        )
        raise ValueError(
            "At least 2 numeric columns are required to compute a correlation matrix."
        )

    logger.info(
        "Computing %s correlation matrix for %d numeric column(s).",
        method,
        numeric_df.shape[1],
    )

    try:
        correlation_matrix = numeric_df.corr(method=method)
    except Exception as exc:
        logger.warning("Unexpected error while computing correlation matrix: %s", exc)
        raise ValueError(
            f"Could not generate correlation matrix due to a data issue: {exc}"
        ) from exc

    return correlation_matrix
