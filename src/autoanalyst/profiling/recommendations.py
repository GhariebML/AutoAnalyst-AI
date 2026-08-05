"""Module 11 — Feature Recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from autoanalyst.profiling.column_profiler import ColumnProfile
from autoanalyst.profiling.correlation import CorrelationResult
from autoanalyst.profiling.duplicates import DuplicateReport
from autoanalyst.profiling.understanding import DatasetUnderstanding
from autoanalyst.utils.helpers import get_logger

logger = get_logger(__name__)

HIGH_MISSING_DROP_THRESHOLD = 60.0
HIGH_CARDINALITY_ENCODE_LIMIT = 50
SKEW_TRANSFORM_THRESHOLD = 1.0


@dataclass
class FeatureRecommendations:
    columns_to_drop: list[str]
    columns_to_encode: list[str]
    columns_to_normalize: list[str]
    columns_to_scale: list[str]
    columns_to_impute: list[str]
    columns_to_bin: list[str]
    potential_target_column: str | None
    potential_leakage: list[str]
    feature_engineering_ideas: list[str]

    def to_dict(self) -> dict:
        return {
            "columns_to_drop": self.columns_to_drop,
            "columns_to_encode": self.columns_to_encode,
            "columns_to_normalize": self.columns_to_normalize,
            "columns_to_scale": self.columns_to_scale,
            "columns_to_impute": self.columns_to_impute,
            "columns_to_bin": self.columns_to_bin,
            "potential_target_column": self.potential_target_column,
            "potential_leakage": self.potential_leakage,
            "feature_engineering_ideas": self.feature_engineering_ideas,
        }


class FeatureRecommendationEngine:
    def recommend(
        self,
        df: pd.DataFrame,
        understanding: DatasetUnderstanding,
        column_profiles: dict[str, ColumnProfile],
        correlation_result: CorrelationResult | None,
        duplicate_report: DuplicateReport,
    ) -> FeatureRecommendations:
        roles = understanding.roles
        drop, encode, normalize, scale, impute, bin_cols = [], [], [], [], [], []

        drop.extend(roles.constant)
        drop.extend(duplicate_report.redundant_columns)
        drop.extend(understanding.identifier_columns)

        for name, profile in column_profiles.items():
            if profile.missing_pct >= HIGH_MISSING_DROP_THRESHOLD and name not in drop:
                drop.append(name)
            elif 0 < profile.missing_pct < HIGH_MISSING_DROP_THRESHOLD:
                impute.append(name)

        for name in roles.categorical:
            if name in drop:
                continue
            n_unique = column_profiles[name].unique_count if name in column_profiles else 0
            if n_unique <= HIGH_CARDINALITY_ENCODE_LIMIT:
                encode.append(name)
            else:
                bin_cols.append(name)  # too many categories -> group/bin rare ones

        for name in roles.numeric:
            if name in drop:
                continue
            stats = column_profiles[name].numeric_stats if name in column_profiles else None
            scale.append(name)
            if stats and stats.get("skewness") is not None and abs(stats["skewness"]) > SKEW_TRANSFORM_THRESHOLD:
                normalize.append(name)

        target = understanding.target_candidates[0] if understanding.target_candidates else None
        leakage = self._detect_leakage(target, correlation_result, roles.numeric)
        ideas = self._feature_engineering_ideas(understanding, column_profiles)

        # De-duplicate while preserving order.
        def dedupe(seq: list[str]) -> list[str]:
            seen: set[str] = set()
            out = []
            for x in seq:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        return FeatureRecommendations(
            columns_to_drop=dedupe(drop),
            columns_to_encode=dedupe([c for c in encode if c not in drop]),
            columns_to_normalize=dedupe([c for c in normalize if c not in drop]),
            columns_to_scale=dedupe([c for c in scale if c not in drop]),
            columns_to_impute=dedupe([c for c in impute if c not in drop]),
            columns_to_bin=dedupe(bin_cols),
            potential_target_column=target,
            potential_leakage=leakage,
            feature_engineering_ideas=ideas,
        )

    def _detect_leakage(self, target: str | None, correlation_result: CorrelationResult | None, numeric_cols: list[str]) -> list[str]:
        if not target or not correlation_result or not correlation_result.pearson or target not in correlation_result.pearson:
            return []
        suspects = []
        for other, value in correlation_result.pearson.get(target, {}).items():
            if other == target or value is None:
                continue
            if abs(value) >= 0.95:
                suspects.append(f"'{other}' correlates {value:.2f} with target '{target}' — verify it isn't derived from/leaking the target.")
        return suspects[:10]

    def _feature_engineering_ideas(self, understanding: DatasetUnderstanding, column_profiles: dict[str, ColumnProfile]) -> list[str]:
        ideas = []
        roles = understanding.roles
        if roles.datetime:
            ideas.append(f"Extract year/month/day/day-of-week/hour components from datetime column(s): {roles.datetime[:5]}")
        if understanding.is_likely_time_series:
            ideas.append("Create lag features and rolling-window aggregates given likely time-series structure.")
        if len(roles.numeric) >= 2:
            ideas.append("Consider interaction/ratio features between strongly related numeric columns.")
        if roles.high_cardinality:
            ideas.append(f"Use target/frequency encoding instead of one-hot for high-cardinality column(s): {roles.high_cardinality[:5]}")
        if roles.text:
            ideas.append(f"Derive TF-IDF or embedding features from free-text column(s): {roles.text[:5]}")
        if understanding.feature_groups:
            ideas.append("Aggregate related feature groups (shared name prefixes) into summary statistics.")
        return ideas
