"""General helper utilities for AutoAnalyst AI."""

from pathlib import Path


def ensure_directory(path: str) -> Path:
    """Create a directory if it does not exist and return it as a Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def normalize_column_names(columns: list[str]) -> list[str]:
    """Normalize column names to lowercase snake_case."""
    return [column.strip().lower().replace(" ", "_").replace("-", "_") for column in columns]
