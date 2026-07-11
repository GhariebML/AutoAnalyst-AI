"""Markdown report generation utilities."""

from pathlib import Path


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
