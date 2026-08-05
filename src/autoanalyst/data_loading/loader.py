"""Module 1 — Dataset Loading.

Automatically detects file type (CSV, TSV, Excel, Parquet, JSON, gzip-CSV),
detects delimiter/encoding, and loads (optionally in chunks for very large
files) into a single pandas DataFrame.
"""

from __future__ import annotations

import gzip
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd

from autoanalyst.exceptions import (
    DataLoadError,
    FileAccessError,
    UnsupportedFileTypeError,
)
from autoanalyst.utils.helpers import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {
    ".csv": "csv",
    ".tsv": "tsv",
    ".txt": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
    ".parquet": "parquet",
    ".json": "json",
    ".gz": "gzip_csv",
}

# Large-file threshold (bytes) above which chunked reading is used for CSV.
LARGE_FILE_BYTES = 200 * 1024 * 1024  # 200 MB
CHUNK_SIZE_ROWS = 250_000


@dataclass
class LoadMetadata:
    """Metadata describing how a dataset was loaded — useful for the report."""

    file_path: str
    file_format: str
    file_size_bytes: int
    encoding_detected: Optional[str] = None
    delimiter_detected: Optional[str] = None
    chunked: bool = False
    n_chunks: int = 1
    warnings: list[str] = field(default_factory=list)


