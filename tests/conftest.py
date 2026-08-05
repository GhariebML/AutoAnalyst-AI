import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make src importable without installation.
SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))


@pytest.fixture
def sample_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 300
    df = pd.DataFrame({
        "customer_id": range(1, n + 1),
        "age": rng.integers(18, 80, n).astype(float),
        "income": np.round(rng.exponential(scale=40000, size=n), 2),
        "signup_date": pd.date_range("2022-01-01", periods=n, freq="D"),
        "gender": rng.choice(["Male", "Female"], n),
        "churn": rng.choice(["Yes", "No"], n, p=[0.2, 0.8]),
        "notes": ["Customer feedback text sample number " + str(i) for i in range(n)],
        "is_active": rng.choice([True, False], n),
        "constant_col": ["same_value"] * n,
    })
    # Inject some missingness and duplicates.
    df.loc[rng.choice(n, 15, replace=False), "income"] = np.nan
    df.loc[rng.choice(n, 5, replace=False), "age"] = np.nan
    df = pd.concat([df, df.iloc[:5]], ignore_index=True)
    return df


@pytest.fixture
def sample_csv_path(tmp_path, sample_df) -> str:
    path = tmp_path / "sample.csv"
    sample_df.to_csv(path, index=False)
    return str(path)
