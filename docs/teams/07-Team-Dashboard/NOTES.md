# Architectural & Integration Notes
- **Inputs Expected**: PipelineResult outputs, configurations
- **Outputs Expected**: Local markdown files, interactive plotly dashboards

### Code Signatures
```python
# src/autoanalyst/reporting/report_generator.py
from pathlib import Path

def create_markdown_report(title: str, insights: list[str], output_path: str) -> Path:
    """Generates a formatted markdown file detailing key insights."""
    pass
```
