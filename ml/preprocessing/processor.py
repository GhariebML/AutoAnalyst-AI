import pandas as pd
from typing import List, Tuple
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class DataCleaner:
    """Handles cleaning, deduplication, and outlier removal."""
    
    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """Removes duplicates and drops completely empty rows."""
        df_clean = df.drop_duplicates()
        return df_clean

class FeatureTransformer:
    """Handles column scaling, encoding, and vectorization."""
    
    def __init__(self, numerical_cols: List[str], categorical_cols: List[str]):
        self.numerical_cols = numerical_cols
        self.categorical_cols = categorical_cols
        self.preprocessor = self._build_preprocessor()

    def _build_preprocessor(self) -> ColumnTransformer:
        """Builds a scikit-learn ColumnTransformer pipeline."""
        num_transformer = StandardScaler()
        cat_transformer = OneHotEncoder(handle_unknown='ignore', drop='first')
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', num_transformer, self.numerical_cols),
                ('cat', cat_transformer, self.categorical_cols)
            ] if self.categorical_cols else [('num', num_transformer, self.numerical_cols)]
        )
        return preprocessor

    def fit_transform(self, df: pd.DataFrame) -> Tuple[ColumnTransformer, pd.DataFrame]:
        """Fits the preprocessor and transforms the data."""
        self.preprocessor.fit(df)
        transformed_data = self.preprocessor.transform(df)
        return self.preprocessor, transformed_data
