# Architectural & Integration Notes
- **Inputs Expected**: Raw file paths (CSV/Excel) or dataframes, PipelineConfig configurations
- **Outputs Expected**: PipelineResult structured dataclass

### Code Signatures
```python
# src/autoanalyst/pipeline.py
from dataclasses import dataclass, field
import pandas as pd
from typing import Any, Literal

@dataclass
class PipelineConfig:
    target_column: str | None = None
    model_task: Literal["classification", "regression", "auto"] = "auto"
    missing_strategy: str = "median"
    encode_categoricals: bool = True
    model_test_size: float = 0.2
    random_state: int = 42

@dataclass
class PipelineResult:
    raw_df: pd.DataFrame
    cleaned_df: pd.DataFrame
    model_ready_df: pd.DataFrame
    profile: dict[str, Any]
    missing_values_report: pd.DataFrame
    insights: list[str] = field(default_factory=list)
    model_results: dict[str, Any] | None = None
    evaluation_results: dict[str, Any] | None = None

def run_analysis_pipeline(
    dataset: str | pd.DataFrame,
    config: PipelineConfig | None = None
) -> PipelineResult:
    """Orchestrates the execution of all team submodules."""
    pass
```
