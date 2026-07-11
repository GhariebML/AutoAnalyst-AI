import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from typing import Dict, Any, Tuple

class DriftDetector:
    """Detects feature drift using Kolmogorov-Smirnov statistical tests."""

    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level

    def detect_drift(
        self, 
        baseline_df: pd.DataFrame, 
        current_df: pd.DataFrame, 
        numerical_cols: list
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs Kolmogorov-Smirnov test on numerical features.
        Returns:
            drift_detected (bool): True if any feature has p-value < significance_level.
            report (dict): Summary of test statistics and p-values for each feature.
        """
        drift_detected = False
        report = {}

        for col in numerical_cols:
            if col not in baseline_df.columns or col not in current_df.columns:
                continue
            
            baseline_vals = baseline_df[col].dropna().values
            current_vals = current_df[col].dropna().values

            if len(baseline_vals) == 0 or len(current_vals) == 0:
                continue

            stat, p_value = ks_2samp(baseline_vals, current_vals)
            
            # If p-value is lower than our significance level, reject null hypothesis (distributions differ)
            feature_drifted = p_value < self.significance_level
            if feature_drifted:
                drift_detected = True

            report[col] = {
                "ks_statistic": float(stat),
                "p_value": float(p_value),
                "drift_detected": bool(feature_drifted)
            }

        return drift_detected, report
