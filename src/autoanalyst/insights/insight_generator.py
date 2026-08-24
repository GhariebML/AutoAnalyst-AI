"""Rule-based and heuristic insight generation for datasets and model results."""

from __future__ import annotations

from typing import Any

import pandas as pd


def generate_dataset_insights(
    df: pd.DataFrame,
    profile: dict[str, Any] | None = None,
    eda_results: dict[str, Any] | None = None,
    model_results: dict[str, Any] | None = None,
    evaluation_results: dict[str, Any] | None = None,
) -> list[str]:
    """Generate structured, actionable human-readable insights from dataset and pipeline outputs."""
    if df.empty:
        return ["The dataset is empty. Please upload a dataset with rows and columns."]

    insights: list[str] = []

    # 1. Dataset Scale & Structure
    insights.append(f"Dataset Dimension: Contains {df.shape[0]:,} rows across {df.shape[1]} columns.")

    # 2. Data Health & Completeness
    missing_total = int(df.isna().sum().sum())
    total_cells = df.shape[0] * df.shape[1]
    if missing_total > 0:
        missing_pct = (missing_total / total_cells * 100.0) if total_cells else 0.0
        insights.append(
            f"Missing Values: {missing_total:,} missing entries "
            f"({missing_pct:.1f}% of total data) identified requiring imputation."
        )
    else:
        insights.append("Data Completeness: Perfect completeness with zero missing values detected.")

    # 3. Duplicate Integrity
    duplicate_count = int(df.duplicated().sum())
    if duplicate_count > 0:
        insights.append(f"Integrity Alert: {duplicate_count:,} duplicate rows identified that should be deduplicated.")

    # 4. Feature Profile
    numeric_cols = list(df.select_dtypes(include="number").columns)
    cat_cols = list(df.select_dtypes(include=["object", "category", "string"]).columns)
    insights.append(
        f"Feature Composition: {len(numeric_cols)} numeric features and {len(cat_cols)} categorical attributes."
    )

    # 5. Correlation & Strong Relationships (from EDA)
    if eda_results and "correlation_matrix" in eda_results:
        corr = eda_results["correlation_matrix"]
        if isinstance(corr, pd.DataFrame) and corr.shape[0] > 1:
            # Find strongest non-diagonal correlation
            strong_pairs: list[tuple[str, str, float]] = []
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    val = float(corr.iloc[i, j])
                    if abs(val) >= 0.5:
                        strong_pairs.append((str(corr.columns[i]), str(corr.columns[j]), val))

            if strong_pairs:
                strong_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                top = strong_pairs[0]
                insights.append(
                    f"Strong Relationship: High correlation between '{top[0]}' and '{top[1]}' (r = {top[2]:.2f})."
                )

    # 6. Model & Predictive Performance
    if model_results and evaluation_results:
        task = model_results.get("task", "ML")
        model_name = model_results.get("model_name", "Champion Model")

        if task == "classification" and "accuracy" in evaluation_results:
            acc = evaluation_results["accuracy"] * 100.0
            f1 = evaluation_results.get("f1_macro", 0.0)
            insights.append(
                f"Model Benchmark: {model_name} achieved {acc:.1f}% accuracy "
                f"(Macro F1: {f1:.3f}) on holdout validation."
            )
        elif task == "regression" and "rmse" in evaluation_results:
            rmse = evaluation_results["rmse"]
            r2 = evaluation_results.get("r2", 0.0)
            insights.append(
                f"Model Benchmark: {model_name} achieved RMSE of {rmse:.3f} with R² explanatory power of {r2:.3f}."
            )

    return insights
