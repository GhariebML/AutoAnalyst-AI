"""Feature engineering and transformation utilities for tabular datasets."""

from __future__ import annotations

import logging
from typing import Any, Literal

import pandas as pd
from sklearn.feature_selection import SelectKBest, VarianceThreshold, mutual_info_classif, mutual_info_regression
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures, RobustScaler, StandardScaler

logger = logging.getLogger(__name__)

# Default cardinality thresholds
DEFAULT_CARDINALITY_THRESHOLD = 20
DEFAULT_CARDINALITY_RATIO = 0.9


def detect_high_cardinality_columns(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    threshold: int = DEFAULT_CARDINALITY_THRESHOLD,
    ratio: float = DEFAULT_CARDINALITY_RATIO,
) -> list[dict[str, Any]]:
    """Detect categorical columns with high cardinality (many distinct values).

    Parameters
    ----------
    df:
        The DataFrame to inspect.
    columns:
        Specific columns to check. If None, auto-selects categorical/object columns.
    threshold:
        Absolute unique count threshold above which a column is considered high cardinality.
    ratio:
        Unique count / total rows ratio above which a column is considered high cardinality.
    """
    total_rows = len(df)
    if columns is not None:
        selected = [c for c in columns if c in df.columns]
    else:
        selected = list(df.select_dtypes(include=["object", "category", "string"]).columns)

    results: list[dict[str, Any]] = []
    for col in selected:
        unique_count = int(df[col].nunique(dropna=True))
        card_ratio = float(unique_count / total_rows) if total_rows > 0 else 0.0

        is_high = False
        if total_rows > 0 and (unique_count > threshold or card_ratio >= ratio):
            is_high = True

        results.append(
            {
                "column": str(col),
                "unique_count": unique_count,
                "cardinality_ratio": round(card_ratio, 4),
                "status": "high_cardinality" if is_high else "normal",
            }
        )

    return results


def encode_categorical_columns(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    drop_first: bool = False,
    cardinality_threshold: int = DEFAULT_CARDINALITY_THRESHOLD,
    cardinality_ratio: float = DEFAULT_CARDINALITY_RATIO,
) -> pd.DataFrame:
    """One-hot encode categorical columns in a DataFrame with high-cardinality warnings."""
    if df.empty:
        return df.copy()

    selected = columns or list(df.select_dtypes(include=["object", "category", "string"]).columns)
    if not selected:
        return df.copy()

    missing = [c for c in selected if c not in df.columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}")

    # Check for high-cardinality columns and log warnings
    cardinality_info = detect_high_cardinality_columns(
        df,
        columns=selected,
        threshold=cardinality_threshold,
        ratio=cardinality_ratio,
    )
    for info in cardinality_info:
        if info["status"] == "high_cardinality":
            logger.warning(
                "High-cardinality column '%s' detected (%d unique values, ratio=%.2f). "
                "One-hot encoding may generate excessive features.",
                info["column"],
                info["unique_count"],
                info["cardinality_ratio"],
            )

    return pd.get_dummies(df, columns=selected, drop_first=drop_first, dtype=int)


