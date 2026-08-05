import numpy as np
import pandas as pd
import pytest

from autoanalyst.exceptions import EmptyDatasetError
from autoanalyst.validation.validator import DatasetValidator


def test_validate_normal_df(sample_df):
    validator = DatasetValidator()
    report = validator.validate(sample_df)
    assert report.status in ("passed", "passed_with_warnings")


def test_empty_dataset_raises():
    validator = DatasetValidator()
    with pytest.raises(EmptyDatasetError):
        validator.validate(pd.DataFrame())


def test_duplicate_columns_detected():
    df = pd.DataFrame([[1, 2]], columns=["a", "a"])
    validator = DatasetValidator()
    report = validator.validate(df)
    assert report.status == "failed"
    assert any("Duplicate column" in e for e in report.errors)


def test_constant_column_warning():
    df = pd.DataFrame({"x": [1, 1, 1, 1], "y": [1, 2, 3, 4]})
    validator = DatasetValidator()
    report = validator.validate(df)
    assert any("single unique value" in w for w in report.warnings)


def test_infinite_values_detected():
    df = pd.DataFrame({"x": [1.0, np.inf, 3.0], "y": [1, 2, 3]})
    validator = DatasetValidator()
    report = validator.validate(df)
    assert any("Infinite" in w for w in report.warnings)


def test_empty_column_detected():
    df = pd.DataFrame({"x": [np.nan, np.nan], "y": [1, 2]})
    validator = DatasetValidator()
    report = validator.validate(df)
    assert any("entirely empty" in w for w in report.warnings)
