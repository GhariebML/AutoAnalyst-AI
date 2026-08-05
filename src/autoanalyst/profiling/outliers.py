"""Module 10 — Outlier Detection (IQR, Z-score, Modified Z-score,
Isolation Forest, Local Outlier Factor)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from autoanalyst.utils.helpers import get_logger, pct, safe_round

logger = get_logger(__name__)

Z_SCORE_THRESHOLD = 3.0
MODIFIED_Z_THRESHOLD = 3.5
MULTIVARIATE_MIN_ROWS = 20
MULTIVARIATE_MAX_ROWS = 50_000


@dataclass
class OutlierReport:
    per_column: dict[str, dict]
    multivariate: dict | None
    total_affected_columns: list[str]

    def to_dict(self) -> dict:
        return {
            "per_column": self.per_column,
            "multivariate": self.multivariate,
            "total_affected_columns": self.total_affected_columns,
        }


class OutlierDetector:
    def detect(self, df: pd.DataFrame, numeric_cols: list[str]) -> OutlierReport:
        per_column = {}
        affected = []

        for col in numeric_cols:
            result = self._univariate(df[col])
            if result is None:
                continue
            per_column[col] = result
            if result["iqr"]["count"] > 0 or result["z_score"]["count"] > 0:
                affected.append(col)

        multivariate = self._multivariate(df, numeric_cols) if len(numeric_cols) >= 2 else None

        return OutlierReport(per_column=per_column, multivariate=multivariate, total_affected_columns=affected)

    # -------------------------------------------------------------- impl --
    def _univariate(self, series: pd.Series) -> dict | None:
        values = pd.to_numeric(series, errors="coerce").dropna()
        n = len(values)
        if n < 4:
            return None

        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        iqr_outliers = values[(values < lower) | (values > upper)]

        std = values.std()
        mean = values.mean()
        if std and std > 0:
            z_scores = (values - mean) / std
            z_outliers = values[z_scores.abs() > Z_SCORE_THRESHOLD]
        else:
            z_outliers = pd.Series(dtype=float)

        median = values.median()
        mad = (values - median).abs().median()
        if mad and mad > 0:
            modified_z = 0.6745 * (values - median) / mad
            modz_outliers = values[modified_z.abs() > MODIFIED_Z_THRESHOLD]
        else:
            modz_outliers = pd.Series(dtype=float)

        return {
            "iqr": {
                "count": int(len(iqr_outliers)),
                "pct": pct(len(iqr_outliers), n),
                "bounds": {"lower": safe_round(lower), "upper": safe_round(upper)},
            },
            "z_score": {
                "count": int(len(z_outliers)),
                "pct": pct(len(z_outliers), n),
                "threshold": Z_SCORE_THRESHOLD,
            },
            "modified_z_score": {
                "count": int(len(modz_outliers)),
                "pct": pct(len(modz_outliers), n),
                "threshold": MODIFIED_Z_THRESHOLD,
            },
        }

    def _multivariate(self, df: pd.DataFrame, numeric_cols: list[str]) -> dict | None:
        num_df = df[numeric_cols].apply(pd.to_numeric, errors="coerce").dropna()
        n = len(num_df)
        if n < MULTIVARIATE_MIN_ROWS:
            return {"note": f"Not enough complete numeric rows ({n}) for multivariate outlier detection."}
        if n > MULTIVARIATE_MAX_ROWS:
            num_df = num_df.sample(MULTIVARIATE_MAX_ROWS, random_state=42)
            n = MULTIVARIATE_MAX_ROWS

        result: dict = {"rows_analyzed": n}
        try:
            from sklearn.ensemble import IsolationForest

            iso = IsolationForest(contamination="auto", random_state=42, n_estimators=200)
            preds = iso.fit_predict(num_df.to_numpy())
            n_out = int((preds == -1).sum())
            result["isolation_forest"] = {"outlier_count": n_out, "outlier_pct": pct(n_out, n)}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Isolation Forest skipped: %s", exc)
            result["isolation_forest"] = None

        try:
            from sklearn.neighbors import LocalOutlierFactor

            n_neighbors = min(20, max(2, n - 1))
            lof = LocalOutlierFactor(n_neighbors=n_neighbors)
            preds = lof.fit_predict(num_df.to_numpy())
            n_out = int((preds == -1).sum())
            result["local_outlier_factor"] = {"outlier_count": n_out, "outlier_pct": pct(n_out, n)}
        except Exception as exc:  # noqa: BLE001
            logger.warning("LOF skipped: %s", exc)
            result["local_outlier_factor"] = None

        return result
