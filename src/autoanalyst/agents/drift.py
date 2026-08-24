"""Schema, distribution, and statistical drift detection (PSI & KS-test)."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from autoanalyst.memory.run_store import RunRecord, numeric_stats

logger = logging.getLogger(__name__)

MISSING_SHIFT_PERCENT_POINTS = 10.0
MEAN_SIGMA_THRESHOLD = 2.0
PSI_MODERATE_DRIFT = 0.10
PSI_SIGNIFICANT_DRIFT = 0.25


def calculate_psi(expected: np.ndarray | pd.Series, actual: np.ndarray | pd.Series, num_buckets: int = 10) -> float:
    """Calculate Population Stability Index (PSI) between baseline and target distributions.

    Rules:
    - PSI < 0.10: Insignificant change
    - 0.10 <= PSI < 0.25: Moderate change / mild drift
    - PSI >= 0.25: Significant change / severe drift
    """
    exp_clean = np.asarray(expected, dtype=float)[~np.isnan(expected)]
    act_clean = np.asarray(actual, dtype=float)[~np.isnan(actual)]

    if len(exp_clean) < 10 or len(act_clean) < 10:
        return 0.0

    # Create quantiles on expected
    try:
        quantiles = np.linspace(0, 100, num_buckets + 1)
        bins = np.percentile(exp_clean, quantiles)
        bins[0] = -np.inf
        bins[-1] = np.inf

        # Ensure bins are strictly increasing
        bins = np.unique(bins)
        if len(bins) < 2:
            return 0.0

        exp_counts, _ = np.histogram(exp_clean, bins=bins)
        act_counts, _ = np.histogram(act_clean, bins=bins)

        # Proportions with Laplace smoothing to avoid log(0)
        eps = 1e-4
        exp_pct = (exp_counts + eps) / (len(exp_clean) + eps * len(exp_counts))
        act_pct = (act_counts + eps) / (len(act_clean) + eps * len(act_counts))

        psi_val = float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))
        return max(0.0, round(psi_val, 4))
    except Exception as exc:
        logger.warning("Could not compute PSI: %s", exc)
        return 0.0


def calculate_ks_test(expected: np.ndarray | pd.Series, actual: np.ndarray | pd.Series) -> tuple[float, float]:
    """Perform two-sample Kolmogorov-Smirnov test for distribution equality.

    Returns (ks_statistic, p_value). A small p-value (p < 0.05) indicates drift.
    """
    exp_clean = np.asarray(expected, dtype=float)[~np.isnan(expected)]
    act_clean = np.asarray(actual, dtype=float)[~np.isnan(actual)]

    if len(exp_clean) < 5 or len(act_clean) < 5:
        return 0.0, 1.0

    try:
        res = stats.ks_2samp(exp_clean, act_clean)
        return round(float(res.statistic), 4), round(float(res.pvalue), 4)
    except Exception:
        return 0.0, 1.0


def detect_drift(df: pd.DataFrame, reference: RunRecord, reference_df: pd.DataFrame | None = None) -> dict[str, Any]:
    """Compare the current DataFrame with a reference run's schema and distributions."""
    current_columns = [str(name) for name in df.columns]
    reference_columns = list(reference.column_names)

    added = sorted(set(current_columns) - set(reference_columns))
    removed = sorted(set(reference_columns) - set(current_columns))

    flagged: dict[str, list[str]] = {}
    current_stats = numeric_stats(df)

    for column, ref_stats in reference.numeric_stats.items():
        if column not in current_stats or column not in df.columns:
            continue
        notes: list[str] = []
        cur = current_stats[column]
        missing_shift = abs(cur["missing_percent"] - ref_stats["missing_percent"])
        if missing_shift >= MISSING_SHIFT_PERCENT_POINTS:
            notes.append(f"missing rate shifted {ref_stats['missing_percent']:.1f}% -> {cur['missing_percent']:.1f}%")
        if ref_stats["std"] > 0:
            shift_sigmas = abs(cur["mean"] - ref_stats["mean"]) / ref_stats["std"]
            if shift_sigmas >= MEAN_SIGMA_THRESHOLD:
                notes.append(f"mean shifted {shift_sigmas:.1f}sigma ({ref_stats['mean']:.3g} -> {cur['mean']:.3g})")

        # Advanced PSI and KS drift if reference DataFrame is provided
        if reference_df is not None and column in reference_df.columns:
            if pd.api.types.is_numeric_dtype(df[column]) and pd.api.types.is_numeric_dtype(reference_df[column]):
                psi = calculate_psi(reference_df[column], df[column])
                ks_stat, p_val = calculate_ks_test(reference_df[column], df[column])
                if psi >= PSI_SIGNIFICANT_DRIFT:
                    notes.append(f"significant statistical drift (PSI = {psi:.3f}, KS p = {p_val:.3e})")
                elif psi >= PSI_MODERATE_DRIFT:
                    notes.append(f"moderate statistical drift (PSI = {psi:.3f}, KS p = {p_val:.3e})")

        if notes:
            flagged[column] = notes

    clean = not added and not removed and not flagged
    return {
        "reference_run_id": reference.run_id,
        "reference_created_at": reference.created_at,
        "clean": clean,
        "added_columns": added,
        "removed_columns": removed,
        "flagged_columns": flagged,
    }


def drift_warnings(report: dict[str, Any]) -> list[str]:
    """Human-readable warning lines for a non-clean report."""
    if report.get("clean"):
        return []
    warnings = []
    if report.get("added_columns"):
        warnings.append(f"Drift: new columns detected: {', '.join(report['added_columns'])}.")
    if report.get("removed_columns"):
        warnings.append(f"Drift: columns no longer present: {', '.join(report['removed_columns'])}.")
    for column, notes in (report.get("flagged_columns") or {}).items():
        warnings.append(f"Drift in '{column}': " + "; ".join(notes) + ".")
    return warnings


__all__ = ["calculate_ks_test", "calculate_psi", "detect_drift", "drift_warnings"]
