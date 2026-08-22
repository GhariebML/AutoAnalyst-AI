"""Markdown report generation utilities."""

from pathlib import Path
from typing import Any

import pandas as pd

_MAX_TABLE_ROWS = 15


def create_markdown_report(title: str, insights: list[str], output_path: str) -> Path:
    """Create a simple Markdown report from generated insights."""
    if not title.strip():
        raise ValueError("Report title must not be empty.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", "## Key Insights", ""]
    lines.extend(f"- {insight}" for insight in insights)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def create_full_report(
    output_path: str,
    title: str,
    profile: dict[str, Any],
    insights: list[str],
    missing_report: pd.DataFrame | None = None,
    eda_results: dict[str, Any] | None = None,
    cleaning_log: list[str] | None = None,
    model_results: dict[str, Any] | None = None,
    evaluation_results: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    executive_summary: str | None = None,
) -> Path:
    """Compile a complete Markdown analysis report from pipeline artifacts.

    Every section except the overview and insights is optional and rendered
    only when its data is present, so the same builder serves runs with and
    without modeling.
    """
    if not title.strip():
        raise ValueError("Report title must not be empty.")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    eda_results = eda_results or {}
    lines: list[str] = [f"# {title}", ""]

    if executive_summary:
        lines.extend(["## Executive Summary", "", executive_summary])

    lines.extend(["", "## Dataset Overview", ""])
    lines.extend(_overview_table(profile))

    if missing_report is not None and not missing_report.empty:
        lines.extend(["", "## Missing Values", ""])
        lines.append(_frame_to_md(missing_report))

    numeric_summary = eda_results.get("numeric_summary")
    if isinstance(numeric_summary, pd.DataFrame) and not numeric_summary.empty:
        lines.extend(["", "## Exploratory Analysis — Numeric Summary", ""])
        lines.append(_frame_to_md(numeric_summary))

    correlation = eda_results.get("correlation_matrix")
    if isinstance(correlation, pd.DataFrame) and not correlation.empty:
        lines.extend(["", "### Correlation Matrix", ""])
        lines.append(_frame_to_md(correlation.round(3)))

    if cleaning_log:
        lines.extend(["", "## Cleaning Log", ""])
        lines.extend(f"- {entry}" for entry in cleaning_log)

    if model_results:
        lines.extend(["", "## Model Results", ""])
        lines.extend(_kv_table(model_results))

    if evaluation_results:
        lines.extend(["", "## Evaluation Metrics", ""])
        lines.extend(_metrics_tables(evaluation_results))

    lines.extend(["", "## Key Insights", ""])
    lines.extend(f"- {insight}" for insight in insights) if insights else lines.append("_No insights generated._")

    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _overview_table(profile: dict[str, Any]) -> list[str]:
    if not profile:
        return ["_No profile available._"]
    rows = [[str(key), str(value)] for key, value in profile.items() if key != "dtypes" and key != "column_names"]
    dtypes = profile.get("dtypes")
    if isinstance(dtypes, dict):
        for column, dtype in list(dtypes.items())[:_MAX_TABLE_ROWS]:
            rows.append([f"dtype: {column}", str(dtype)])
    return _md_table(rows, ["Property", "Value"])


def _kv_table(values: dict[str, Any]) -> list[str]:
    rows = [[str(key), str(value)] for key, value in values.items()]
    return _md_table(rows, ["Field", "Value"])


def _metrics_tables(evaluation_results: dict[str, Any]) -> list[str]:
    scalar_rows = [
        [str(key), f"{value:.6f}" if isinstance(value, float) else str(value)]
        for key, value in evaluation_results.items()
        if isinstance(value, (int, float))
    ]
    lines = _md_table(scalar_rows, ["Metric", "Value"]) if scalar_rows else []

    confusion = evaluation_results.get("confusion_matrix")
    if isinstance(confusion, list) and confusion:
        header_labels = _class_labels(evaluation_results.get("classification_report", {}), len(confusion))
        rows = [
            [header_labels[i] if i < len(header_labels) else str(i), *(str(cell) for cell in row)]
            for i, row in enumerate(confusion)
        ]
        lines.extend(["", "**Confusion matrix** (rows = actual, columns = predicted):", ""])
        lines.extend(_md_table(rows, ["actual \\ predicted", *header_labels]))

    report = evaluation_results.get("classification_report")
    if isinstance(report, dict):
        per_class_rows = []
        for label, stats in report.items():
            if not (isinstance(stats, dict) and {"precision", "recall", "f1-score", "support"} <= stats.keys()):
                continue
            per_class_rows.append([
                str(label),
                f"{stats['precision']:.3f}",
                f"{stats['recall']:.3f}",
                f"{stats['f1-score']:.3f}",
                str(stats["support"]),
            ])
        if per_class_rows:
            lines.extend(["", "**Per-class metrics**:", ""])
            lines.extend(_md_table(per_class_rows, ["label", "precision", "recall", "f1-score", "support"]))
    return lines


def _class_labels(report: dict[str, Any], matrix_size: int) -> list[str]:
    """Extract per-class label names from a classification report."""
    labels = [str(label) for label, stats in report.items() if isinstance(stats, dict)]
    if len(labels) >= matrix_size:
        return labels[:matrix_size]
    return [str(i) for i in range(matrix_size)]


def _md_table(rows: list[list[str]], headers: list[str]) -> list[str]:
    width = max((len(headers), *(len(row) for row in rows)))
    normalized = [row + [""] * (width - len(row)) for row in rows]
    lines = [
        "| " + " | ".join(headers + [""] * (width - len(headers))) + " |",
        "| " + " | ".join("---" for _ in range(width)) + " |",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in normalized)
    return lines


def _frame_to_md(df: pd.DataFrame, max_rows: int = _MAX_TABLE_ROWS) -> str:
    preview = df.head(max_rows)
    headers = [str(column) for column in preview.columns]
    rows = [[_cell(value) for value in row] for row in preview.itertuples(index=False, name=None)]
    text = "\n".join(_md_table(rows, headers))
    total = len(df)
    if total > max_rows:
        text += f"\n\n_Showing {max_rows} of {total} rows._"
    return text


def _cell(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
