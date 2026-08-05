"""Module 12 — Business Insights (natural-language summary generation)."""

from __future__ import annotations

import pandas as pd

from autoanalyst.profiling.column_profiler import ColumnProfile
from autoanalyst.profiling.duplicates import DuplicateReport
from autoanalyst.profiling.missing_analysis import MissingAnalysisResult
from autoanalyst.profiling.recommendations import FeatureRecommendations
from autoanalyst.profiling.understanding import DatasetUnderstanding
from autoanalyst.quality.quality import QualityReport
from autoanalyst.utils.helpers import get_logger

logger = get_logger(__name__)


class BusinessInsightGenerator:
    """Turns structured profiling results into a plain-English bullet list."""

    def generate(
        self,
        df: pd.DataFrame,
        understanding: DatasetUnderstanding,
        column_profiles: dict[str, ColumnProfile],
        quality_report: QualityReport,
        missing_result: MissingAnalysisResult,
        duplicate_report: DuplicateReport,
        recommendations: FeatureRecommendations,
    ) -> list[str]:
        insights: list[str] = []

        insights.append(
            f"The dataset contains {understanding.n_rows:,} records across {understanding.n_columns} columns."
        )
        insights.append(understanding.dataset_purpose_guess)

        if missing_result.total_missing_pct > 0:
            insights.append(f"{missing_result.total_missing_pct}% missing values detected overall.")
        else:
            insights.append("No missing values were detected — the dataset is fully complete.")

        if understanding.primary_key_candidate:
            insights.append(f"'{understanding.primary_key_candidate}' appears to be the primary key (unique, non-null identifier).")

        if understanding.target_candidates:
            insights.append(f"The likely target variable is '{understanding.target_candidates[0]}'.")

        if duplicate_report.duplicate_row_count > 0:
            insights.append(
                f"{duplicate_report.duplicate_row_count:,} duplicate row(s) found "
                f"({duplicate_report.duplicate_row_pct}% of the dataset)."
            )

        skewed = [
            name for name, p in column_profiles.items()
            if p.numeric_stats and p.numeric_stats.get("skewness") is not None
            and abs(p.numeric_stats["skewness"]) > 1
        ]
        if skewed:
            sample = ", ".join(f"'{s}'" for s in skewed[:3])
            insights.append(f"{sample} {'is' if len(skewed) == 1 else 'are'} highly skewed and may benefit from a log or power transform.")

        high_card = understanding.roles.high_cardinality
        if high_card:
            insights.append(f"{len(high_card)} column(s) show high cardinality: {', '.join(high_card[:3])}{'…' if len(high_card) > 3 else ''}.")

        if recommendations.potential_leakage:
            insights.append("Potential target leakage was flagged — review recommended feature list before modeling.")

        insights.append(
            f"Overall data quality score is {quality_report.overall_quality_score}/100 "
            f"(grade {quality_report.quality_grade})."
        )

        if understanding.is_likely_time_series:
            insights.append("The dataset shows characteristics of a time-series problem based on its datetime column(s).")

        if recommendations.columns_to_drop:
            insights.append(
                f"{len(recommendations.columns_to_drop)} column(s) are recommended for removal "
                f"(constant, duplicate, or mostly-missing)."
            )

        return insights