def encode_frequency(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Replace categorical values with their observed frequency (percentage) in the column."""
    result = df.copy()
    selected = columns or list(result.select_dtypes(include=["object", "category", "string"]).columns)
    for col in selected:
        if col not in result.columns:
            continue
        freq_map = result[col].value_counts(normalize=True).to_dict()
        result[f"{col}_freq"] = result[col].map(freq_map).fillna(0.0)
    return result


def encode_target(
    df: pd.DataFrame,
    target_column: str,
    columns: list[str] | None = None,
    smoothing: float = 10.0,
) -> pd.DataFrame:
    """Perform smooth Bayesian target encoding for categorical columns without data leakage.

    Formula: S_i = (n_i * mean_i + m * global_mean) / (n_i + m)
    """
    if target_column not in df.columns:
        raise KeyError(f"Target column '{target_column}' not found.")

    result = df.copy()
    target = pd.to_numeric(result[target_column], errors="coerce")
    global_mean = float(target.mean())

    selected = columns or list(result.select_dtypes(include=["object", "category", "string"]).columns)
    if target_column in selected:
        selected.remove(target_column)

    for col in selected:
        if col not in result.columns:
            continue
        stats = target.groupby(result[col]).agg(["count", "mean"])
        counts = stats["count"]
        means = stats["mean"]
        smooth_enc = (counts * means + smoothing * global_mean) / (counts + smoothing)
        result[f"{col}_target_enc"] = result[col].map(smooth_enc.to_dict()).fillna(global_mean)

    return result


def extract_datetime_features(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    drop_original: bool = False,
) -> pd.DataFrame:
    """Extract temporal features (year, month, day, dayofweek, is_weekend, hour, quarter) from date columns."""
    result = df.copy()
    candidates = columns or []

    if not candidates:
        for col in result.columns:
            if pd.api.types.is_datetime64_any_dtype(result[col]):
                candidates.append(col)
            elif pd.api.types.is_object_dtype(result[col]) or pd.api.types.is_string_dtype(result[col]):
                sample = result[col].dropna().head(10)
                if not sample.empty:
                    try:
                        pd.to_datetime(sample, errors="raise")
                        candidates.append(col)
                    except Exception:
                        pass

    for col in candidates:
        if col not in result.columns:
            continue
        dt_series = pd.to_datetime(result[col], errors="coerce")
        if dt_series.isna().all():
            continue

        result[f"{col}_year"] = dt_series.dt.year.fillna(-1).astype(int)
        result[f"{col}_month"] = dt_series.dt.month.fillna(-1).astype(int)
        result[f"{col}_day"] = dt_series.dt.day.fillna(-1).astype(int)
        result[f"{col}_dayofweek"] = dt_series.dt.dayofweek.fillna(-1).astype(int)
        result[f"{col}_is_weekend"] = dt_series.dt.dayofweek.isin([5, 6]).astype(int)
        result[f"{col}_quarter"] = dt_series.dt.quarter.fillna(-1).astype(int)

        if drop_original:
            result = result.drop(columns=[col])

    return result


def scale_features(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: Literal["standard", "robust", "minmax"] = "standard",
    exclude_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Apply feature scaling (StandardScaler, RobustScaler, or MinMaxScaler) to numeric columns."""
    result = df.copy()
    exclude = set(exclude_columns or [])
    numeric_cols = [c for c in (columns or list(result.select_dtypes(include="number").columns)) if c not in exclude]

    if not numeric_cols:
        return result

    if method == "standard":
        scaler = StandardScaler()
    elif method == "robust":
        scaler = RobustScaler()
    elif method == "minmax":
        scaler = MinMaxScaler()
    else:
        raise ValueError(f"Unknown scaling method '{method}'. Use: standard, robust, minmax.")

    scaled_vals = scaler.fit_transform(result[numeric_cols])
    result[numeric_cols] = pd.DataFrame(scaled_vals, columns=numeric_cols, index=result.index)
    return result


def select_features(
    df: pd.DataFrame,
    target_column: str,
    task: Literal["classification", "regression"] = "classification",
    k: int | str = 10,
    variance_threshold: float = 0.0,
) -> tuple[pd.DataFrame, list[str]]:
    """Select the most informative numeric features using variance and mutual information.

    Returns the transformed DataFrame with the selected features plus the target column,
    and a list of selected feature column names.
    """
    if target_column not in df.columns:
        raise KeyError(f"Target column '{target_column}' not found.")

    X = df.drop(columns=[target_column]).select_dtypes(include="number")
    y = df[target_column]

    if X.empty:
        return df.copy(), []

    vt = VarianceThreshold(threshold=variance_threshold)
    vt.fit(X)
    retained_cols = list(X.columns[vt.get_support()])
    X = X[retained_cols]

    if X.shape[1] <= 1:
        return df[[*retained_cols, target_column]], retained_cols

    n_features = X.shape[1]
    k_val = min(int(k) if isinstance(k, (int, float)) else 10, n_features)

    if task == "classification":
        mi_fn = mutual_info_classif
    else:
        mi_fn = mutual_info_regression

    selector = SelectKBest(score_func=mi_fn, k=k_val)
    selector.fit(X.fillna(0), y)
    selected_cols = list(X.columns[selector.get_support()])

    result_df = pd.concat([df[selected_cols], df[[target_column]]], axis=1)
    return result_df, selected_cols


def create_interaction_features(
    df: pd.DataFrame,
    numeric_columns: list[str] | None = None,
    operations: list[str] | None = None,
) -> pd.DataFrame:
    """Create pairwise interaction features (multiplication and ratios) for numeric columns."""
    result = df.copy()
    cols = numeric_columns or list(result.select_dtypes(include="number").columns)
    ops = operations or ["multiply", "ratio"]

    n = len(cols)
    for i in range(n):
        for j in range(i + 1, n):
            c1 = cols[i]
            c2 = cols[j]
            if "multiply" in ops:
                result[f"{c1}_x_{c2}"] = result[c1] * result[c2]
            if "ratio" in ops:
                eps = 1e-6
                result[f"{c1}_div_{c2}"] = result[c1] / (result[c2].replace(0, eps) + eps)

    return result


def create_polynomial_features(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    degree: int = 2,
    include_bias: bool = False,
) -> pd.DataFrame:
    """Generate polynomial feature combinations for specified numeric columns."""
    result = df.copy()
    selected = columns or list(result.select_dtypes(include="number").columns)
    if not selected:
        return result

    poly = PolynomialFeatures(degree=degree, include_bias=include_bias)
    poly_array = poly.fit_transform(result[selected].fillna(0))
    feature_names = poly.get_feature_names_out(selected)

    poly_df = pd.DataFrame(poly_array, columns=feature_names, index=result.index)
    new_cols = [c for c in feature_names if c not in result.columns]
    for c in new_cols:
        result[c] = poly_df[c]

    return result
