"""Module 3 — Automatic Data Understanding.

Infers, without any user configuration, the semantic role of each column
(identifier, target candidate, numeric/categorical/datetime/boolean/text),
groups columns into feature groups, and guesses the likely ML problem type.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from autoanalyst.utils.helpers import (
    get_logger,
    is_effectively_boolean,
    is_effectively_datetime,
    is_effectively_numeric_object,
)

logger = get_logger(__name__)

_ID_NAME_HINTS = ("id", "_id", "uuid", "guid", "key", "index", "pk")
_TARGET_NAME_HINTS = (
    "target", "label", "class", "outcome", "churn", "y", "response",
    "result", "default", "fraud", "survived", "price", "sales", "revenue",
)
HIGH_CARDINALITY_RATIO = 0.9
LOW_CARDINALITY_MAX_UNIQUE = 20
TEXT_AVG_LENGTH_THRESHOLD = 30


@dataclass
class ColumnRoles:
    numeric: list[str] = field(default_factory=list)
    categorical: list[str] = field(default_factory=list)
    datetime: list[str] = field(default_factory=list)
    boolean: list[str] = field(default_factory=list)
    text: list[str] = field(default_factory=list)
    identifier: list[str] = field(default_factory=list)
    constant: list[str] = field(default_factory=list)
    unique: list[str] = field(default_factory=list)
    high_cardinality: list[str] = field(default_factory=list)
    low_cardinality: list[str] = field(default_factory=list)


@dataclass
class DatasetUnderstanding:
    n_rows: int
    n_columns: int
    feature_names: list[str]
    roles: ColumnRoles
    primary_key_candidate: str | None
    identifier_columns: list[str]
    target_candidates: list[str]
    feature_groups: dict[str, list[str]]
    potential_relationships: list[str]
    is_likely_time_series: bool
    inferred_problem_type: str
    regression_target_candidates: list[str]
    classification_target_candidates: list[str]
    dataset_purpose_guess: str

    def to_dict(self) -> dict:
        return {
            "n_rows": self.n_rows,
            "n_columns": self.n_columns,
            "feature_names": self.feature_names,
            "column_roles": {
                "numeric": self.roles.numeric,
                "categorical": self.roles.categorical,
                "datetime": self.roles.datetime,
                "boolean": self.roles.boolean,
                "text": self.roles.text,
                "identifier": self.roles.identifier,
                "constant": self.roles.constant,
                "unique": self.roles.unique,
                "high_cardinality": self.roles.high_cardinality,
                "low_cardinality": self.roles.low_cardinality,
            },
            "primary_key_candidate": self.primary_key_candidate,
            "identifier_columns": self.identifier_columns,
            "target_candidates": self.target_candidates,
            "feature_groups": self.feature_groups,
            "potential_relationships": self.potential_relationships,
            "is_likely_time_series": self.is_likely_time_series,
            "inferred_problem_type": self.inferred_problem_type,
            "regression_target_candidates": self.regression_target_candidates,
            "classification_target_candidates": self.classification_target_candidates,
            "dataset_purpose_guess": self.dataset_purpose_guess,
        }


class DataUnderstandingEngine:
    """Infers dataset semantics automatically from column names and content."""

    def analyze(self, df: pd.DataFrame) -> DatasetUnderstanding:
        n_rows, n_cols = df.shape
        roles = ColumnRoles()

        for col in df.columns:
            self._classify_column(df, col, roles)

        identifier_columns = self._detect_identifiers(df, roles)
        primary_key = self._detect_primary_key(df, identifier_columns)
        target_candidates = self._detect_target_candidates(df, roles, identifier_columns)
        feature_groups = self._group_features(df.columns.tolist())
        relationships = self._detect_relationships(df, roles)
        is_time_series = self._detect_time_series(df, roles)

        regression_targets = [
            c for c in target_candidates
            if c in roles.numeric and c not in roles.low_cardinality
        ]
        classification_targets = [
            c for c in target_candidates
            if c in roles.categorical or c in roles.boolean or c in roles.low_cardinality
        ]

        problem_type = self._infer_problem_type(
            is_time_series, regression_targets, classification_targets
        )
        purpose = self._guess_purpose(df.columns.tolist(), problem_type)

        return DatasetUnderstanding(
            n_rows=n_rows,
            n_columns=n_cols,
            feature_names=df.columns.tolist(),
            roles=roles,
            primary_key_candidate=primary_key,
            identifier_columns=identifier_columns,
            target_candidates=target_candidates,
            feature_groups=feature_groups,
            potential_relationships=relationships,
            is_likely_time_series=is_time_series,
            inferred_problem_type=problem_type,
            regression_target_candidates=regression_targets,
            classification_target_candidates=classification_targets,
            dataset_purpose_guess=purpose,
        )

    # ------------------------------------------------------------- steps --
    def _classify_column(self, df: pd.DataFrame, col: str, roles: ColumnRoles) -> None:
        series = df[col]
        n = len(series)
        n_unique = series.nunique(dropna=True)

        if n_unique <= 1:
            roles.constant.append(col)
        if n and n_unique == n:
            roles.unique.append(col)
        if n and n_unique / n >= HIGH_CARDINALITY_RATIO and n_unique > LOW_CARDINALITY_MAX_UNIQUE:
            roles.high_cardinality.append(col)
        elif n_unique <= LOW_CARDINALITY_MAX_UNIQUE:
            roles.low_cardinality.append(col)

        if is_effectively_boolean(series):
            roles.boolean.append(col)
        elif pd.api.types.is_numeric_dtype(series):
            roles.numeric.append(col)
        elif pd.api.types.is_datetime64_any_dtype(series):
            roles.datetime.append(col)
        elif is_effectively_datetime(series):
            roles.datetime.append(col)
        elif is_effectively_numeric_object(series):
            roles.numeric.append(col)
        else:
            avg_len = series.dropna().astype(str).str.len().mean() if series.notna().any() else 0
            if avg_len and avg_len > TEXT_AVG_LENGTH_THRESHOLD and n_unique > LOW_CARDINALITY_MAX_UNIQUE:
                roles.text.append(col)
            else:
                roles.categorical.append(col)

    def _detect_identifiers(self, df: pd.DataFrame, roles: ColumnRoles) -> list[str]:
        ids = []
        n = len(df)
        for col in df.columns:
            name_lower = str(col).lower()
            name_hint = any(h in name_lower for h in _ID_NAME_HINTS)
            near_unique = n > 0 and df[col].nunique(dropna=True) / n >= 0.98
            if name_hint or (near_unique and col in roles.unique):
                ids.append(col)
        return ids

    def _detect_primary_key(self, df: pd.DataFrame, identifier_columns: list[str]) -> str | None:
        n = len(df)
        best = None
        for col in identifier_columns:
            if df[col].isna().any():
                continue
            if df[col].nunique(dropna=True) == n:
                best = col
                break
        return best

    def _detect_target_candidates(self, df: pd.DataFrame, roles: ColumnRoles, identifier_columns: list[str]) -> list[str]:
        candidates = []
        for col in df.columns:
            if col in identifier_columns or col in roles.constant or col in roles.text:
                continue
            name_lower = str(col).lower()
            if any(h in name_lower for h in _TARGET_NAME_HINTS):
                candidates.append(col)
        if not candidates:
            # Fall back: last column, if it's not an identifier, is a common
            # convention in many tabular ML datasets.
            last_col = df.columns[-1]
            if last_col not in identifier_columns and last_col not in roles.text:
                candidates.append(last_col)
        return candidates

    def _group_features(self, columns: list[str]) -> dict[str, list[str]]:
        """Group columns sharing a common name prefix/suffix (heuristic)."""
        groups: dict[str, list[str]] = {}
        for col in columns:
            parts = re_split_name(str(col))
            prefix = parts[0] if parts else str(col)
            groups.setdefault(prefix, []).append(col)
        return {k: v for k, v in groups.items() if len(v) > 1}

    def _detect_relationships(self, df: pd.DataFrame, roles: ColumnRoles) -> list[str]:
        relationships = []
        id_like = [c for c in df.columns if str(c).lower().endswith(("_id", "id")) and c in roles.categorical or c in roles.numeric]
        for col in id_like:
            if str(col).lower() not in ("id",) and str(col).lower().endswith("_id"):
                referenced = str(col).lower().replace("_id", "")
                relationships.append(f"'{col}' may be a foreign key referencing a '{referenced}' entity")
        return relationships[:15]

    def _detect_time_series(self, df: pd.DataFrame, roles: ColumnRoles) -> bool:
        if not roles.datetime:
            return False
        for dt_col in roles.datetime:
            series = pd.to_datetime(df[dt_col], errors="coerce", format="mixed") if not pd.api.types.is_datetime64_any_dtype(df[dt_col]) else df[dt_col]
            if series.is_monotonic_increasing or series.is_monotonic_decreasing:
                return True
        return len(roles.datetime) > 0 and len(df) > 1

    def _infer_problem_type(self, is_time_series: bool, regression_targets: list[str], classification_targets: list[str]) -> str:
        if is_time_series:
            return "time_series_forecasting"
        if classification_targets:
            return "supervised_classification"
        if regression_targets:
            return "supervised_regression"
        return "unsupervised_or_exploratory"

    def _guess_purpose(self, columns: list[str], problem_type: str) -> str:
        lowered = " ".join(str(c).lower() for c in columns)
        if any(k in lowered for k in ("churn", "subscription", "customer")):
            domain = "customer analytics / churn prediction"
        elif any(k in lowered for k in ("price", "sales", "revenue", "transaction")):
            domain = "sales / pricing analytics"
        elif any(k in lowered for k in ("patient", "diagnosis", "disease", "symptom", "medical")):
            domain = "healthcare / clinical analytics"
        elif any(k in lowered for k in ("fraud", "transaction", "amount", "risk")):
            domain = "risk / fraud detection"
        elif any(k in lowered for k in ("temp", "sensor", "device", "reading")):
            domain = "IoT / sensor monitoring"
        else:
            domain = "general tabular analytics"
        return f"Likely a {domain} dataset (inferred problem type: {problem_type})."


def re_split_name(name: str) -> list[str]:
    """Split a column name on common separators to find a semantic prefix."""
    import re

    parts = re.split(r"[_\-. ]+", name)
    return [p for p in parts if p]
