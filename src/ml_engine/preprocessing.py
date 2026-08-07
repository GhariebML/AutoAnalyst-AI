"""Data preprocessing functions for the ML Engine.

Includes functions for cleaning data, encoding categorical columns,
scaling numeric features, and splitting datasets into train and test sets.
"""

import logging
from typing import Any, Literal
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler

logger = logging.getLogger(__name__)


def clean_data(
    df: pd.DataFrame,
    fill_strategy: str | dict[str, str] = "median",
    drop_duplicates: bool = True,
    outlier_method: Literal["iqr", "z_score"] | None = None,
) -> pd.DataFrame:
    """Clean the input DataFrame by handling duplicates, missing values, and outliers.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    fill_strategy : str or dict, default "median"
        Missing value imputation strategy.
        If str, must be one of: 'mean', 'median', 'mode', 'drop', or a constant (like 'missing').
        If dict, mapping of column name to its imputation strategy.
    drop_duplicates : bool, default True
        Whether to drop duplicate rows.
    outlier_method : {'iqr', 'z_score'}, optional
        Method to detect and clip outliers in numeric columns.

    Returns
    -------
    pd.DataFrame
        Cleaned copy of the input DataFrame.
    """
    if df is None:
        raise ValueError("Input DataFrame cannot be None.")
    
    cleaned = df.copy()

    # 1. Drop duplicates
    if drop_duplicates:
        initial_rows = len(cleaned)
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        dup_count = initial_rows - len(cleaned)
        if dup_count > 0:
            logger.info(f"Dropped {dup_count} duplicate rows.")

    if cleaned.empty:
        return cleaned

    # 2. Handle missing values
    if isinstance(fill_strategy, str):
        fill_strategy = fill_strategy.lower()
        if fill_strategy not in {"mean", "median", "mode", "drop"}:
            raise ValueError("fill_strategy must be one of: 'mean', 'median', 'mode', 'drop'.")
        
        if fill_strategy == "drop":
            cleaned = cleaned.dropna().reset_index(drop=True)
        else:
            for col in cleaned.columns:
                if not cleaned[col].isna().any():
                    continue
                if fill_strategy in {"mean", "median"} and pd.api.types.is_numeric_dtype(cleaned[col]):
                    val = cleaned[col].mean() if fill_strategy == "mean" else cleaned[col].median()
                else:
                    # Fallback to mode for categorical / non-numeric columns under mean/median, or for explicit mode
                    modes = cleaned[col].mode(dropna=True)
                    val = modes.iloc[0] if not modes.empty else "Unknown"
                cleaned[col] = cleaned[col].fillna(val)
                
    elif isinstance(fill_strategy, dict):
        for col, strat in fill_strategy.items():
            if col not in cleaned.columns:
                raise KeyError(f"Column '{col}' specified in fill_strategy not found in DataFrame.")
            if not cleaned[col].isna().any():
                continue
            
            strat_lower = strat.lower() if isinstance(strat, str) else ""
            
            if strat_lower == "drop":
                cleaned = cleaned.dropna(subset=[col]).reset_index(drop=True)
            elif strat_lower in {"mean", "median"} and pd.api.types.is_numeric_dtype(cleaned[col]):
                val = cleaned[col].mean() if strat_lower == "mean" else cleaned[col].median()
                cleaned[col] = cleaned[col].fillna(val)
            elif strat_lower == "mode" or (strat_lower in {"mean", "median"} and not pd.api.types.is_numeric_dtype(cleaned[col])):
                modes = cleaned[col].mode(dropna=True)
                val = modes.iloc[0] if not modes.empty else "Unknown"
                cleaned[col] = cleaned[col].fillna(val)
            else:
                # Custom fill constant
                cleaned[col] = cleaned[col].fillna(strat)
    else:
        raise ValueError("fill_strategy must be a string or a dictionary.")

    # 3. Handle outliers
    if outlier_method is not None:
        outlier_method = outlier_method.lower()
        if outlier_method not in {"iqr", "z_score"}:
            raise ValueError("outlier_method must be 'iqr' or 'z_score'.")
        
        numeric_cols = cleaned.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            col_data = cleaned[col]
            if col_data.nunique() <= 1:
                continue
            
            if outlier_method == "iqr":
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                cleaned[col] = np.clip(col_data, lower_bound, upper_bound)
            elif outlier_method == "z_score":
                mean_val = col_data.mean()
                std_val = col_data.std()
                if std_val > 0:
                    lower_bound = mean_val - 3 * std_val
                    upper_bound = mean_val + 3 * std_val
                    cleaned[col] = np.clip(col_data, lower_bound, upper_bound)

    return cleaned