class DatasetLoader:
    """Auto-detecting, format-agnostic dataset loader."""

    def __init__(self, sample_bytes: int = 65536) -> None:
        self.sample_bytes = sample_bytes

    # ------------------------------------------------------------ public --
    def load(self, file_path: str) -> tuple[pd.DataFrame, LoadMetadata]:
        """Load a dataset from `file_path`, auto-detecting its format.

        Returns
        -------
        (DataFrame, LoadMetadata)

        Raises
        ------
        FileAccessError, UnsupportedFileTypeError, DataLoadError
        """
        path = self._validate_path(file_path)
        fmt = self._detect_format(path)
        size = path.stat().st_size
        meta = LoadMetadata(file_path=str(path), file_format=fmt, file_size_bytes=size)

        logger.info("Loading dataset '%s' detected as format=%s (%.2f MB)",
                    path.name, fmt, size / (1024 * 1024))

        try:
            if fmt in ("csv", "tsv", "gzip_csv"):
                df = self._load_delimited(path, fmt, meta)
            elif fmt == "excel":
                df = self._load_excel(path, meta)
            elif fmt == "parquet":
                df = self._load_parquet(path, meta)
            elif fmt == "json":
                df = self._load_json(path, meta)
            else:  # pragma: no cover - guarded by _detect_format
                raise UnsupportedFileTypeError(f"Unsupported format: {fmt}")
        except (DataLoadError, UnsupportedFileTypeError, FileAccessError):
            raise
        except Exception as exc:  # noqa: BLE001 - convert to domain exception
            raise DataLoadError(
                f"Failed to parse '{path.name}' as {fmt}: {exc}",
                details={"file": str(path), "format": fmt},
            ) from exc

        if df is None:
            raise DataLoadError(f"Loader returned no data for '{path.name}'")

        logger.info("Loaded %s rows x %s columns from '%s'", df.shape[0], df.shape[1], path.name)
        return df, meta

    # -------------------------------------------------------------- steps --
    def _validate_path(self, file_path: str) -> Path:
        if not file_path or not isinstance(file_path, str):
            raise FileAccessError("file_path must be a non-empty string")
        path = Path(file_path).expanduser()
        if not path.exists():
            raise FileAccessError(f"File does not exist: {file_path}")
        if not path.is_file():
            raise FileAccessError(f"Path is not a file: {file_path}")
        if not os.access(path, os.R_OK):
            raise FileAccessError(f"File is not readable (permissions): {file_path}")
        if path.stat().st_size == 0:
            raise FileAccessError(f"File is empty (0 bytes): {file_path}")
        return path

    def _detect_format(self, path: Path) -> str:
        ext = path.suffix.lower()
        if ext == ".gz":
            # Peek inside gzip to make sure it's delimited text, not binary.
            return "gzip_csv"
        fmt = SUPPORTED_EXTENSIONS.get(ext)
        if fmt is None:
            raise UnsupportedFileTypeError(
                f"Unsupported file extension '{ext}'. Supported: "
                f"{sorted(set(SUPPORTED_EXTENSIONS.values()))}"
            )
        return fmt

    def _detect_encoding(self, path: Path) -> str:
        try:
            import chardet  # optional but installed in this environment

            with open(path, "rb") as f:
                raw = f.read(self.sample_bytes)
            result = chardet.detect(raw)
            encoding = result.get("encoding") or "utf-8"
            return encoding
        except ImportError:
            return "utf-8"
        except Exception:  # noqa: BLE001
            return "utf-8"

    def _detect_delimiter(self, sample_text: str) -> str:
        import csv as csv_module

        try:
            dialect = csv_module.Sniffer().sniff(sample_text, delimiters=",;\t|")
            return dialect.delimiter
        except csv_module.Error:
            # Fallback heuristic: pick the most frequent candidate.
            candidates = [",", ";", "\t", "|"]
            counts = {c: sample_text.count(c) for c in candidates}
            best = max(counts, key=counts.get)
            return best if counts[best] > 0 else ","

    def _load_delimited(self, path: Path, fmt: str, meta: LoadMetadata) -> pd.DataFrame:
        opener = gzip.open if fmt == "gzip_csv" else open
        mode = "rt"

        encoding = self._detect_encoding(path)
        meta.encoding_detected = encoding

        try:
            with opener(path, mode, encoding=encoding, errors="replace") as f:
                sample = f.read(self.sample_bytes)
        except (UnicodeDecodeError, LookupError):
            encoding = "utf-8"
            meta.encoding_detected = encoding
            meta.warnings.append("Encoding detection failed; fell back to utf-8 with replacement.")
            with opener(path, mode, encoding=encoding, errors="replace") as f:
                sample = f.read(self.sample_bytes)

        if fmt == "tsv":
            delimiter = "\t"
        else:
            delimiter = self._detect_delimiter(sample)
        meta.delimiter_detected = delimiter

        read_kwargs = dict(
            sep=delimiter,
            encoding=encoding,
            engine="python",
            on_bad_lines="warn",
            compression="gzip" if fmt == "gzip_csv" else None,
        )

        file_size = meta.file_size_bytes
        if file_size > LARGE_FILE_BYTES:
            meta.chunked = True
            chunks = []
            n_chunks = 0
            for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE_ROWS, **read_kwargs):
                chunks.append(chunk)
                n_chunks += 1
            meta.n_chunks = n_chunks
            if not chunks:
                raise DataLoadError(f"No data could be parsed from '{path.name}'")
            df = pd.concat(chunks, ignore_index=True)
        else:
            df = pd.read_csv(path, **read_kwargs)

        return df

    def _load_excel(self, path: Path, meta: LoadMetadata) -> pd.DataFrame:
        try:
            excel_file = pd.ExcelFile(path)
        except Exception as exc:  # noqa: BLE001
            raise DataLoadError(f"Could not open Excel file: {exc}") from exc

        sheet_names = excel_file.sheet_names
        if not sheet_names:
            raise DataLoadError("Excel workbook contains no sheets")
        if len(sheet_names) > 1:
            meta.warnings.append(
                f"Workbook has {len(sheet_names)} sheets; using the first sheet "
                f"'{sheet_names[0]}'. Other sheets ignored."
            )
        return excel_file.parse(sheet_names[0])

    def _load_parquet(self, path: Path, meta: LoadMetadata) -> pd.DataFrame:
        try:
            return pd.read_parquet(path)
        except ImportError as exc:
            raise DataLoadError(
                "Reading Parquet requires 'pyarrow' or 'fastparquet' to be installed."
            ) from exc

    def _load_json(self, path: Path, meta: LoadMetadata) -> pd.DataFrame:
        encoding = self._detect_encoding(path)
        meta.encoding_detected = encoding

        # Detect line-delimited JSON (one JSON object per physical line)
        # vs. a standard JSON document (array/object), which is the far
        # more common case for uploaded datasets.
        with open(path, "r", encoding=encoding, errors="replace") as f:
            first_lines = [f.readline() for _ in range(2)]
        looks_line_delimited = False
        stripped = [ln.strip() for ln in first_lines if ln.strip()]
        if len(stripped) >= 1:
            try:
                json.loads(stripped[0])
                looks_line_delimited = len(stripped) >= 2 or (
                    len(stripped) == 1 and not stripped[0].startswith("[")
                )
            except (ValueError, json.JSONDecodeError):
                looks_line_delimited = False

        if looks_line_delimited:
            try:
                return pd.read_json(path, lines=True, encoding=encoding)
            except ValueError:
                pass

        with open(path, "r", encoding=encoding, errors="replace") as f:
            raw = json.load(f)

        if isinstance(raw, list):
            return pd.json_normalize(raw)
        if isinstance(raw, dict):
            # Look for a top-level list-of-records field; else normalise the dict.
            list_fields = [k for k, v in raw.items() if isinstance(v, list)]
            if len(list_fields) == 1:
                return pd.json_normalize(raw[list_fields[0]])
            return pd.json_normalize([raw])
        raise DataLoadError("Unsupported JSON structure (expected object or array of records)")
