"""Module 9 — Distribution Analysis (normality tests, distribution shape,
heavy-tail / zero-inflation detection)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

from autoanalyst.utils.helpers import get_logger, safe_round

logger = get_logger(__name__)

SHAPIRO_MAX_N = 5000  # Shapiro-Wilk is unreliable/slow far beyond this
ZERO_INFLATION_THRESHOLD = 0.3
HEAVY_TAIL_KURTOSIS_THRESHOLD = 3.0  # excess kurtosis


@dataclass
class ColumnDistribution:
    column: str
    is_normal_shapiro: bool | None
    shapiro_p_value: float | None
    anderson_statistic: float | None
    anderson_critical_5pct: float | None
    is_normal_anderson: bool | None
    qq_sample: dict | None
    distribution_type_guess: str
    is_heavy_tailed: bool
    is_zero_inflated: bool
    zero_ratio: float

    def to_dict(self) -> dict:
        return {
            "column": self.column,
            "is_normal_shapiro": self.is_normal_shapiro,
            "shapiro_p_value": self.shapiro_p_value,
            "anderson_statistic": self.anderson_statistic,
            "anderson_critical_5pct": self.anderson_critical_5pct,
            "is_normal_anderson": self.is_normal_anderson,
            "qq_sample": self.qq_sample,
            "distribution_type_guess": self.distribution_type_guess,
            "is_heavy_tailed": self.is_heavy_tailed,
            "is_zero_inflated": self.is_zero_inflated,
            "zero_ratio": self.zero_ratio,
        }


class DistributionAnalyzer:
    def analyze(self, df: pd.DataFrame, numeric_cols: list[str]) -> dict[str, ColumnDistribution]:
        results = {}
        for col in numeric_cols:
            try:
                results[col] = self._analyze_column(df[col])
            except Exception as exc:  # noqa: BLE001
                logger.warning("Distribution analysis failed for '%s': %s", col, exc)
        return results

    def _analyze_column(self, series: pd.Series) -> ColumnDistribution:
        values = pd.to_numeric(series, errors="coerce").dropna()
        col = series.name

        if len(values) < 8:
            return ColumnDistribution(
                column=col, is_normal_shapiro=None, shapiro_p_value=None,
                anderson_statistic=None, anderson_critical_5pct=None, is_normal_anderson=None,
                qq_sample=None, distribution_type_guess="insufficient_data",
                is_heavy_tailed=False, is_zero_inflated=False, zero_ratio=0.0,
            )

        # --- Shapiro-Wilk (sampled if large) ---
        sample = values if len(values) <= SHAPIRO_MAX_N else values.sample(SHAPIRO_MAX_N, random_state=42)
        try:
            shapiro_stat, shapiro_p = sp_stats.shapiro(sample)
            is_normal_shapiro = bool(shapiro_p > 0.05)
        except Exception:  # noqa: BLE001
            shapiro_p, is_normal_shapiro = None, None

        # --- Anderson-Darling ---
        try:
            anderson_res = sp_stats.anderson(values, dist="norm")
            crit_5pct = float(anderson_res.critical_values[2])  # index 2 ~= 5% significance
            is_normal_anderson = bool(anderson_res.statistic < crit_5pct)
        except Exception:  # noqa: BLE001
            anderson_res, crit_5pct, is_normal_anderson = None, None, None

        # --- QQ-plot sample data (theoretical vs sample quantiles) ---
        try:
            osm, osr = sp_stats.probplot(values, dist="norm", fit=False)
            step = max(1, len(osm) // 50)
            qq_sample = {
                "theoretical_quantiles": [safe_round(v) for v in osm[::step]],
                "sample_quantiles": [safe_round(v) for v in osr[::step]],
            }
        except Exception:  # noqa: BLE001
            qq_sample = None

        skew = float(values.skew())
        kurt = float(values.kurt())  # excess kurtosis (Fisher)
        zero_ratio = float((values == 0).mean())
        is_zero_inflated = zero_ratio >= ZERO_INFLATION_THRESHOLD
        is_heavy_tailed = kurt >= HEAVY_TAIL_KURTOSIS_THRESHOLD

        dist_guess = self._guess_distribution(skew, kurt, values, zero_ratio)

        return ColumnDistribution(
            column=col,
            is_normal_shapiro=is_normal_shapiro,
            shapiro_p_value=safe_round(shapiro_p, 5) if shapiro_p is not None else None,
            anderson_statistic=safe_round(anderson_res.statistic, 4) if anderson_res else None,
            anderson_critical_5pct=safe_round(crit_5pct, 4) if crit_5pct else None,
            is_normal_anderson=is_normal_anderson,
            qq_sample=qq_sample,
            distribution_type_guess=dist_guess,
            is_heavy_tailed=is_heavy_tailed,
            is_zero_inflated=is_zero_inflated,
            zero_ratio=safe_round(zero_ratio, 4),
        )

    def _guess_distribution(self, skew: float, kurt: float, values: pd.Series, zero_ratio: float) -> str:
        if zero_ratio >= ZERO_INFLATION_THRESHOLD:
            return "zero_inflated"
        if abs(skew) < 0.5 and abs(kurt) < 1:
            return "approximately_normal"
        if skew > 1:
            return "right_skewed (consider log/box-cox transform)"
        if skew < -1:
            return "left_skewed (consider reflection + transform)"
        if kurt >= HEAVY_TAIL_KURTOSIS_THRESHOLD:
            return "heavy_tailed / leptokurtic"
        if (values >= 0).all() and values.nunique() < 30:
            return "possibly_discrete_or_count_distribution"
        return "moderately_skewed"
