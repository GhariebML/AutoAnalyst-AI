"""Data loading utilities for AutoAnalyst AI.

Supports CSV, Excel, Parquet, JSON, and SQLite data formats with
file validation, memory estimation, size guardrails, and chunked previews.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Default file size limit: 500 MB
DEFAULT_MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024


@dataclass
class DatasetMetadata:
    """Metadata describing a loaded or inspected dataset."""

    file_path: str
    file_size_bytes: int
    file_format: str
    estimated_memory_bytes: int
    num_rows: int | None = None
    num_columns: int | None = None
    columns: list[str] | None = None


def _validate_file_path(file_path: str | Path, max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES) -> Path:
    """Validate that a file path exists, is a file, and does not exceed size guardrails."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: '{file_path}'")
    if not path.is_file():
        raise ValueError(f"Path is not a regular file: '{file_path}'")

    file_size = path.stat().st_size
    if file_size == 0:
        raise ValueError(f"File is empty (0 bytes): '{file_path}'")
    if file_size > max_file_size_bytes:
        limit_mb = max_file_size_bytes / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise ValueError(
            f"File size ({actual_mb:.1f} MB) exceeds maximum allowed size ({limit_mb:.1f} MB): '{file_path}'"
        )
    return path


def estimate_memory_usage(df: pd.DataFrame) -> int:
    """Return estimated memory usage in bytes for a DataFrame."""
    return int(df.memory_usage(deep=True).sum())


def load_csv(
    file_path: str | Path, max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES, **kwargs: Any
) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    path = _validate_file_path(file_path, max_file_size_bytes=max_file_size_bytes)
    try:
        df = pd.read_csv(path, **kwargs)
        if df.empty and path.stat().st_size > 0 and len(df.columns) == 0:
            raise ValueError("CSV contains no columns or parseable data.")
        return df
    except Exception as exc:
        if isinstance(exc, (ValueError, FileNotFoundError)):
            raise
        raise ValueError(f"Could not load CSV file '{file_path}': {exc}") from exc


def load_excel(
    file_path: str | Path,
    sheet_name: str | int = 0,
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    **kwargs: Any,
) -> pd.DataFrame:
    """Load an Excel file (.xlsx, .xls) into a pandas DataFrame."""
    path = _validate_file_path(file_path, max_file_size_bytes=max_file_size_bytes)
    try:
        return pd.read_excel(path, sheet_name=sheet_name, **kwargs)
    except Exception as exc:
        if isinstance(exc, (ValueError, FileNotFoundError)):
            raise
        raise ValueError(f"Could not load Excel file '{file_path}': {exc}") from exc


def load_parquet(
    file_path: str | Path,
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    **kwargs: Any,
) -> pd.DataFrame:
    """Load a Parquet file (.parquet, .pq) into a pandas DataFrame."""
    path = _validate_file_path(file_path, max_file_size_bytes=max_file_size_bytes)
    try:
        return pd.read_parquet(path, **kwargs)
    except Exception as exc:
        if isinstance(exc, (ValueError, FileNotFoundError)):
            raise
        raise ValueError(f"Could not load Parquet file '{file_path}': {exc}") from exc


def load_json(
    file_path: str | Path,
    lines: bool = False,
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    **kwargs: Any,
) -> pd.DataFrame:
    """Load a JSON or JSONL file into a pandas DataFrame."""
    path = _validate_file_path(file_path, max_file_size_bytes=max_file_size_bytes)
    try:
        try:
            return pd.read_json(path, lines=lines, **kwargs)
        except Exception:
            # Fallback to lines=True if lines=False failed or vice versa
            return pd.read_json(path, lines=not lines, **kwargs)
    except Exception as exc:
        raise ValueError(f"Could not load JSON file '{file_path}': {exc}") from exc


def load_sqlite(
    file_path: str | Path,
    table_name: str | None = None,
    query: str | None = None,
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> pd.DataFrame:
    """Load data from a SQLite database (.sqlite, .db)."""
    path = _validate_file_path(file_path, max_file_size_bytes=max_file_size_bytes)
    try:
        with sqlite3.connect(str(path)) as conn:
            if query:
                return pd.read_sql_query(query, conn)
            if not table_name:
                # Find first user table
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                tables = [row[0] for row in cursor.fetchall()]
                if not tables:
                    raise ValueError(f"No tables found in SQLite database '{file_path}'.")
                table_name = tables[0]
            return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except Exception as exc:
        if isinstance(exc, (ValueError, FileNotFoundError)):
            raise
        raise ValueError(f"Could not load SQLite file '{file_path}': {exc}") from exc


def load_dataset(
    file_path: str | Path, max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES, **kwargs: Any
) -> pd.DataFrame:
    """Unified entrypoint to load a dataset from any supported file format.

    Supported extensions:
    - CSV: ``.csv``
    - Excel: ``.xlsx``, ``.xls``
    - Parquet: ``.parquet``, ``.pq``
    - JSON: ``.json``, ``.jsonl``
    - SQLite: ``.sqlite``, ``.db``
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return load_csv(path, max_file_size_bytes=max_file_size_bytes, **kwargs)
    if suffix in {".xlsx", ".xls"}:
        return load_excel(path, max_file_size_bytes=max_file_size_bytes, **kwargs)
    if suffix in {".parquet", ".pq"}:
        return load_parquet(path, max_file_size_bytes=max_file_size_bytes, **kwargs)
    if suffix in {".json", ".jsonl"}:
        return load_json(path, max_file_size_bytes=max_file_size_bytes, **kwargs)
    if suffix in {".sqlite", ".db"}:
        return load_sqlite(path, max_file_size_bytes=max_file_size_bytes, **kwargs)

    raise ValueError(
        f"Unsupported file format '{suffix}'. Supported formats are: CSV (.csv), Excel (.xlsx, .xls), "
        f"Parquet (.parquet, .pq), JSON (.json, .jsonl), and SQLite (.sqlite, .db)."
    )


def preview_dataset(file_path: str | Path, n_rows: int = 5) -> pd.DataFrame:
    """Read a fast sample preview of a dataset without loading the entire file."""
    path = _validate_file_path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path, nrows=n_rows)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, nrows=n_rows)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path).head(n_rows)
    if suffix in {".json", ".jsonl"}:
        try:
            return pd.read_json(path, nrows=n_rows)
        except Exception:
            return pd.read_json(path, lines=True, nrows=n_rows)
    if suffix in {".sqlite", ".db"}:
        with sqlite3.connect(str(path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            if not tables:
                raise ValueError(f"No tables found in SQLite database '{file_path}'.")
            return pd.read_sql_query(f"SELECT * FROM {tables[0]} LIMIT {n_rows}", conn)

    raise ValueError(f"Unsupported file format '{suffix}' for preview.")
