# Architectural & Integration Notes
- **Inputs Expected**: Local dataset filepath strings (CSV or Excel)
- **Outputs Expected**: Pandas DataFrame, and dict representing basic data shapes and types

### Code Signatures
```python
# src/autoanalyst/data_loading/loader.py
import pandas as pd

def load_csv(file_path: str, **kwargs) -> pd.DataFrame:
    """Loads CSV files into Pandas DataFrames safely."""
    pass

# src/autoanalyst/data_profiling/profiler.py
def generate_basic_profile(df: pd.DataFrame) -> dict[str, Any]:
    """Returns row count, column count, dtypes, duplicates, and missing count."""
    pass
```
