"""Module 6 — Duplicate Detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
import pandas as pd

from autoanalyst.utils.helpers import get_logger, pct, safe_round

logger = get_logger(__name__)

NEAR_DUPLICATE_MISMATCH_TOLERANCE = 0.05  # <=5% of columns differ
HIGH_CORR_DUPLICATE_THRESHOLD = 0.98
MAX_ROWS_FOR_NEAR_DUP_SCAN = 20_000


@dataclass
class DuplicateReport:
    duplicate_row_count: int
    duplicate_row_pct: float
    near_duplicate_row_count: int
    duplicate_columns: list[list[str]]
    constant_columns: list[str]
    redundant_columns: list[str]
    highly_correlated_pairs: list[dict]

    def to_dict(self) -> dict:
        return {
            "duplicate_row_count": self.duplicate_row_count,
            "duplicate_row_pct": self.duplicate_row_pct,
            "near_duplicate_row_count": self.near_duplicate_row_count,
            "duplicate_columns": self.duplicate_columns,
            "constant_columns": self.constant_columns,
            "redundant_columns": self.redundant_columns,
            "highly_correlated_pairs": self.highly_correlated_pairs,
        }


class DuplicateDetector:
    def detect(self, df: pd.DataFrame, numeric_cols: list[str], constant_cols: list[str]) -> DuplicateReport:
        n = len(df)

        dup_mask = df.duplicated(keep="first")
        duplicate_rows = int(dup_mask.sum())

        near_dup_count = self._near_duplicate_count(df) if n <= MAX_ROWS_FOR_NEAR_DUP_SCAN else 0

        duplicate_columns = self._duplicate_columns(df)
        redundant = sorted({c for group in duplicate_columns for c in group[1:]})

        high_corr_pairs = self._highly_correlated_pairs(df, numeric_cols)

        return DuplicateReport(
            duplicate_row_count=duplicate_rows,
            duplicate_row_pct=pct(duplicate_rows, n),
            near_duplicate_row_count=near_dup_count,
            duplicate_columns=duplicate_columns,
            constant_columns=constant_cols,
            redundant_columns=redundant,
            highly_correlated_pairs=high_corr_pairs,
        )

    # -------------------------------------------------------------- impl --
    def _near_duplicate_count(self, df: pd.DataFrame) -> int:
        """Count rows that differ from another row in <= tolerance fraction
        of columns. O(n^2) — only run on reasonably small datasets."""
        n, n_cols = df.shape
        if n_cols == 0 or n < 2:
            return 0
        max_mismatch = max(1, int(n_cols * NEAR_DUPLICATE_MISMATCH_TOLERANCE))

        # Compare against exact-duplicate-collapsed representation for speed.
        sample = df
        if n > 3000:
            sample = df.sample(3000, random_state=42)

        values = sample.astype(str).to_numpy()
        near_dupes = 0
        seen_pairs = 0
        max_pairs = 500_000  # safety cap
        rows = len(values)
        for i in range(rows):
            for j in range(i + 1, rows):
                seen_pairs += 1
                if seen_pairs > max_pairs:
                    return near_dupes
                mismatches = np.sum(values[i] != values[j])
                if 0 < mismatches <= max_mismatch:
                    near_dupes += 1
                    break
        return near_dupes

    def _duplicate_columns(self, df: pd.DataFrame) -> list[list[str]]:
        groups: dict[tuple, list[str]] = {}
        for col in df.columns:
            try:
                key = tuple(df[col].fillna("__NA__").astype(str))
            except Exception:  # noqa: BLE001
                continue
            groups.setdefault(key, []).append(col)
        return [cols for cols in groups.values() if len(cols) > 1]

    def _highly_correlated_pairs(self, df: pd.DataFrame, numeric_cols: list[str]) -> list[dict]:
        if len(numeric_cols) < 2:
            return []
        try:
            corr = df[numeric_cols].corr(method="pearson", numeric_only=True)
        except Exception:  # noqa: BLE001
            return []

        pairs = []
        for c1, c2 in combinations(corr.columns, 2):
            value = corr.loc[c1, c2]
            if pd.notna(value) and abs(value) >= HIGH_CORR_DUPLICATE_THRESHOLD:
                pairs.append({"column_a": c1, "column_b": c2, "correlation": safe_round(value, 4)})
        pairs.sort(key=lambda p: abs(p["correlation"]), reverse=True)
        return pairs
