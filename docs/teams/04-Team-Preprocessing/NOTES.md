# Architectural & Integration Notes
- **Inputs Expected**: Raw datasets containing nulls and categorical features
- **Outputs Expected**: Preprocessed, clean, encoded DataFrames ready for estimator fits

### Code Signatures
```python
# src/autoanalyst/preprocessing/cleaner.py
import pandas as pd

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    pass

def handle_missing_values(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Imputes missing cells. Strategies: mean, median, mode, drop."""
    pass
```
