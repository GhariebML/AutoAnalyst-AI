"""
EDA Engine visualizer module.

Generates Plotly-based visualizations for the post-ingestion analysis layer
of AutoAnalyst AI. Each function returns structured, JSON-serializable
metadata (a dict with "data" and "layout" keys) suitable for rendering by
Plotly-based front-end widgets, rather than a static rendered image.
"""

import logging

import pandas as pd
import plotly.express as px

from autoanalyst.eda.analyzer import get_correlation_matrix

logger = logging.getLogger(__name__)


def _validate_dataframe(df: pd.DataFrame) -> None:
    """Shared guard clause: df must exist and must not be empty."""
    if df is None:
        logger.warning("Visualizer function received None instead of a DataFrame.")
        raise KeyError("Input dataframe is missing (received None).")

    if df.empty:
        logger.warning("Visualizer function received an empty DataFrame.")
        raise ValueError("Input dataframe is empty; nothing to plot.")


def _validate_numeric_column(df: pd.DataFrame, column: str) -> None:
    """Shared guard clause: column must exist, be numeric, and have data."""
    if column not in df.columns:
        logger.warning("Column '%s' not found in the provided DataFrame.", column)
        raise KeyError(f"Column '{column}' not found in the dataframe.")

    if not pd.api.types.is_numeric_dtype(df[column]):
        logger.warning("Column '%s' is not numeric.", column)
        raise ValueError(f"Column '{column}' is not numeric; cannot generate this plot.")

    if df[column].dropna().empty:
        logger.warning("Column '%s' has no non-null values.", column)
        raise ValueError(f"Column '{column}' has no non-null values to plot.")


def plot_histogram(df: pd.DataFrame, column: str) -> dict:
    """Generate histogram metadata for a single numeric column.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.
    column : str
        Name of the numeric column to plot.

    Returns
    -------
    dict
        JSON-serializable Plotly figure metadata (data + layout).

    Raises
    ------
    KeyError
        If df is None or column is not found in df.
    ValueError
        If df is empty, column is not numeric, or column has no data.
    """
    _validate_dataframe(df)
    _validate_numeric_column(df, column)

    logger.info("Generating histogram for column '%s'.", column)
    fig = px.histogram(df, x=column, title=f"Distribution of {column}")

    return fig.to_plotly_json()


def plot_distribution(df: pd.DataFrame, column: str) -> dict:
    """Generate a distribution view (histogram with a box-plot margin) for a numeric column.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.
    column : str
        Name of the numeric column to analyze.

    Returns
    -------
    dict
        JSON-serializable Plotly figure metadata (data + layout).

    Raises
    ------
    KeyError
        If df is None or column is not found in df.
    ValueError
        If df is empty, column is not numeric, or column has no data.
    """
    _validate_dataframe(df)
    _validate_numeric_column(df, column)

    logger.info("Generating distribution analysis for column '%s'.", column)
    fig = px.histogram(df, x=column, marginal="box", title=f"Distribution of {column}")

    return fig.to_plotly_json()


def plot_correlation_heatmap(df: pd.DataFrame, method: str = "pearson") -> dict:
    """Generate a correlation heatmap for numeric features.

    Reuses `get_correlation_matrix` so the underlying numbers always match
    the values reported by the analyzer module.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.
    method : str, default "pearson"
        Correlation method: "pearson", "kendall", or "spearman".

    Returns
    -------
    dict
        JSON-serializable Plotly figure metadata (data + layout).

    Raises
    ------
    KeyError
        If df is None.
    ValueError
        If df is empty, method is invalid, or fewer than 2 numeric columns exist.
    """
    correlation_matrix = get_correlation_matrix(df, method=method)

    logger.info(
        "Generating %s correlation heatmap for %d numeric column(s).",
        method,
        correlation_matrix.shape[1],
    )

    fig = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"Correlation Heatmap ({method})",
    )

    return fig.to_plotly_json()


def plot_scatter(df: pd.DataFrame, x_column: str, y_column: str, color_column: str = None) -> dict:
    """Generate a scatter plot between two numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.
    x_column : str
        Name of the numeric column for the x-axis.
    y_column : str
        Name of the numeric column for the y-axis.
    color_column : str, optional
        Name of a column used to color points (e.g. a category or target column).

    Returns
    -------
    dict
        JSON-serializable Plotly figure metadata (data + layout).

    Raises
    ------
    KeyError
        If df is None, or x_column/y_column/color_column is not found in df.
    ValueError
        If df is empty, or x_column/y_column is not numeric or has no data.
    """
    _validate_dataframe(df)
    _validate_numeric_column(df, x_column)
    _validate_numeric_column(df, y_column)

    if color_column is not None and color_column not in df.columns:
        logger.warning("Color column '%s' not found in the provided DataFrame.", color_column)
        raise KeyError(f"Column '{color_column}' not found in the dataframe.")

    logger.info("Generating scatter plot: %s vs %s.", y_column, x_column)
    fig = px.scatter(
        df,
        x=x_column,
        y=y_column,
        color=color_column,
        title=f"{y_column} vs {x_column}",
    )

    return fig.to_plotly_json()


def plot_category_breakdown(
    df: pd.DataFrame, category_column: str, target_column: str = None
) -> dict:
    """Generate a business-facing breakdown of a categorical column.

    With no target_column, this shows the count of records per category
    (e.g. how many loans fall under each loan_grade). With a target_column,
    this shows the mean of that column per category (e.g. the default rate
    within each loan_grade) -- the "business visualization" use case.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.
    category_column : str
        Name of the categorical column to group by.
    target_column : str, optional
        Name of a numeric column to average per category (e.g. a binary
        target such as loan_status). If omitted, raw category counts are shown.

    Returns
    -------
    dict
        JSON-serializable Plotly figure metadata (data + layout).

    Raises
    ------
    KeyError
        If df is None, or category_column/target_column is not found in df.
    ValueError
        If df is empty, or target_column is provided but is not numeric.
    """
    _validate_dataframe(df)

    if category_column not in df.columns:
        logger.warning("Category column '%s' not found in the provided DataFrame.", category_column)
        raise KeyError(f"Column '{category_column}' not found in the dataframe.")

    if target_column is None:
        logger.info("Generating category breakdown (counts) for '%s'.", category_column)
        counts = df[category_column].value_counts().reset_index()
        counts.columns = [category_column, "count"]
        fig = px.bar(
            counts,
            x=category_column,
            y="count",
            title=f"Distribution of {category_column}",
        )
        return fig.to_plotly_json()

    if target_column not in df.columns:
        logger.warning("Target column '%s' not found in the provided DataFrame.", target_column)
        raise KeyError(f"Column '{target_column}' not found in the dataframe.")

    if not pd.api.types.is_numeric_dtype(df[target_column]):
        logger.warning("Target column '%s' is not numeric.", target_column)
        raise ValueError(f"Column '{target_column}' is not numeric; cannot compute a rate.")

    logger.info(
        "Generating '%s' rate by '%s'.",
        target_column,
        category_column,
    )
    rate = df.groupby(category_column, dropna=False)[target_column].mean().reset_index()
    fig = px.bar(
        rate,
        x=category_column,
        y=target_column,
        title=f"{target_column} rate by {category_column}",
    )

    return fig.to_plotly_json()
