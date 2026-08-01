# Architectural & Integration Notes
- **Inputs Expected**: Cleaned or raw Pandas DataFrames
- **Outputs Expected**: Descriptive statistics summaries and correlation dataframes

### Code Signatures
```python
# src/autoanalyst/eda/analyzer.py
import pandas as pd

def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generates descriptive statistics for all numeric columns (describe transpose)."""
    pass

def get_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Generates a correlation matrix for numeric features."""
    pass
```
