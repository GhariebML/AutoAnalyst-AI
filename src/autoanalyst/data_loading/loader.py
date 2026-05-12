"""Data loading utilities for AutoAnalyst AI."""

from pathlib import Path

import pandas as pd


def _validate_file_path(file_path: str) -> Path:
    """Validate that a file path exists and points to a file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    return path


def load_csv(file_path: str, **kwargs) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    path = _validate_file_path(file_path)
    try:
        return pd.read_csv(path, **kwargs)
    except Exception as exc:
        raise ValueError(f"Could not load CSV file '{file_path}': {exc}") from exc


def load_excel(file_path: str, sheet_name: str | int = 0, **kwargs) -> pd.DataFrame:
    """Load an Excel file into a pandas DataFrame."""
    path = _validate_file_path(file_path)
    try:
        return pd.read_excel(path, sheet_name=sheet_name, **kwargs)
    except Exception as exc:
        raise ValueError(f"Could not load Excel file '{file_path}': {exc}") from exc
