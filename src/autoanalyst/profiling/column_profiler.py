"""Module 4 — Complete Data Profiling (per-column statistics)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

from autoanalyst.profiling.understanding import ColumnRoles
from autoanalyst.utils.helpers import entropy, get_logger, pct, safe_round

logger = get_logger(__name__)

_SPECIAL_CHAR_RE = re.compile(r"[^A-Za-z0-9\s]")


def _role_of(col: str, roles: ColumnRoles) -> str:
    if col in roles.boolean:
        return "boolean"
    if col in roles.datetime:
        return "datetime"
    if col in roles.numeric:
        return "numeric"
    if col in roles.text:
        return "text"
    return "categorical"


@dataclass
class ColumnProfile:
    name: str
    role: str
    dtype: str
    memory_usage_bytes: int
    missing_count: int
    missing_pct: float
    unique_count: int
    unique_pct: float
    duplicate_ratio: float
    mode: Any
    mode_frequency: int | None
    entropy_bits: float | None
    cardinality: int
    is_constant: bool
    numeric_stats: dict | None = field(default=None)
    categorical_stats: dict | None = field(default=None)
    datetime_stats: dict | None = field(default=None)
    text_stats: dict | None = field(default=None)

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "role": self.role,
            "dtype": self.dtype,
            "memory_usage_bytes": self.memory_usage_bytes,
            "missing_count": self.missing_count,
            "missing_pct": self.missing_pct,
            "unique_count": self.unique_count,
            "unique_pct": self.unique_pct,
            "duplicate_ratio": self.duplicate_ratio,
            "mode": self.mode,
            "mode_frequency": self.mode_frequency,
            "entropy_bits": self.entropy_bits,
            "cardinality": self.cardinality,
            "is_constant": self.is_constant,
        }
        if self.numeric_stats:
            d["numeric_stats"] = self.numeric_stats
        if self.categorical_stats:
            d["categorical_stats"] = self.categorical_stats
        if self.datetime_stats:
            d["datetime_stats"] = self.datetime_stats
        if self.text_stats:
            d["text_stats"] = self.text_stats
        return d


class ColumnProfiler:
    """Computes a rich statistical profile for every column in a DataFrame."""

    def profile_all(self, df: pd.DataFrame, roles: ColumnRoles) -> dict[str, ColumnProfile]:
        profiles: dict[str, ColumnProfile] = {}
        for col in df.columns:
            try:
                profiles[col] = self.profile_column(df, col, roles)
            except Exception as exc:  # noqa: BLE001 - one bad column shouldn't kill the run
                logger.warning("Failed to profile column '%s': %s", col, exc)
                profiles[col] = self._fallback_profile(df, col)
        return profiles

    def profile_column(self, df: pd.DataFrame, col: str, roles: ColumnRoles) -> ColumnProfile:
        series = df[col]
        n = len(series)
        role = _role_of(col, roles)

        missing_count = int(series.isna().sum())
        non_null = series.dropna()
        unique_count = int(non_null.nunique())
        mode_series = non_null.mode()
        mode_val = mode_series.iloc[0] if not mode_series.empty else None
        mode_freq = int((non_null == mode_val).sum()) if mode_val is not None and not non_null.empty else None

        profile = ColumnProfile(
            name=col,
            role=role,
            dtype=str(series.dtype),
            memory_usage_bytes=int(series.memory_usage(deep=True)),
            missing_count=missing_count,
            missing_pct=pct(missing_count, n),
            unique_count=unique_count,
            unique_pct=pct(unique_count, n),
            duplicate_ratio=safe_round(1 - (unique_count / n), 4) if n else 0.0,
            mode=self._safe_scalar(mode_val),
            mode_frequency=mode_freq,
            entropy_bits=safe_round(entropy(non_null), 4) if role in ("categorical", "boolean") else None,
            cardinality=unique_count,
            is_constant=unique_count <= 1,
        )

        if role == "numeric":
            profile.numeric_stats = self._numeric_stats(series)
        elif role == "datetime":
            profile.datetime_stats = self._datetime_stats(series)
        elif role == "text":
            profile.text_stats = self._text_stats(series)
        else:
            profile.categorical_stats = self._categorical_stats(series)

        return profile

    # -------------------------------------------------------- type stats --
    def _numeric_stats(self, series: pd.Series) -> dict:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            return {"note": "no valid numeric values"}

        q1, q2, q3 = numeric.quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        mad = float((numeric - numeric.median()).abs().median())
        percentiles = {
            f"p{p}": safe_round(numeric.quantile(p / 100), 4)
            for p in (1, 5, 10, 25, 50, 75, 90, 95, 99)
        }
        skew = float(numeric.skew()) if len(numeric) > 2 else None
        kurt = float(numeric.kurt()) if len(numeric) > 2 else None

        return {
            "min": safe_round(numeric.min()),
            "max": safe_round(numeric.max()),
            "mean": safe_round(numeric.mean()),
            "median": safe_round(q2),
            "variance": safe_round(numeric.var()),
            "std": safe_round(numeric.std()),
            "mad": safe_round(mad),
            "iqr": safe_round(iqr),
            "skewness": safe_round(skew),
            "kurtosis": safe_round(kurt),
            "percentiles": percentiles,
            "zeros_count": int((numeric == 0).sum()),
            "negative_count": int((numeric < 0).sum()),
            "sum": safe_round(numeric.sum()),
        }

    def _categorical_stats(self, series: pd.Series) -> dict:
        non_null = series.dropna()
        n = len(non_null)
        if n == 0:
            return {"note": "no valid categorical values"}

        value_counts = non_null.astype(str).value_counts()
        top_values = [
            {"value": v, "count": int(c), "pct": pct(c, n)}
            for v, c in value_counts.head(10).items()
        ]
        rare_threshold = max(1, int(n * 0.01))
        rare_categories = value_counts[value_counts <= rare_threshold].index.tolist()

        # Imbalance score: ratio of most-frequent to least-frequent among
        # observed categories (higher => more imbalanced). Capped for sanity.
        if len(value_counts) > 1:
            imbalance = float(value_counts.iloc[0] / max(value_counts.iloc[-1], 1))
        else:
            imbalance = None

        return {
            "top_values": top_values,
            "frequency_table_size": int(len(value_counts)),
            "rare_categories_count": len(rare_categories),
            "rare_categories_sample": rare_categories[:10],
            "imbalance_score": safe_round(imbalance, 2),
        }

    def _datetime_stats(self, series: pd.Series) -> dict:
        if pd.api.types.is_datetime64_any_dtype(series):
            dt = series.dropna()
        else:
            dt = pd.to_datetime(series, errors="coerce", format="mixed").dropna()
        if dt.empty:
            return {"note": "no valid datetime values"}

        span = dt.max() - dt.min()
        full_range = pd.date_range(start=dt.min(), end=dt.max(), freq="D") if span.days > 0 else None
        missing_dates = None
        if full_range is not None and len(full_range) > 0:
            present_dates = pd.to_datetime(dt.dt.date.unique())
            missing_dates = int(len(full_range) - len(present_dates))

        return {
            "min_date": dt.min().isoformat(),
            "max_date": dt.max().isoformat(),
            "date_span_days": int(span.days),
            "missing_dates_in_range": missing_dates,
            "weekday_distribution": {
                str(k): int(v) for k, v in dt.dt.day_name().value_counts().items()
            },
        }

    def _text_stats(self, series: pd.Series) -> dict:
        non_null = series.dropna().astype(str)
        if non_null.empty:
            return {"note": "no valid text values"}

        lengths = non_null.str.len()
        special_char_ratio = non_null.apply(
            lambda s: len(_SPECIAL_CHAR_RE.findall(s)) / max(len(s), 1)
        ).mean()
        avg_word_count = non_null.str.split().apply(len).mean()

        return {
            "avg_length": safe_round(lengths.mean(), 2),
            "min_length": int(lengths.min()),
            "max_length": int(lengths.max()),
            "avg_word_count": safe_round(avg_word_count, 2),
            "special_char_ratio": safe_round(special_char_ratio, 4),
            "language_detection": "not_available (install a language-detection library for this feature)",
        }

    def _safe_scalar(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (pd.Timestamp,)):
            return value.isoformat()
        if isinstance(value, (np.generic,)):
            return value.item()
        return value

    def _fallback_profile(self, df: pd.DataFrame, col: str) -> ColumnProfile:
        series = df[col]
        n = len(series)
        missing = int(series.isna().sum())
        return ColumnProfile(
            name=col,
            role="unknown",
            dtype=str(series.dtype),
            memory_usage_bytes=int(series.memory_usage(deep=True)),
            missing_count=missing,
            missing_pct=pct(missing, n),
            unique_count=0,
            unique_pct=0.0,
            duplicate_ratio=0.0,
            mode=None,
            mode_frequency=None,
            entropy_bits=None,
            cardinality=0,
            is_constant=False,
        )
