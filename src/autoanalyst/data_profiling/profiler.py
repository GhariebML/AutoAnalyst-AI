"""Dataset profiling helpers for comprehensive data understanding and quality scoring."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ColumnProfile:
    """Detailed profile metrics for an individual DataFrame column."""

    column_name: str
    dtype: str
    total_count: int
    missing_count: int
    missing_percentage: float
    unique_count: int
    unique_ratio: float
    zero_count: int
    zero_percentage: float
    infinite_count: int
    memory_bytes: int
    is_constant: bool
    is_numeric: bool
    is_categorical: bool
    is_datetime: bool


@dataclass
class DataQualityReport:
    """Data quality health score and breakdown across key dimensions."""

    health_score: float  # 0 to 100
    completeness_score: float  # 0 to 100 (absence of missing values)
    uniqueness_score: float  # 0 to 100 (absence of duplicate rows)
    uniformity_score: float  # 0 to 100 (absence of constant/empty columns)
    validity_score: float  # 0 to 100 (absence of infinite or invalid values)
    grade: str  # 'A', 'B', 'C', 'D', 'F'
    flags: list[str]


@dataclass
class DataProfile:
    """Comprehensive dataset profile schema."""

    rows: int
    columns: int
    column_names: list[str]
    dtypes: dict[str, str]
    missing_values_total: int
    missing_cells_percentage: float
    duplicate_rows: int
    duplicate_rows_percentage: float
    duplicate_columns: list[str]
    constant_columns: list[str]
    memory_footprint_bytes: int
    memory_footprint_formatted: str
    column_profiles: dict[str, ColumnProfile]
    quality_report: DataQualityReport

    def to_dict(self) -> dict[str, Any]:
        """Convert DataProfile to a plain dictionary for serialization."""
        return asdict(self)


def calculate_data_quality_score(
    df: pd.DataFrame,
    missing_total: int,
    duplicate_rows: int,
    constant_cols: list[str],
    inf_total: int,
) -> DataQualityReport:
    """Calculate an objective 0-100% data quality health score."""
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    flags: list[str] = []

    # 1. Completeness (35% weight)
    if total_cells > 0:
        missing_rate = missing_total / total_cells
        completeness = max(0.0, 1.0 - missing_rate) * 100.0
    else:
        completeness = 0.0
    if completeness < 80.0:
        flags.append(f"High missingness: {missing_total} missing cells ({100 - completeness:.1f}% missing).")

    # 2. Uniqueness (25% weight)
    if total_rows > 0:
        dup_rate = duplicate_rows / total_rows
        uniqueness = max(0.0, 1.0 - dup_rate) * 100.0
    else:
        uniqueness = 0.0
    if uniqueness < 90.0:
        flags.append(f"Significant duplicates: {duplicate_rows} duplicate rows detected.")

    # 3. Uniformity & Non-constancy (20% weight)
    if total_cols > 0:
        constant_rate = len(constant_cols) / total_cols
        uniformity = max(0.0, 1.0 - constant_rate) * 100.0
    else:
        uniformity = 0.0
    if constant_cols:
        flags.append(f"Constant columns with zero variance: {constant_cols}.")

    # 4. Validity & Cleanliness (20% weight)
    if total_cells > 0:
        inf_rate = inf_total / total_cells
        validity = max(0.0, 1.0 - (inf_rate * 5.0)) * 100.0
    else:
        validity = 0.0
    if inf_total > 0:
        flags.append(f"Infinite or extreme unparsed values: {inf_total} instances.")

    # Combined Health Score
    health_score = (0.35 * completeness) + (0.25 * uniqueness) + (0.20 * uniformity) + (0.20 * validity)
    health_score = round(max(0.0, min(100.0, health_score)), 1)

    if health_score >= 90.0:
        grade = "A"
    elif health_score >= 80.0:
        grade = "B"
    elif health_score >= 70.0:
        grade = "C"
    elif health_score >= 60.0:
        grade = "D"
    else:
        grade = "F"

    return DataQualityReport(
        health_score=health_score,
        completeness_score=round(completeness, 1),
        uniqueness_score=round(uniqueness, 1),
        uniformity_score=round(uniformity, 1),
        validity_score=round(validity, 1),
        grade=grade,
        flags=flags,
    )


def profile_column(series: pd.Series) -> ColumnProfile:
    """Compute detailed profile metrics for a single Series."""
    col_name = str(series.name)
    dtype_str = str(series.dtype)
    total_len = len(series)
    missing_count = int(series.isna().sum())
    missing_pct = round((missing_count / total_len * 100.0) if total_len else 0.0, 2)

    unique_count = int(series.nunique(dropna=True))
    unique_ratio = round((unique_count / total_len) if total_len else 0.0, 4)

    is_num = bool(pd.api.types.is_numeric_dtype(series))
    is_cat = bool(
        isinstance(series.dtype, pd.CategoricalDtype)
        or pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
    )
    is_dt = bool(pd.api.types.is_datetime64_any_dtype(series))

    zero_count = 0
    inf_count = 0
    if is_num:
        zero_count = int((series == 0).sum())
        # Inf count
        numeric_series = series.dropna()
        if not numeric_series.empty:
            inf_count = int(np.isinf(numeric_series).sum())

    zero_pct = round((zero_count / total_len * 100.0) if total_len else 0.0, 2)
    memory_bytes = int(series.memory_usage(deep=True))
    is_const = unique_count <= 1 and missing_count == 0

    return ColumnProfile(
        column_name=col_name,
        dtype=dtype_str,
        total_count=total_len,
        missing_count=missing_count,
        missing_percentage=missing_pct,
        unique_count=unique_count,
        unique_ratio=unique_ratio,
        zero_count=zero_count,
        zero_percentage=zero_pct,
        infinite_count=inf_count,
        memory_bytes=memory_bytes,
        is_constant=is_const,
        is_numeric=is_num,
        is_categorical=is_cat,
        is_datetime=is_dt,
    )


def profile_dataframe(df: pd.DataFrame) -> DataProfile:
    """Generate a rich, structured DataProfile for a DataFrame."""
    if df.empty:
        raise ValueError("Cannot profile an empty DataFrame.")

    rows = int(df.shape[0])
    cols = int(df.shape[1])
    total_cells = rows * cols

    missing_total = int(df.isna().sum().sum())
    missing_cells_pct = round((missing_total / total_cells * 100.0) if total_cells else 0.0, 2)

    dup_rows = int(df.duplicated().sum())
    dup_rows_pct = round((dup_rows / rows * 100.0) if rows else 0.0, 2)

    # Duplicate column detection (columns with identical values)
    dup_cols: list[str] = []
    if cols > 1:
        # Check pairwise duplicate columns efficiently on transposed or equality
        sample_df = df.head(100) if rows > 100 else df
        for i in range(cols):
            for j in range(i + 1, cols):
                col_i = df.columns[i]
                col_j = df.columns[j]
                if sample_df[col_i].equals(sample_df[col_j]) and df[col_i].equals(df[col_j]):
                    dup_cols.append(f"{col_i} == {col_j}")

    col_profiles: dict[str, ColumnProfile] = {}
    constant_cols: list[str] = []
    total_inf = 0

    for col in df.columns:
        cp = profile_column(df[col])
        col_profiles[str(col)] = cp
        if cp.is_constant:
            constant_cols.append(str(col))
        total_inf += cp.infinite_count

    mem_bytes = int(df.memory_usage(deep=True).sum())
    if mem_bytes >= 1024 * 1024:
        mem_str = f"{mem_bytes / (1024 * 1024):.2f} MB"
    else:
        mem_str = f"{mem_bytes / 1024:.2f} KB"

    quality = calculate_data_quality_score(
        df=df,
        missing_total=missing_total,
        duplicate_rows=dup_rows,
        constant_cols=constant_cols,
        inf_total=total_inf,
    )

    return DataProfile(
        rows=rows,
        columns=cols,
        column_names=list(df.columns),
        dtypes={str(column): str(dtype) for column, dtype in df.dtypes.items()},
        missing_values_total=missing_total,
        missing_cells_percentage=missing_cells_pct,
        duplicate_rows=dup_rows,
        duplicate_rows_percentage=dup_rows_pct,
        duplicate_columns=dup_cols,
        constant_columns=constant_cols,
        memory_footprint_bytes=mem_bytes,
        memory_footprint_formatted=mem_str,
        column_profiles=col_profiles,
        quality_report=quality,
    )


def generate_basic_profile(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a profile summary dictionary compatible with existing pipeline contracts."""
    dp = profile_dataframe(df)
    res = dp.to_dict()
    # Ensure standard top-level legacy keys are present
    res["health_score"] = dp.quality_report.health_score
    res["quality_grade"] = dp.quality_report.grade
    res["quality_flags"] = dp.quality_report.flags
    return res


def get_missing_values_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing-value counts and percentages per column, sorted descending."""
    total_rows = len(df)
    missing_count = df.isna().sum()
    if total_rows > 0:
        missing_percent = missing_count / total_rows * 100.0
    else:
        missing_percent = missing_count * 0.0

    return (
        pd.DataFrame(
            {
                "column": missing_count.index.astype(str),
                "missing_count": missing_count.values,
                "missing_percent": missing_percent.values.round(2),
            }
        )
        .sort_values("missing_count", ascending=False)
        .reset_index(drop=True)
    )


def get_duplicate_count(df: pd.DataFrame) -> int:
    """Return the number of duplicated rows in a DataFrame."""
    return int(df.duplicated().sum())
