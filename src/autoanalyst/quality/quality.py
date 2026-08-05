"""Module 7 — Data Quality Assessment.

Combines validation, profiling, and duplicate-detection signals into a set
of 0-100 quality sub-scores plus an overall grade.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from autoanalyst.profiling.column_profiler import ColumnProfile
from autoanalyst.profiling.duplicates import DuplicateReport
from autoanalyst.utils.helpers import get_logger, safe_round
from autoanalyst.validation.validator import ValidationReport

logger = get_logger(__name__)


def _grade_from_score(score: float) -> str:
    if score >= 97:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


@dataclass
class QualityReport:
    completeness_score: float
    consistency_score: float
    validity_score: float
    uniqueness_score: float
    accuracy_heuristic_score: float
    integrity_score: float
    overall_quality_score: float
    quality_grade: str
    sub_score_details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "completeness_score": self.completeness_score,
            "consistency_score": self.consistency_score,
            "validity_score": self.validity_score,
            "uniqueness_score": self.uniqueness_score,
            "accuracy_heuristic_score": self.accuracy_heuristic_score,
            "integrity_score": self.integrity_score,
            "overall_quality_score": self.overall_quality_score,
            "quality_grade": self.quality_grade,
            "sub_score_details": self.sub_score_details,
        }


class DataQualityAssessor:
    """Weighted composite of completeness, consistency, validity,
    uniqueness, accuracy-heuristic, and integrity."""

    WEIGHTS = {
        "completeness": 0.25,
        "consistency": 0.15,
        "validity": 0.15,
        "uniqueness": 0.20,
        "accuracy": 0.10,
        "integrity": 0.15,
    }

    def assess(
        self,
        df: pd.DataFrame,
        validation_report: ValidationReport,
        column_profiles: dict[str, ColumnProfile],
        duplicate_report: DuplicateReport,
    ) -> QualityReport:
        completeness = self._completeness_score(df)
        consistency = self._consistency_score(validation_report, df)
        validity = self._validity_score(validation_report, df)
        uniqueness = self._uniqueness_score(df, duplicate_report)
        accuracy = self._accuracy_heuristic_score(column_profiles)
        integrity = self._integrity_score(df, duplicate_report)

        overall = (
            completeness * self.WEIGHTS["completeness"]
            + consistency * self.WEIGHTS["consistency"]
            + validity * self.WEIGHTS["validity"]
            + uniqueness * self.WEIGHTS["uniqueness"]
            + accuracy * self.WEIGHTS["accuracy"]
            + integrity * self.WEIGHTS["integrity"]
        )
        overall = round(overall, 2)

        return QualityReport(
            completeness_score=completeness,
            consistency_score=consistency,
            validity_score=validity,
            uniqueness_score=uniqueness,
            accuracy_heuristic_score=accuracy,
            integrity_score=integrity,
            overall_quality_score=overall,
            quality_grade=_grade_from_score(overall),
            sub_score_details={"weights": self.WEIGHTS},
        )

    # -------------------------------------------------------------- subs --
    def _completeness_score(self, df: pd.DataFrame) -> float:
        total_cells = df.shape[0] * df.shape[1]
        if total_cells == 0:
            return 0.0
        missing = df.isna().sum().sum()
        return safe_round(max(0.0, 100.0 * (1 - missing / total_cells)), 2)

    def _consistency_score(self, validation_report: ValidationReport, df: pd.DataFrame) -> float:
        # Penalize mixed types, encoding issues, duplicate/unsupported names
        # (all captured as validation warnings/errors).
        penalty = min(60, len(validation_report.warnings) * 4 + len(validation_report.errors) * 15)
        return safe_round(max(0.0, 100.0 - penalty), 2)

    def _validity_score(self, validation_report: ValidationReport, df: pd.DataFrame) -> float:
        penalty = min(70, len(validation_report.errors) * 20)
        # Small extra penalty for structural warnings tied to validity (headers, infinities).
        validity_related = [w for w in validation_report.warnings if any(
            k in w.lower() for k in ("infinite", "header", "duplicate column"))]
        penalty += min(20, len(validity_related) * 5)
        return safe_round(max(0.0, 100.0 - penalty), 2)

    def _uniqueness_score(self, df: pd.DataFrame, duplicate_report: DuplicateReport) -> float:
        row_penalty = min(60, duplicate_report.duplicate_row_pct * 0.6)
        col_penalty = min(30, len(duplicate_report.redundant_columns) * 8)
        return safe_round(max(0.0, 100.0 - row_penalty - col_penalty), 2)

    def _accuracy_heuristic_score(self, column_profiles: dict[str, ColumnProfile]) -> float:
        """No ground truth exists, so this is a heuristic based on internal
        plausibility signals: extreme skew/kurtosis, implausible cardinality,
        columns that are entirely one repeated value, etc."""
        if not column_profiles:
            return 100.0
        penalty = 0.0
        n_cols = len(column_profiles)
        for profile in column_profiles.values():
            if profile.is_constant:
                penalty += 3
            stats = profile.numeric_stats
            if stats and stats.get("skewness") is not None and abs(stats["skewness"]) > 5:
                penalty += 2
            if stats and stats.get("kurtosis") is not None and abs(stats["kurtosis"]) > 20:
                penalty += 2
        score = 100.0 - min(70.0, (penalty / max(1, n_cols)) * 25)
        return safe_round(max(0.0, score), 2)

    def _integrity_score(self, df: pd.DataFrame, duplicate_report: DuplicateReport) -> float:
        penalty = 0.0
        penalty += min(30, len(duplicate_report.duplicate_columns) * 10)
        penalty += min(30, len(duplicate_report.highly_correlated_pairs) * 5)
        return safe_round(max(0.0, 100.0 - penalty), 2)
