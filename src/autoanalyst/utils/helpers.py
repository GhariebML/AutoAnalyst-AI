"""Shared utilities: logging setup, safe-math helpers, JSON-safe casting."""

from __future__ import annotations

import logging
import math
import sys
from typing import Any

import numpy as np
import pandas as pd

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a configured module-level logger (idempotent)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger


def safe_round(value: Any, ndigits: int = 4) -> Any:
    """Round a numeric value, passing through None/NaN/inf untouched -> None."""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, ndigits)


def json_safe(value: Any) -> Any:
    """Recursively convert numpy/pandas types into plain JSON-serialisable
    Python types. Handles nested dict/list structures."""
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        f = float(value)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, pd.Timedelta):
        return str(value)
    if isinstance(value, float):
        return None if (math.isnan(value) or math.isinf(value)) else value
    if isinstance(value, (np.datetime64,)):
        return pd.Timestamp(value).isoformat()
    return value


def pct(numerator: float, denominator: float, ndigits: int = 2) -> float:
    """Safe percentage calculation, returns 0.0 on zero-division."""
    if not denominator:
        return 0.0
    return round((numerator / denominator) * 100, ndigits)


def entropy(series: pd.Series) -> float | None:
    """Shannon entropy (base 2) of a categorical/discrete series' value
    distribution. Returns None if the series is empty."""
    counts = series.value_counts(dropna=True)
    total = counts.sum()
    if total == 0:
        return None
    probs = counts / total
    return float(-(probs * np.log2(probs)).sum())


def is_effectively_numeric_object(series: pd.Series, sample_size: int = 500) -> bool:
    """Heuristic: does an `object` dtype column actually hold numbers stored
    as strings (e.g. "1,234", "45.6", "$100")?"""
    sample = series.dropna().astype(str).head(sample_size)
    if sample.empty:
        return False
    cleaned = sample.str.replace(r"[,$%\s]", "", regex=True)
    numeric_like = pd.to_numeric(cleaned, errors="coerce")
    return numeric_like.notna().mean() >= 0.9


def is_effectively_boolean(series: pd.Series) -> bool:
    """Heuristic boolean detection across common encodings."""
    bool_sets = [
        {True, False},
        {0, 1},
        {"true", "false"},
        {"yes", "no"},
        {"y", "n"},
        {"t", "f"},
        {"1", "0"},
    ]
    uniques = set(
        str(v).strip().lower() if not isinstance(v, bool) else v
        for v in series.dropna().unique()
    )
    if not uniques or len(uniques) > 2:
        return False
    return any(uniques.issubset(bs) or uniques == bs for bs in bool_sets)


def is_effectively_datetime(series: pd.Series, sample_size: int = 200, threshold: float = 0.85) -> bool:
    """Heuristic datetime detection for object/string columns."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if not pd.api.types.is_object_dtype(series) and not pd.api.types.is_string_dtype(series):
        return False
    sample = series.dropna().astype(str).head(sample_size)
    if sample.empty:
        return False
    try:
        parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
    except (ValueError, TypeError):
        parsed = pd.to_datetime(sample, errors="coerce")
    return parsed.notna().mean() >= threshold


def chunker(total: int, chunk_size: int):
    """Yield (start, end) index pairs for chunked processing."""
    start = 0
    while start < total:
        end = min(start + chunk_size, total)
        yield start, end
        start = end
