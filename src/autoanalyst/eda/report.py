"""
EDA Engine report module.

Combines the descriptive statistics, correlation analysis, and Plotly
visualizations produced by `analyzer.py` and `visualizer.py` into a single,
self-contained HTML report for the post-ingestion analysis layer.

This module is scoped to the EDA team's own output. It does not read from
or write to `autoanalyst.insights` or `autoanalyst.reporting`, which are
owned by separate feature branches/teams.
"""

import logging
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from autoanalyst.eda.analyzer import get_numeric_summary
from autoanalyst.eda.visualizer import (
    plot_category_breakdown,
    plot_correlation_heatmap,
    plot_distribution,
)

logger = logging.getLogger(__name__)

PLOTLY_CDN_URL = "https://cdn.plot.ly/plotly-2.32.0.min.js"

REPORT_CSS = """
<style>
  :root {
    --bg: #f5f6fa;
    --card-bg: #ffffff;
    --text: #1f2430;
    --muted: #6b7280;
    --accent: #4f46e5;
    --border: #e5e7eb;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 32px 16px 64px;
  }
  .report-container {
    max-width: 960px;
    margin: 0 auto;
  }
  h1 {
    font-size: 28px;
    font-weight: 700;
    border-bottom: 3px solid var(--accent);
    padding-bottom: 12px;
    margin-bottom: 24px;
  }
  h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--accent);
    margin-top: 40px;
    margin-bottom: 12px;
  }
  h3 {
    font-size: 15px;
    font-weight: 600;
    color: var(--muted);
    margin-top: 24px;
    margin-bottom: 8px;
  }
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 14px;
  }
  th, td {
    padding: 8px 12px;
    text-align: right;
    border-bottom: 1px solid var(--border);
  }
  th {
    background: #fafafa;
    color: var(--muted);
    font-weight: 600;
  }
  tr:hover td {
    background: #fafbff;
  }
  .skipped {
    color: var(--muted);
    font-style: italic;
  }
</style>
"""


def _figure_to_html_div(fig_dict: dict) -> str:
    """Convert Plotly figure metadata (a data/layout dict) into a styled, embeddable HTML div."""
    fig = go.Figure(data=fig_dict.get("data", []), layout=fig_dict.get("layout", {}))
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=50, r=30, t=50, b=40),
        height=420,
        font=dict(family="-apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"),
    )
    html_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
    return f'<div class="card">{html_div}</div>'


def generate_eda_html_report(
    df: pd.DataFrame,
    output_path: str,
    category_column: str = None,
    target_column: str = None,
) -> Path:
    """Generate a single-file HTML EDA report for a DataFrame.

    The report includes a descriptive-statistics table, a correlation
    heatmap (when at least 2 numeric columns exist), a distribution plot
    for every numeric column, and an optional business breakdown for a
    categorical column (counts, or a rate per category when target_column
    is also provided).

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe coming from the ingestion step.
    output_path : str
        File path where the HTML report will be written.
    category_column : str, optional
        Categorical column to break down (e.g. "loan_grade").
    target_column : str, optional
        Numeric target column to compute a rate per category
        (e.g. "loan_status"). Ignored if category_column is not provided.

    Returns
    -------
    Path
        Path to the generated HTML report.

    Raises
    ------
    KeyError
        If df is None.
    ValueError
        If df is empty or has no numeric columns to summarize.
    """
    if df is None:
        logger.warning("generate_eda_html_report received None instead of a DataFrame.")
        raise KeyError("Input dataframe is missing (received None).")

    if df.empty:
        logger.warning("generate_eda_html_report received an empty DataFrame.")
        raise ValueError("Input dataframe is empty; no report can be generated.")

    logger.info("Building EDA HTML report for a dataframe with shape %s.", df.shape)

    sections = ["<h1>EDA Report</h1>"]

    summary = get_numeric_summary(df)
    sections.append("<h2>Descriptive Statistics</h2>")
    sections.append(f'<div class="card">{summary.to_html(border=0)}</div>')

    sections.append("<h2>Correlation Heatmap</h2>")
    try:
        heatmap_dict = plot_correlation_heatmap(df)
        sections.append(_figure_to_html_div(heatmap_dict))
    except ValueError as exc:
        logger.info("Skipping correlation heatmap: %s", exc)
        sections.append(f'<p class="skipped">Skipped: {exc}</p>')

    sections.append("<h2>Distributions</h2>")
    numeric_columns = df.select_dtypes(include="number").columns
    for column in numeric_columns:
        try:
            dist_dict = plot_distribution(df, column)
            sections.append(f"<h3>{column}</h3>")
            sections.append(_figure_to_html_div(dist_dict))
        except ValueError as exc:
            logger.info("Skipping distribution for '%s': %s", column, exc)

    if category_column is not None:
        sections.append(f"<h2>Breakdown by {category_column}</h2>")
        try:
            breakdown_dict = plot_category_breakdown(df, category_column, target_column)
            sections.append(_figure_to_html_div(breakdown_dict))
        except (KeyError, ValueError) as exc:
            logger.info("Skipping category breakdown: %s", exc)
            sections.append(f'<p class="skipped">Skipped: {exc}</p>')

    body = "".join(sections)
    html = (
        "<html><head><meta charset='utf-8'>"
        f"<script src='{PLOTLY_CDN_URL}'></script>"
        f"{REPORT_CSS}"
        f'</head><body><div class="report-container">{body}</div></body></html>'
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")

    logger.info("EDA HTML report written to %s.", path)
    return path
