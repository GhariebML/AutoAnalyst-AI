"""Data cleaning and preprocessing functions with comprehensive audit logging."""

from __future__ import annotations

import datetime
import logging
from dataclasses import asdict, dataclass, field
from typing import Any

import pandas as pd
from sklearn.impute import KNNImputer

try:
    from sklearn.experimental import enable_iterative_imputer  # noqa: F401
    from sklearn.impute import IterativeImputer

    HAS_ITERATIVE_IMPUTER = True
except ImportError:
    HAS_ITERATIVE_IMPUTER = False

logger = logging.getLogger(__name__)

# Skewness threshold: if abs(skewness) exceeds this, use median instead of mean.
SKEWNESS_THRESHOLD = 1.0

VALID_STRATEGIES = {
    "median",
    "mean",
    "mode",
    "drop",
    "constant",
    "forward_fill",
    "ffill",
    "backward_fill",
    "bfill",
    "knn",
    "iterative_mice",
}


@dataclass
class CleaningLogEntry:
    """Detailed audit record for a specific cleaning operation on a dataset."""

    operation: str
    column: str
    affected_rows: int
    original_condition: str
    new_condition: str
    parameters: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CleaningResult:
    """Structured result returned by comprehensive dataset cleaning."""

    cleaned_df: pd.DataFrame
    log: list[CleaningLogEntry]
    total_duplicates_removed: int
    total_missing_imputed: int
    total_outliers_treated: int

    @property
    def log_messages(self) -> list[str]:
        """Human-readable log messages for dashboard and report rendering."""
        return [
            f"[{e.operation}] {e.column}: affected {e.affected_rows} rows ({e.original_condition} -> {e.new_condition})"
            for e in self.log
        ]


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with duplicate rows removed."""
    before = len(df)
    result = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(result)
    if removed > 0:
        logger.info("Removed %d duplicate row(s).", removed)
    else:
        logger.info("No duplicate rows found.")
    return result


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "median",
    fill_value: Any | None = None,
    n_neighbors: int = 5,
) -> pd.DataFrame:
    """Handle missing values using a specified strategy.

    Supported strategies:
    - ``median``: Skewness-aware median imputation for numeric; mode for categoricals.
    - ``mean``: Skewness-aware mean imputation for numeric; mode for categoricals.
    - ``mode``: Most frequent value imputation.
    - ``drop``: Drop all rows containing any null values.
    - ``constant``: Fill with a constant value (or default 0 / 'Unknown').
    - ``forward_fill`` / ``ffill``: Propagate last valid observation forward.
    - ``backward_fill`` / ``bfill``: Propagate next valid observation backward.
    - ``knn``: K-Nearest Neighbors multivariate imputation for numeric columns.
    - ``iterative_mice``: Multivariate Imputation by Chained Equations (MICE).
    """
    strategy = strategy.lower().strip()
    if strategy not in VALID_STRATEGIES:
        valid_str = ", ".join(sorted(VALID_STRATEGIES))
        raise ValueError(f"strategy must be one of: {valid_str} (got '{strategy}')")

    cleaned = df.copy()
    total_missing = int(cleaned.isna().sum().sum())
    logger.info(
        "Handling missing values: strategy='%s', total_missing=%d, shape=%s",
        strategy,
        total_missing,
        cleaned.shape,
    )

    if cleaned.empty or total_missing == 0:
        return cleaned

    if strategy == "drop":
        logger.info("Dropping rows with missing values.")
        return cleaned.dropna().reset_index(drop=True)

    if strategy in {"forward_fill", "ffill"}:
        return cleaned.ffill().bfill().reset_index(drop=True)

    if strategy in {"backward_fill", "bfill"}:
        return cleaned.bfill().ffill().reset_index(drop=True)

    if strategy == "constant":
        for col in cleaned.columns:
            if cleaned[col].isna().any():
                val = (
                    fill_value
                    if fill_value is not None
                    else (0 if pd.api.types.is_numeric_dtype(cleaned[col]) else "Unknown")
                )
                cleaned[col] = cleaned[col].fillna(val)
        return cleaned

    if strategy == "knn":
        return _impute_knn(cleaned, n_neighbors=n_neighbors)

    if strategy == "iterative_mice":
        return _impute_iterative(cleaned)

    # Standard univariate strategies
    for column in cleaned.columns:
        if not cleaned[column].isna().any():
            continue

        missing_count = int(cleaned[column].isna().sum())

        if pd.api.types.is_numeric_dtype(cleaned[column]):
            non_null = cleaned[column].dropna()
            if len(non_null) == 0:
                logger.warning("Column '%s' is entirely null. Filling with 0.", column)
                cleaned[column] = cleaned[column].fillna(0)
                continue

            skewness = float(non_null.skew()) if len(non_null) > 2 else 0.0
            if strategy in {"median", "mean"} and abs(skewness) > SKEWNESS_THRESHOLD:
                calc_val = cleaned[column].median()
                logger.info(
                    "Column '%s': skewed (skew=%.2f), using median=%.2f (requested '%s'). Filling %d null(s).",
                    column,
                    skewness,
                    calc_val,
                    strategy,
                    missing_count,
                )
            elif strategy == "median":
                calc_val = cleaned[column].median()
                logger.info("Column '%s': using median=%.2f. Filling %d null(s).", column, calc_val, missing_count)
            elif strategy == "mean":
                calc_val = cleaned[column].mean()
                logger.info("Column '%s': using mean=%.2f. Filling %d null(s).", column, calc_val, missing_count)
            else:  # mode
                modes = cleaned[column].mode(dropna=True)
                calc_val = modes.iloc[0] if not modes.empty else 0
                logger.info("Column '%s': using mode=%s. Filling %d null(s).", column, calc_val, missing_count)
        else:
            modes = cleaned[column].mode(dropna=True)
            calc_val = modes.iloc[0] if not modes.empty else "Unknown"
            logger.info("Column '%s': using mode='%s'. Filling %d null(s).", column, calc_val, missing_count)

        cleaned[column] = cleaned[column].fillna(calc_val)

    logger.info("Missing value handling complete. Remaining nulls: %d.", int(cleaned.isna().sum().sum()))
    return cleaned


def _impute_knn(df: pd.DataFrame, n_neighbors: int = 5) -> pd.DataFrame:
    """Impute numeric columns with KNN; impute categorical columns with mode."""
    cleaned = df.copy()
    numeric_cols = list(cleaned.select_dtypes(include="number").columns)
    cat_cols = [c for c in cleaned.columns if c not in numeric_cols]

    for c in cat_cols:
        if cleaned[c].isna().any():
            modes = cleaned[c].mode(dropna=True)
            mode_val = modes.iloc[0] if not modes.empty else "Unknown"
            cleaned[c] = cleaned[c].fillna(mode_val)

    if numeric_cols and cleaned[numeric_cols].isna().any().any():
        k = min(n_neighbors, max(1, len(cleaned) - 1))
        imputer = KNNImputer(n_neighbors=k)
        imputed_array = imputer.fit_transform(cleaned[numeric_cols])
        cleaned[numeric_cols] = pd.DataFrame(imputed_array, columns=numeric_cols, index=cleaned.index)

    return cleaned


def _impute_iterative(df: pd.DataFrame) -> pd.DataFrame:
    """Impute numeric columns with MICE / IterativeImputer; categoricals with mode."""
    cleaned = df.copy()
    numeric_cols = list(cleaned.select_dtypes(include="number").columns)
    cat_cols = [c for c in cleaned.columns if c not in numeric_cols]

    for c in cat_cols:
        if cleaned[c].isna().any():
            modes = cleaned[c].mode(dropna=True)
            mode_val = modes.iloc[0] if not modes.empty else "Unknown"
            cleaned[c] = cleaned[c].fillna(mode_val)

    if numeric_cols and cleaned[numeric_cols].isna().any().any():
        if HAS_ITERATIVE_IMPUTER:
            imputer = IterativeImputer(random_state=42, max_iter=10)
            imputed_array = imputer.fit_transform(cleaned[numeric_cols])
            cleaned[numeric_cols] = pd.DataFrame(imputed_array, columns=numeric_cols, index=cleaned.index)
        else:
            return _impute_knn(cleaned)

    return cleaned


def winsorize_outliers(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    lower_percentile: float = 0.01,
    upper_percentile: float = 0.99,
) -> tuple[pd.DataFrame, list[CleaningLogEntry]]:
    """Clip extreme values in numeric columns between specified percentiles (Winsorization)."""
    cleaned = df.copy()
    numeric_cols = columns or list(cleaned.select_dtypes(include="number").columns)
    log_entries: list[CleaningLogEntry] = []

    for col in numeric_cols:
        if col not in cleaned.columns or not pd.api.types.is_numeric_dtype(cleaned[col]):
            continue
        series = cleaned[col].dropna()
        if len(series) < 3:
            continue

        lower_bound = float(series.quantile(lower_percentile))
        upper_bound = float(series.quantile(upper_percentile))

        outliers_lower = int((cleaned[col] < lower_bound).sum())
        outliers_upper = int((cleaned[col] > upper_bound).sum())
        total_affected = outliers_lower + outliers_upper

        if total_affected > 0:
            cleaned[col] = cleaned[col].clip(lower=lower_bound, upper=upper_bound)
            log_entries.append(
                CleaningLogEntry(
                    operation="Winsorization",
                    column=str(col),
                    affected_rows=total_affected,
                    original_condition=f"Values outside [{lower_bound:.2f}, {upper_bound:.2f}]",
                    new_condition=(
                        f"Clipped to bounds at P({lower_percentile * 100:.0f}) and P({upper_percentile * 100:.0f})"
                    ),
                    parameters={"lower_percentile": lower_percentile, "upper_percentile": upper_percentile},
                )
            )

    return cleaned, log_entries


def clean_dataset(
    df: pd.DataFrame,
    missing_strategy: str = "median",
    handle_outliers: str = "none",  # "none", "winsorize"
    drop_duplicate_rows: bool = True,
    fill_value: Any | None = None,
) -> CleaningResult:
    """Execute end-to-end cleaning pipeline with full audit trail tracking."""
    log: list[CleaningLogEntry] = []
    current_df = df.copy()

    # 1. Duplicates
    dup_removed = 0
    if drop_duplicate_rows:
        before_dup = len(current_df)
        current_df = remove_duplicates(current_df)
        dup_removed = before_dup - len(current_df)
        if dup_removed > 0:
            log.append(
                CleaningLogEntry(
                    operation="Remove Duplicates",
                    column="<all_columns>",
                    affected_rows=dup_removed,
                    original_condition=f"{dup_removed} duplicate rows present",
                    new_condition="Exact duplicate rows removed",
                    parameters={"drop_duplicate_rows": True},
                )
            )

    # 2. Missing Values
    total_missing_before = int(current_df.isna().sum().sum())
    if total_missing_before > 0:
        missing_by_col = current_df.isna().sum()
        current_df = handle_missing_values(current_df, strategy=missing_strategy, fill_value=fill_value)
        for col, cnt in missing_by_col.items():
            if cnt > 0:
                log.append(
                    CleaningLogEntry(
                        operation=f"Imputation ({missing_strategy})",
                        column=str(col),
                        affected_rows=int(cnt),
                        original_condition=f"{cnt} missing values (NaN)",
                        new_condition=f"Imputed using '{missing_strategy}' strategy",
                        parameters={"strategy": missing_strategy},
                    )
                )

    # 3. Outlier handling
    outliers_treated = 0
    if handle_outliers == "winsorize":
        current_df, outlier_logs = winsorize_outliers(current_df)
        log.extend(outlier_logs)
        outliers_treated = sum(e.affected_rows for e in outlier_logs)

    return CleaningResult(
        cleaned_df=current_df,
        log=log,
        total_duplicates_removed=dup_removed,
        total_missing_imputed=total_missing_before,
        total_outliers_treated=outliers_treated,
    )
