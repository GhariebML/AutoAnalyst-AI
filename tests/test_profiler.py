import pandas as pd

from autoanalyst.profiling.understanding import DataUnderstandingEngine
from autoanalyst.profiling.column_profiler import ColumnProfiler
from autoanalyst.profiling.missing_analysis import MissingValueAnalyzer
from autoanalyst.profiling.duplicates import DuplicateDetector
from autoanalyst.profiling.correlation import CorrelationAnalyzer
from autoanalyst.profiling.distribution import DistributionAnalyzer
from autoanalyst.profiling.outliers import OutlierDetector
from autoanalyst.profiling.profiler import DatasetProfiler
from autoanalyst.validation.validator import DatasetValidator


def test_understanding_roles(sample_df):
    engine = DataUnderstandingEngine()
    result = engine.analyze(sample_df)
    assert "age" in result.roles.numeric
    assert "customer_id" in result.identifier_columns
    assert result.n_rows == len(sample_df)


def test_column_profiler(sample_df):
    engine = DataUnderstandingEngine()
    understanding = engine.analyze(sample_df)
    profiler = ColumnProfiler()
    profiles = profiler.profile_all(sample_df, understanding.roles)
    assert "age" in profiles
    assert profiles["age"].numeric_stats is not None
    assert profiles["gender"].categorical_stats is not None


def test_missing_analysis(sample_df):
    engine = DataUnderstandingEngine()
    understanding = engine.analyze(sample_df)
    analyzer = MissingValueAnalyzer()
    result = analyzer.analyze(sample_df, understanding.roles.numeric, understanding.roles.categorical)
    assert result.total_missing_cells > 0
    assert "income" in result.columns_with_missing


def test_duplicate_detection(sample_df):
    engine = DataUnderstandingEngine()
    understanding = engine.analyze(sample_df)
    detector = DuplicateDetector()
    result = detector.detect(sample_df, understanding.roles.numeric, understanding.roles.constant)
    assert result.duplicate_row_count >= 5  # 5 duplicate rows injected in fixture
    assert "constant_col" in result.constant_columns


def test_correlation_analysis(sample_df):
    engine = DataUnderstandingEngine()
    understanding = engine.analyze(sample_df)
    analyzer = CorrelationAnalyzer()
    result = analyzer.analyze(sample_df, understanding.roles.numeric, understanding.roles.categorical)
    assert result.pearson is not None


def test_distribution_analysis(sample_df):
    engine = DataUnderstandingEngine()
    understanding = engine.analyze(sample_df)
    analyzer = DistributionAnalyzer()
    result = analyzer.analyze(sample_df, understanding.roles.numeric)
    assert "income" in result


def test_outlier_detection(sample_df):
    engine = DataUnderstandingEngine()
    understanding = engine.analyze(sample_df)
    detector = OutlierDetector()
    result = detector.detect(sample_df, understanding.roles.numeric)
    assert "income" in result.per_column


def test_full_profiler_pipeline(sample_df):
    validator = DatasetValidator()
    validation_report = validator.validate(sample_df)
    profiler = DatasetProfiler()
    full_profile = profiler.run(sample_df, validation_report)
    assert full_profile.quality_report.overall_quality_score >= 0
    assert len(full_profile.business_insights) > 0
    d = full_profile.to_dict()
    assert "data_understanding" in d
    assert "feature_recommendations" in d
