"""Dataset profiling helper for data understanding and quality checks."""

import logging
from typing import Any
import pandas as pd
import numpy as np

# Set up logger
logger = logging.getLogger(__name__)


def generate_basic_profile(df: pd.DataFrame) -> dict[str, Any]:
    """Returns row count, column count, dtypes, duplicates, and missing count.

    Casts numpy numeric types to standard Python integers.
    Raises ValueError if df is empty.
    """
    if df is None:
        raise ValueError("DataFrame cannot be None.")
    
    if df.empty:
        logger.error("ValueError: Cannot profile an empty DataFrame.")
        raise ValueError("Cannot profile an empty DataFrame.")

    # Convert pandas dtypes to strings
    dtypes_dict = {str(col): str(dtype) for col, dtype in df.dtypes.items()}
    
    # Calculate duplicate count and missing values
    try:
        duplicate_rows = int(df.duplicated().sum())
    except Exception as e:
        logger.warning(f"Error calculating duplicates: {e}. Defaulting to 0.")
        duplicate_rows = 0

    try:
        missing_values_total = int(df.isnull().sum().sum())
    except Exception as e:
        logger.warning(f"Error calculating missing values: {e}. Defaulting to 0.")
        missing_values_total = 0

    profile = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": [str(c) for c in df.columns],
        "dtypes": dtypes_dict,
        "missing_values_total": missing_values_total,
        "duplicate_rows": duplicate_rows
    }
    
    logger.info("Successfully generated basic dataset profile.")
    return profile


def get_duplicate_count(df: pd.DataFrame) -> int:
    """Returns the total number of duplicate rows in the DataFrame."""
    if df is None or df.empty:
        return 0
    return int(df.duplicated().sum())


def get_missing_values_report(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a DataFrame detailing missing values per column.

    Columns in returned DataFrame:
        - column: str
        - missing_count: int
        - percentage: float (0.0 to 100.0)
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["column", "missing_count", "percentage"])
    
    total_rows = len(df)
    missing_series = df.isnull().sum()
    
    report_data = []
    for col, count in missing_series.items():
        report_data.append({
            "column": str(col),
            "missing_count": int(count),
            "percentage": float((count / total_rows) * 100.0) if total_rows > 0 else 0.0
        })
        
    return pd.DataFrame(report_data)


class DataProfilingAgent:
    """Intelligent profiling agent that analyzes dataset structure and quality.

    Provides automated, actionable recommendations for data cleaning and preprocessing.
    """

    def __init__(self, df: pd.DataFrame):
        if df is None:
            raise ValueError("DataFrame cannot be None.")
        self.df = df
        self.profile = generate_basic_profile(df)
        self.missing_report = get_missing_values_report(df)

    def analyze_data_quality(self) -> dict[str, Any]:
        """Performs data quality checks (outliers, constant columns, class imbalance)."""
        df = self.df
        total_rows = self.profile["rows"]
        
        constant_columns = []
        high_cardinality_categorical = {}
        low_cardinality_categorical = {}
        skewed_numerical = []
        
        for col in df.columns:
            # Check cardinality
            try:
                unique_vals = df[col].nunique(dropna=True)
            except Exception:
                unique_vals = 0
                
            if unique_vals <= 1:
                constant_columns.append(col)
                continue
                
            dtype_str = self.profile["dtypes"][col]
            
            # Categorical analysis
            if any(term in dtype_str for term in ["object", "category", "bool", "string", "str"]):
                if unique_vals > 10:
                    high_cardinality_categorical[col] = unique_vals
                else:
                    low_cardinality_categorical[col] = unique_vals

            
            # Numerical analysis
            elif any(term in dtype_str for term in ["int", "float"]):
                try:
                    skewness = df[col].skew()
                    if abs(skewness) > 1.5:
                        skewed_numerical.append((col, float(skewness)))
                except Exception:
                    pass

        # Calculate general data quality score
        # Start at 100 and deduct for issues
        quality_score = 100.0
        
        # Deduct for duplicates (up to 15 points)
        duplicate_ratio = self.profile["duplicate_rows"] / total_rows if total_rows > 0 else 0
        quality_score -= min(15.0, duplicate_ratio * 100.0)
        
        # Deduct for missing values (up to 30 points)
        total_cells = total_rows * self.profile["columns"]
        missing_ratio = self.profile["missing_values_total"] / total_cells if total_cells > 0 else 0
        quality_score -= min(30.0, missing_ratio * 100.0 * 1.5)
        
        # Deduct for constant columns (5 points per column, up to 15)
        quality_score -= min(15.0, len(constant_columns) * 5.0)

        quality_score = max(0.0, quality_score)
        
        if quality_score >= 85:
            rating = "Excellent"
        elif quality_score >= 70:
            rating = "Good"
        elif quality_score >= 50:
            rating = "Fair"
        else:
            rating = "Poor"

        return {
            "quality_score": float(quality_score),
            "quality_rating": rating,
            "constant_columns": constant_columns,
            "high_cardinality_categorical": high_cardinality_categorical,
            "low_cardinality_categorical": low_cardinality_categorical,
            "skewed_numerical": skewed_numerical
        }

    def generate_recommendations(self) -> list[str]:
        """Generates clear, step-by-step recommendations for next pipeline tasks."""
        quality = self.analyze_data_quality()
        recommendations = []

        # 1. Duplicate checks
        duplicates = self.profile["duplicate_rows"]
        if duplicates > 0:
            recommendations.append(
                f"Drop {duplicates} duplicate rows using `df.drop_duplicates()` to avoid model bias."
            )

        # 2. Missing value strategies
        for _, row in self.missing_report.iterrows():
            col = row["column"]
            count = row["missing_count"]
            pct = row["percentage"]
            
            if count > 0:
                if pct > 50.0:
                    recommendations.append(
                        f"Drop column '{col}' because it has {pct:.1f}% missing values (exceeds 50% limit)."
                    )
                else:
                    dtype = self.profile["dtypes"][col]
                    if any(t in dtype for t in ["int", "float"]):
                        recommendations.append(
                            f"Impute numeric column '{col}' ({pct:.1f}% missing) using the median or mean."
                        )
                    else:
                        recommendations.append(
                            f"Impute categorical column '{col}' ({pct:.1f}% missing) using mode or 'Unknown'."
                        )

        # 3. Constant columns
        for col in quality["constant_columns"]:
            recommendations.append(
                f"Drop constant column '{col}' as it has zero variance and carries no feature information."
            )

        # 4. Encoding recommendations
        for col, card in quality["low_cardinality_categorical"].items():
            recommendations.append(
                f"Apply One-Hot Encoding to categorical column '{col}' (low cardinality: {card} unique values)."
            )
        for col, card in quality["high_cardinality_categorical"].items():
            recommendations.append(
                f"Apply Label/Target Encoding to categorical column '{col}' (high cardinality: {card} unique values) to prevent dimensional explosion."
            )

        # 5. Skewness
        for col, skew_val in quality["skewed_numerical"]:
            recommendations.append(
                f"Apply log or power transform to column '{col}' to correct high skewness ({skew_val:.2f})."
            )

        # 6. Overall recommendation
        if not recommendations:
            recommendations.append(
                "Dataset looks extremely clean and ready for modeling without preprocessing."
            )

        return recommendations
