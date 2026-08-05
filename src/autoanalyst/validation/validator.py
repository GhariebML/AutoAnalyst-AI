"""Module 2 — Dataset Validation.

Runs a battery of structural/quality checks against a freshly-loaded
DataFrame and returns a `ValidationReport` with status, errors, warnings,
and recommendations. Errors indicate the dataset cannot be safely profiled
as-is (e.g. truly empty); warnings are non-blocking quality concerns that
still allow profiling to proceed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from autoanalyst.exceptions import EmptyDatasetError
from autoanalyst.utils.helpers import (
    get_logger,
    is_effectively_boolean,
    is_effectively_numeric_object,
)

logger = get_logger(__name__)

_VALID_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_OUTLIER_NAME_LENGTH = 64


@dataclass
class ValidationReport:
    status: str = "passed"  # passed | passed_with_warnings | failed
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_recommendation(self, msg: str) -> None:
        self.recommendations.append(msg)

    def finalize(self) -> "ValidationReport":
        if self.errors:
            self.status = "failed"
        elif self.warnings:
            self.status = "passed_with_warnings"
        else:
            self.status = "passed"
        return self

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


class DatasetValidator:
    """Runs structural and quality validation checks on a DataFrame."""

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        report = ValidationReport()

        self._check_empty_dataset(df, report)  # raises if fatal
        self._check_headers(df, report)
        self._check_duplicate_columns(df, report)

        if self._has_duplicate_columns(df):
            # Duplicate column names make `df[col]` return a DataFrame
            # instead of a Series, which breaks every per-column check
            # below. The duplicate-name error above already tells the
            # caller what to fix, so skip deeper checks until resolved.
            report.add_warning(
                "Skipping deeper per-column validation until duplicate column names are resolved."
            )
            return report.finalize()

        self._check_unsupported_names(df, report)
        self._check_empty_columns(df, report)
        self._check_mixed_types(df, report)
        self._check_infinite_values(df, report)
        self._check_nan_values(df, report)
        self._check_object_numeric(df, report)
        self._check_boolean_like(df, report)
        self._check_datetime_like(df, report)
        self._check_encoding_issues(df, report)
        self._check_outlier_name_length(df, report)
        self._check_constant_columns(df, report)

        return report.finalize()

    # ------------------------------------------------------------ checks --
    def _has_duplicate_columns(self, df: pd.DataFrame) -> bool:
        return pd.Series(df.columns).duplicated().any()

    def _check_empty_dataset(self, df: pd.DataFrame, report: ValidationReport) -> None:
        if df is None or df.shape[0] == 0 or df.shape[1] == 0:
            raise EmptyDatasetError(
                f"Dataset is empty (rows={0 if df is None else df.shape[0]}, "
                f"columns={0 if df is None else df.shape[1]})."
            )

    def _check_headers(self, df: pd.DataFrame, report: ValidationReport) -> None:
        cols = list(df.columns)
        unnamed = [c for c in cols if str(c).lower().startswith("unnamed:") or str(c).strip() == ""]
        if unnamed:
            report.add_warning(f"{len(unnamed)} column(s) appear to be missing proper headers: {unnamed[:5]}")
            report.add_recommendation("Rename unnamed columns or verify the header row was read correctly.")
        if all(isinstance(c, int) for c in cols):
            report.add_warning("Columns are integer-indexed; the source file may lack a header row.")

    def _check_duplicate_columns(self, df: pd.DataFrame, report: ValidationReport) -> None:
        cols = pd.Series(df.columns)
        dupes = cols[cols.duplicated()].unique().tolist()
        if dupes:
            report.add_error(f"Duplicate column names detected: {dupes}")
            report.add_recommendation("Rename or drop duplicate columns before analysis to avoid ambiguous references.")

    def _check_unsupported_names(self, df: pd.DataFrame, report: ValidationReport) -> None:
        bad = [c for c in df.columns if not _VALID_NAME_RE.match(str(c))]
        if bad:
            report.add_warning(
                f"{len(bad)} column name(s) contain spaces/special characters and may need "
                f"sanitising for downstream ML libraries: {bad[:5]}"
            )
            report.add_recommendation("Consider snake_case column names (e.g. 'Customer ID' -> 'customer_id').")

    def _check_empty_columns(self, df: pd.DataFrame, report: ValidationReport) -> None:
        empty_cols = [c for c in df.columns if df[c].isna().all()]
        if empty_cols:
            report.add_warning(f"{len(empty_cols)} column(s) are entirely empty (100% missing): {empty_cols[:10]}")
            report.add_recommendation(f"Drop fully-empty columns: {empty_cols[:10]}")

    def _check_mixed_types(self, df: pd.DataFrame, report: ValidationReport) -> None:
        mixed = []
        for col in df.select_dtypes(include="object").columns:
            sample = df[col].dropna()
            if sample.empty:
                continue
            types_seen = sample.map(lambda v: type(v).__name__).unique()
            if len(types_seen) > 1:
                mixed.append((col, list(types_seen)))
        if mixed:
            names = [m[0] for m in mixed]
            report.add_warning(f"{len(mixed)} column(s) contain mixed Python types: {names[:5]}")
            report.add_recommendation("Cast mixed-type columns to a single consistent dtype.")

    def _check_infinite_values(self, df: pd.DataFrame, report: ValidationReport) -> None:
        num_df = df.select_dtypes(include=[np.number])
        if num_df.empty:
            return
        inf_mask = np.isinf(num_df.to_numpy(dtype="float64", na_value=0.0))
        if inf_mask.any():
            cols_with_inf = num_df.columns[inf_mask.any(axis=0)].tolist()
            report.add_warning(f"Infinite values detected in column(s): {cols_with_inf}")
            report.add_recommendation("Replace +/-inf with NaN or clip to a reasonable range before modeling.")

    def _check_nan_values(self, df: pd.DataFrame, report: ValidationReport) -> None:
        total_missing = int(df.isna().sum().sum())
        total_cells = df.shape[0] * df.shape[1]
        if total_missing == 0:
            return
        pct_missing = (total_missing / total_cells) * 100 if total_cells else 0
        if pct_missing > 40:
            report.add_warning(f"Dataset-wide missingness is high: {pct_missing:.1f}% of all cells are NaN.")
            report.add_recommendation("Investigate systemic data collection gaps before imputing.")

    def _check_object_numeric(self, df: pd.DataFrame, report: ValidationReport) -> None:
        offenders = [
            c for c in df.select_dtypes(include="object").columns
            if is_effectively_numeric_object(df[c])
        ]
        if offenders:
            report.add_warning(
                f"{len(offenders)} object column(s) appear to store numbers as text: {offenders[:5]}"
            )
            report.add_recommendation(f"Convert to numeric dtype (strip currency/thousands separators): {offenders[:5]}")

    def _check_boolean_like(self, df: pd.DataFrame, report: ValidationReport) -> None:
        offenders = [
            c for c in df.columns
            if df[c].dtype != bool and is_effectively_boolean(df[c])
        ]
        if offenders:
            report.add_recommendation(f"Column(s) look boolean and could be cast to bool: {offenders[:5]}")

    def _check_datetime_like(self, df: pd.DataFrame, report: ValidationReport) -> None:
        from autoanalyst.utils.helpers import is_effectively_datetime

        offenders = []
        for c in df.select_dtypes(include="object").columns:
            try:
                if is_effectively_datetime(df[c]):
                    offenders.append(c)
            except Exception:  # noqa: BLE001
                continue
        if offenders:
            report.add_recommendation(f"Column(s) look like datetimes stored as text: {offenders[:5]}")

    def _check_encoding_issues(self, df: pd.DataFrame, report: ValidationReport) -> None:
        suspicious_markers = ("\ufffd", "Ã", "â€", "\x00")
        offenders = []
        for c in df.select_dtypes(include="object").columns:
            sample = df[c].dropna().astype(str).head(200)
            if sample.empty:
                continue
            if sample.str.contains("|".join(re.escape(m) for m in suspicious_markers), regex=True).any():
                offenders.append(c)
        if offenders:
            report.add_warning(f"Possible string encoding artifacts detected in: {offenders[:5]}")
            report.add_recommendation("Re-load with an explicit encoding (e.g. 'latin-1' or 'cp1252') and verify text integrity.")

    def _check_outlier_name_length(self, df: pd.DataFrame, report: ValidationReport) -> None:
        long_names = [c for c in df.columns if len(str(c)) > _OUTLIER_NAME_LENGTH]
        if long_names:
            report.add_warning(f"{len(long_names)} column name(s) are unusually long (>{_OUTLIER_NAME_LENGTH} chars).")

    def _check_constant_columns(self, df: pd.DataFrame, report: ValidationReport) -> None:
        constant = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
        if constant:
            report.add_warning(f"{len(constant)} column(s) have a single unique value (no variance): {constant[:10]}")
            report.add_recommendation(f"Consider dropping zero-variance columns: {constant[:10]}")