def encode_features(
    df: pd.DataFrame,
    categorical_cols: list[str] | None = None,
    method: Literal["onehot", "label"] = "onehot",
) -> pd.DataFrame:
    """Encode categorical columns in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    categorical_cols : list of str, optional
        Specific categorical columns to encode. If None, auto-selects object, category, and bool columns.
    method : {'onehot', 'label'}, default "onehot"
        Encoding methodology.

    Returns
    -------
    pd.DataFrame
        DataFrame with encoded columns.
    """
    if df is None:
        raise ValueError("Input DataFrame cannot be None.")
    
    encoded = df.copy()
    
    if categorical_cols is None:
        # Include object, category, and bool columns
        categorical_cols = list(encoded.select_dtypes(include=["object", "category", "bool"]).columns)
        
    if not categorical_cols:
        return encoded

    # Ensure all specified columns exist
    for col in categorical_cols:
        if col not in encoded.columns:
            raise KeyError(f"Categorical column '{col}' not found in DataFrame.")

    method = method.lower()
    if method not in {"onehot", "label"}:
        raise ValueError("Encoding method must be 'onehot' or 'label'.")

    if method == "onehot":
        # Using get_dummies to perform onehot encoding. Convert boolean output to int for downstream models.
        encoded = pd.get_dummies(encoded, columns=categorical_cols, drop_first=False, dtype=int)
    elif method == "label":
        for col in categorical_cols:
            le = LabelEncoder()
            # Handle possible NaNs before encoding
            non_nulls = encoded[col].dropna()
            if len(non_nulls) < len(encoded):
                # Impute temporarily to allow encoding or raise error
                temp_series = encoded[col].fillna("Missing")
                encoded[col] = le.fit_transform(temp_series.astype(str))
            else:
                encoded[col] = le.fit_transform(encoded[col].astype(str))

    return encoded


def scale_features(
    df: pd.DataFrame,
    numeric_cols: list[str] | None = None,
    method: Literal["standard", "minmax"] = "standard",
) -> pd.DataFrame:
    """Scale numeric columns in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    numeric_cols : list of str, optional
        Specific columns to scale. If None, auto-detects all numeric columns.
    method : {'standard', 'minmax'}, default "standard"
        Scaling methodology.

    Returns
    -------
    pd.DataFrame
        DataFrame with scaled features.
    """
    if df is None:
        raise ValueError("Input DataFrame cannot be None.")
        
    scaled = df.copy()
    
    if numeric_cols is None:
        numeric_cols = list(scaled.select_dtypes(include=[np.number]).columns)

    if not numeric_cols:
        return scaled

    # Ensure all specified columns exist
    for col in numeric_cols:
        if col not in scaled.columns:
            raise KeyError(f"Numeric column '{col}' not found in DataFrame.")

    method = method.lower()
    if method not in {"standard", "minmax"}:
        raise ValueError("Scaling method must be 'standard' or 'minmax'.")

    scaler = StandardScaler() if method == "standard" else MinMaxScaler()
    scaled[numeric_cols] = scaler.fit_transform(scaled[numeric_cols].astype(float))

    return scaled


def split_data(
    df: pd.DataFrame,
    target_col: str,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split the DataFrame into train and test features and target.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    target_col : str
        Name of the target column.
    test_size : float, default 0.2
        Fraction of data to allocate to the test set.
    random_state : int, default 42
        Random state for reproducibility.
    stratify : bool, default False
        Whether to perform stratified splitting.

    Returns
    -------
    tuple of (X_train, X_test, y_train, y_test)
    """
    if df is None:
        raise ValueError("Input DataFrame cannot be None.")
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in DataFrame.")
    if test_size <= 0.0 or test_size >= 1.0:
        raise ValueError("test_size must be between 0.0 and 1.0 (exclusive).")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    stratify_y = None
    if stratify:
        # Safe stratification check:
        # 1. Target must have at least 2 classes.
        # 2. Minimum class frequency must be at least 2.
        # 3. Test split must be large enough to contain at least one of each class.
        class_counts = y.value_counts()
        if len(class_counts) < 2:
            logger.warning("Stratification requested but target has only 1 class. Proceeding without stratification.")
        elif class_counts.min() < 2:
            logger.warning("Stratification requested but some classes have less than 2 samples. Proceeding without stratification.")
        else:
            stratify_y = y

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_y
    )

    return X_train, X_test, y_train, y_test
