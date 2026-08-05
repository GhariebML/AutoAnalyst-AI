"""Module 8 — Correlation Analysis (Pearson, Spearman, Kendall, Cramer's V,
multicollinearity / VIF)."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
import pandas as pd

from autoanalyst.utils.helpers import get_logger, safe_round

logger = get_logger(__name__)

HIGH_CORR_THRESHOLD = 0.8
MAX_CATEGORICAL_FOR_CRAMERS_V = 12  # cap cardinality to keep contingency tables sane
VIF_HIGH_THRESHOLD = 10.0


@dataclass
class CorrelationResult:
    pearson: dict | None
    spearman: dict | None
    kendall: dict | None
    cramers_v: dict | None
    highly_correlated_features: list[dict]
    multicollinear_features: list[dict]
    vif_scores: dict[str, float | None]

    def to_dict(self) -> dict:
        return {
            "pearson": self.pearson,
            "spearman": self.spearman,
            "kendall": self.kendall,
            "cramers_v": self.cramers_v,
            "highly_correlated_features": self.highly_correlated_features,
            "multicollinear_features": self.multicollinear_features,
            "vif_scores": self.vif_scores,
        }


class CorrelationAnalyzer:
    def analyze(self, df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]) -> CorrelationResult:
        pearson = spearman = kendall = None
        highly_correlated: list[dict] = []
        vif_scores: dict[str, float | None] = {}
        multicollinear: list[dict] = []

        if len(numeric_cols) >= 2:
            num_df = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
            pearson = self._matrix_to_dict(num_df.corr(method="pearson"))
            spearman = self._matrix_to_dict(num_df.corr(method="spearman"))
            kendall = self._matrix_to_dict(num_df.corr(method="kendall")) if len(num_df) <= 5000 else None
            highly_correlated = self._high_corr_pairs(num_df.corr(method="pearson"))
            vif_scores = self._compute_vif(num_df)
            multicollinear = [
                {"feature": f, "vif": v} for f, v in vif_scores.items()
                if v is not None and v >= VIF_HIGH_THRESHOLD
            ]

        cramers_v = None
        if len(categorical_cols) >= 2:
            cramers_v = self._cramers_v_matrix(df, categorical_cols)

        return CorrelationResult(
            pearson=pearson,
            spearman=spearman,
            kendall=kendall,
            cramers_v=cramers_v,
            highly_correlated_features=highly_correlated,
            multicollinear_features=multicollinear,
            vif_scores=vif_scores,
        )

    # -------------------------------------------------------------- impl --
    def _matrix_to_dict(self, matrix: pd.DataFrame) -> dict:
        return {
            col: {row: safe_round(matrix.loc[row, col], 4) for row in matrix.index}
            for col in matrix.columns
        }

    def _high_corr_pairs(self, matrix: pd.DataFrame) -> list[dict]:
        pairs = []
        for c1, c2 in combinations(matrix.columns, 2):
            value = matrix.loc[c1, c2]
            if pd.notna(value) and abs(value) >= HIGH_CORR_THRESHOLD:
                pairs.append({"feature_a": c1, "feature_b": c2, "correlation": safe_round(value, 4)})
        pairs.sort(key=lambda p: abs(p["correlation"]), reverse=True)
        return pairs

    def _compute_vif(self, num_df: pd.DataFrame) -> dict[str, float | None]:
        clean = num_df.dropna()
        scores: dict[str, float | None] = {c: None for c in num_df.columns}
        if clean.shape[0] < clean.shape[1] + 2 or clean.shape[1] < 2:
            return scores
        try:
            from sklearn.linear_model import LinearRegression

            X = clean.to_numpy(dtype=float)
            # Standardize to avoid scale-driven instability.
            X = (X - X.mean(axis=0)) / np.where(X.std(axis=0) == 0, 1, X.std(axis=0))
            for i, col in enumerate(clean.columns):
                y = X[:, i]
                others = np.delete(X, i, axis=1)
                if others.shape[1] == 0:
                    continue
                model = LinearRegression().fit(others, y)
                r2 = model.score(others, y)
                vif = float("inf") if r2 >= 0.9999 else 1.0 / (1.0 - r2)
                scores[col] = safe_round(vif, 3)
        except Exception as exc:  # noqa: BLE001
            logger.warning("VIF computation skipped: %s", exc)
        return scores

    def _cramers_v_matrix(self, df: pd.DataFrame, categorical_cols: list[str]) -> dict:
        cols = [
            c for c in categorical_cols
            if df[c].nunique(dropna=True) <= MAX_CATEGORICAL_FOR_CRAMERS_V and df[c].nunique(dropna=True) >= 2
        ][:15]  # cap total columns for performance
        if len(cols) < 2:
            return {}

        from scipy.stats import chi2_contingency

        result: dict[str, dict[str, float | None]] = {c: {} for c in cols}
        for c1, c2 in combinations(cols, 2):
            try:
                table = pd.crosstab(df[c1], df[c2])
                chi2, _, _, _ = chi2_contingency(table)
                n = table.sum().sum()
                phi2 = chi2 / n
                r, k = table.shape
                phi2_corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
                r_corr = r - ((r - 1) ** 2) / (n - 1)
                k_corr = k - ((k - 1) ** 2) / (n - 1)
                denom = min((k_corr - 1), (r_corr - 1))
                v = float(np.sqrt(phi2_corr / denom)) if denom > 0 else 0.0
            except Exception:  # noqa: BLE001
                v = None
            result[c1][c2] = safe_round(v, 4)
            result[c2][c1] = safe_round(v, 4)
        for c in cols:
            result[c][c] = 1.0
        return result
