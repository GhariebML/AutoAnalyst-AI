"""Rule-based insight generation for datasets."""

import pandas as pd


def generate_dataset_insights(df: pd.DataFrame) -> list[str]:
    """Generate simple human-readable insights from a DataFrame."""
    if df.empty:
        return ["The dataset is empty. Please upload a dataset with rows and columns."]

    insights = [f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns."]
    missing_total = int(df.isna().sum().sum())
    if missing_total:
        insights.append(f"There are {missing_total} missing values that may need cleaning.")
    else:
        insights.append("No missing values were detected.")

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        insights.append(f"There are {duplicate_count} duplicate rows that may be removed.")

    numeric_columns = list(df.select_dtypes(include="number").columns)
    insights.append(f"The dataset has {len(numeric_columns)} numeric columns suitable for statistical analysis.")
    return insights
