"""Module 5 — Missing Values Analysis.

Heuristic classification of missingness mechanism (MCAR / MAR / MNAR),
missing-pattern and missing-correlation detection, and per-column
imputation-strategy suggestions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from autoanalyst.utils.helpers import get_logger, pct, safe_round

logger = get_logger(__name__)

MISSING_CORR_THRESHOLD = 0.5


@dataclass
class MissingAnalysisResult:
    total_missing_cells: int
    total_missing_pct: float
    columns_with_missing: dict[str, float]
    missing_mechanism_guess: str
    mechanism_explanation: str
    missing_correlations: list[dict]
    row_missing_heatmap_sample: list[list[int]]
    suggestions: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "total_missing_cells": self.total_missing_cells,
            "total_missing_pct": self.total_missing_pct,
            "columns_with_missing": self.columns_with_missing,
            "missing_mechanism_guess": self.missing_mechanism_guess,
            "mechanism_explanation": self.mechanism_explanation,
            "missing_correlations": self.missing_correlations,
            "row_missing_heatmap_sample": self.row_missing_heatmap_sample,
            "suggestions": self.suggestions,
        }


class MissingValueAnalyzer:
    def analyze(self, df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]) -> MissingAnalysisResult:
        n_rows, n_cols = df.shape
        total_cells = n_rows * n_cols
        missing_mask = df.isna()
        total_missing = int(missing_mask.sum().sum())

        col_missing_pct = {
            col: pct(int(missing_mask[col].sum()), n_rows)
            for col in df.columns if missing_mask[col].any()
        }

        correlations = self._missing_correlations(missing_mask)
        mechanism, explanation = self._guess_mechanism(df, missing_mask, correlations, numeric_cols)
        heatmap_sample = missing_mask.head(50).astype(int).values.tolist()
        suggestions = self._suggest_strategies(df, col_missing_pct, numeric_cols, categorical_cols)

        return MissingAnalysisResult(
            total_missing_cells=total_missing,
            total_missing_pct=pct(total_missing, total_cells),
            columns_with_missing=col_missing_pct,
            missing_mechanism_guess=mechanism,
            mechanism_explanation=explanation,
            missing_correlations=correlations,
            row_missing_heatmap_sample=heatmap_sample,
            suggestions=suggestions,
        )

    # -------------------------------------------------------------- impl --
    def _missing_correlations(self, missing_mask: pd.DataFrame) -> list[dict]:
        cols_with_missing = [c for c in missing_mask.columns if missing_mask[c].any() and missing_mask[c].sum() < len(missing_mask)]
        if len(cols_with_missing) < 2:
            return []
        try:
            corr = missing_mask[cols_with_missing].astype(int).corr()
        except Exception:  # noqa: BLE001
            return []

        pairs = []
        seen = set()
        for c1 in corr.columns:
            for c2 in corr.columns:
                if c1 == c2 or (c2, c1) in seen:
                    continue
                seen.add((c1, c2))
                value = corr.loc[c1, c2]
                if pd.notna(value) and abs(value) >= MISSING_CORR_THRESHOLD:
                    pairs.append({"column_a": c1, "column_b": c2, "correlation": safe_round(value, 3)})
        pairs.sort(key=lambda p: abs(p["correlation"]), reverse=True)
        return pairs[:20]

    def _guess_mechanism(self, df: pd.DataFrame, missing_mask: pd.DataFrame, correlations: list[dict], numeric_cols: list[str]) -> tuple[str, str]:
        if missing_mask.sum().sum() == 0:
            return "NONE", "No missing values were detected in this dataset."

        if correlations:
            return (
                "MAR",
                "Missingness in some columns correlates with missingness in others, "
                "suggesting values are Missing At Random conditional on other observed "
                "fields (heuristic, not statistically confirmed).",
            )

        # Check whether missingness in any column correlates with the *values*
        # of other numeric columns (a classic MNAR/MAR signal).
        cols_with_missing = [c for c in missing_mask.columns if missing_mask[c].any()]
        for target_col in cols_with_missing:
            for num_col in numeric_cols:
                if num_col == target_col or df[num_col].dropna().empty:
                    continue
                try:
                    ind = missing_mask[target_col].astype(int)
                    aligned = df[num_col]
                    valid = aligned.notna()
                    if valid.sum() < 10 or ind[valid].nunique() < 2:
                        continue
                    corr_val = np.corrcoef(ind[valid], aligned[valid])[0, 1]
                    if abs(corr_val) >= MISSING_CORR_THRESHOLD:
                        return (
                            "MAR",
                            f"Missingness in '{target_col}' correlates with observed values in "
                            f"'{num_col}' (heuristic signal of Missing At Random).",
                        )
                except Exception:  # noqa: BLE001
                    continue

        return (
            "MCAR_OR_MNAR",
            "No strong correlation was found between missingness and other observed columns. "
            "This is consistent with Missing Completely At Random (MCAR), but could also be "
            "Missing Not At Random (MNAR) if missingness depends on the unobserved value itself "
            "— which cannot be verified from the data alone.",
        )

    def _suggest_strategies(self, df: pd.DataFrame, col_missing_pct: dict[str, float], numeric_cols: list[str], categorical_cols: list[str]) -> dict[str, str]:
        suggestions = {}
        for col, pct_missing in col_missing_pct.items():
            if pct_missing > 60:
                suggestions[col] = "drop_column (missingness too high to reliably impute)"
            elif pct_missing == 0:
                continue
            elif col in numeric_cols:
                suggestions[col] = "median_imputation (or KNN/MICE if missingness correlates with other features)"
            elif col in categorical_cols:
                suggestions[col] = "mode_imputation (or a dedicated 'Missing' category if informative)"
            else:
                suggestions[col] = "forward_fill / interpolation if temporally ordered, else mode imputation"
        return suggestions
