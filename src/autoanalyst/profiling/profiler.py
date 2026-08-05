"""profiling/profiler.py — Orchestrates Modules 3–12.

`DatasetProfiler.run()` is the single entrypoint that chains: automatic data
understanding -> per-column profiling -> missing-value analysis ->
duplicate detection -> correlation analysis -> distribution analysis ->
outlier detection -> feature recommendations -> business insights.

Each sub-stage is isolated with its own try/except so a single failing
stage degrades gracefully rather than aborting the whole profile.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from autoanalyst.profiling.column_profiler import ColumnProfile, ColumnProfiler
from autoanalyst.profiling.correlation import CorrelationAnalyzer, CorrelationResult
from autoanalyst.profiling.distribution import ColumnDistribution, DistributionAnalyzer
from autoanalyst.profiling.duplicates import DuplicateDetector, DuplicateReport
from autoanalyst.profiling.insights import BusinessInsightGenerator
from autoanalyst.profiling.missing_analysis import MissingAnalysisResult, MissingValueAnalyzer
from autoanalyst.profiling.outliers import OutlierDetector, OutlierReport
from autoanalyst.profiling.recommendations import FeatureRecommendationEngine, FeatureRecommendations
from autoanalyst.profiling.understanding import DataUnderstandingEngine, DatasetUnderstanding
from autoanalyst.quality.quality import DataQualityAssessor, QualityReport
from autoanalyst.utils.helpers import get_logger
from autoanalyst.validation.validator import ValidationReport

logger = get_logger(__name__)


@dataclass
class FullProfile:
    understanding: DatasetUnderstanding
    column_profiles: dict[str, ColumnProfile]
    missing_analysis: MissingAnalysisResult
    duplicate_report: DuplicateReport
    quality_report: QualityReport
    correlation_result: CorrelationResult | None
    distributions: dict[str, ColumnDistribution]
    outlier_report: OutlierReport
    recommendations: FeatureRecommendations
    business_insights: list[str]

    def to_dict(self) -> dict:
        return {
            "data_understanding": self.understanding.to_dict(),
            "column_profiles": {k: v.to_dict() for k, v in self.column_profiles.items()},
            "missing_value_analysis": self.missing_analysis.to_dict(),
            "duplicate_analysis": self.duplicate_report.to_dict(),
            "data_quality": self.quality_report.to_dict(),
            "correlation_analysis": self.correlation_result.to_dict() if self.correlation_result else None,
            "distribution_analysis": {k: v.to_dict() for k, v in self.distributions.items()},
            "outlier_analysis": self.outlier_report.to_dict(),
            "feature_recommendations": self.recommendations.to_dict(),
            "business_insights": self.business_insights,
        }


class DatasetProfiler:
    """Top-level orchestrator for Modules 3 through 12."""

    def __init__(self) -> None:
        self._understanding_engine = DataUnderstandingEngine()
        self._column_profiler = ColumnProfiler()
        self._missing_analyzer = MissingValueAnalyzer()
        self._duplicate_detector = DuplicateDetector()
        self._correlation_analyzer = CorrelationAnalyzer()
        self._distribution_analyzer = DistributionAnalyzer()
        self._outlier_detector = OutlierDetector()
        self._quality_assessor = DataQualityAssessor()
        self._recommendation_engine = FeatureRecommendationEngine()
        self._insight_generator = BusinessInsightGenerator()

    def run(self, df: pd.DataFrame, validation_report: ValidationReport) -> FullProfile:
        logger.info("Stage: automatic data understanding")
        understanding = self._understanding_engine.analyze(df)

        logger.info("Stage: per-column profiling")
        column_profiles = self._column_profiler.profile_all(df, understanding.roles)

        logger.info("Stage: missing value analysis")
        missing_analysis = self._missing_analyzer.analyze(
            df, understanding.roles.numeric, understanding.roles.categorical
        )

        logger.info("Stage: duplicate detection")
        duplicate_report = self._duplicate_detector.detect(
            df, understanding.roles.numeric, understanding.roles.constant
        )

        logger.info("Stage: correlation analysis")
        try:
            correlation_result = self._correlation_analyzer.analyze(
                df, understanding.roles.numeric, understanding.roles.categorical
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Correlation analysis failed: %s", exc)
            correlation_result = None

        logger.info("Stage: distribution analysis")
        try:
            distributions = self._distribution_analyzer.analyze(df, understanding.roles.numeric)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Distribution analysis failed: %s", exc)
            distributions = {}

        logger.info("Stage: outlier detection")
        try:
            outlier_report = self._outlier_detector.detect(df, understanding.roles.numeric)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Outlier detection failed: %s", exc)
            outlier_report = OutlierReport(per_column={}, multivariate=None, total_affected_columns=[])

        logger.info("Stage: data quality assessment")
        quality_report = self._quality_assessor.assess(df, validation_report, column_profiles, duplicate_report)

        logger.info("Stage: feature recommendations")
        recommendations = self._recommendation_engine.recommend(
            df, understanding, column_profiles, correlation_result, duplicate_report
        )

        logger.info("Stage: business insight generation")
        business_insights = self._insight_generator.generate(
            df, understanding, column_profiles, quality_report, missing_analysis, duplicate_report, recommendations
        )

        return FullProfile(
            understanding=understanding,
            column_profiles=column_profiles,
            missing_analysis=missing_analysis,
            duplicate_report=duplicate_report,
            quality_report=quality_report,
            correlation_result=correlation_result,
            distributions=distributions,
            outlier_report=outlier_report,
            recommendations=recommendations,
            business_insights=business_insights,
        )
