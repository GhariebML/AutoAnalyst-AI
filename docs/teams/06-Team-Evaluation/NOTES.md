# Architectural & Integration Notes
- **Inputs Expected**: True target arrays, predictions, and datasets
- **Outputs Expected**: Metrics dictionary outputs and lists of insight strings

### Code Signatures
```python
# src/autoanalyst/evaluation/evaluator.py
from typing import Any

def evaluate_classification(y_true, y_pred) -> dict[str, Any]:
    """Calculates accuracy and returns scikit-learn classification report."""
    pass

# src/autoanalyst/insights/insight_generator.py
def generate_dataset_insights(df: pd.DataFrame) -> list[str]:
    """Generates descriptive textual insights of dataset anomalies."""
    pass
```
