"""
AutoAnalyst AI — Automated Data Profiling Engine
==================================================

Public entrypoint:

    from autoanalyst import profile_dataset
    result = profile_dataset("data.csv")

`result` is a ProfileResult object exposing `.to_dict()`, `.to_json()`,
`.to_html()`, `.to_markdown()`, and `.console_summary()`.
"""

from autoanalyst.engine import profile_dataset, AutoAnalystEngine
from autoanalyst.exceptions import (
    AutoAnalystError,
    FileAccessError,
    UnsupportedFileTypeError,
    EmptyDatasetError,
    DataLoadError,
    ValidationError,
)

__version__ = "1.0.0"

__all__ = [
    "profile_dataset",
    "AutoAnalystEngine",
    "AutoAnalystError",
    "FileAccessError",
    "UnsupportedFileTypeError",
    "EmptyDatasetError",
    "DataLoadError",
    "ValidationError",
]
