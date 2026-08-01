# Architectural & Integration Notes
- **Inputs Expected**: Clean, model-ready features and target variables
- **Outputs Expected**: Trained estimator instances and prediction arrays

### Code Signatures
```python
# src/autoanalyst/modeling/classification.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class ClassificationModel:
    def __init__(self, random_state: int = 42):
        self.model = RandomForestClassifier(random_state=random_state)
        
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Trains RandomForestClassifier on stratified splits."""
        pass
        
    def predict(self, X: pd.DataFrame):
        pass
```
