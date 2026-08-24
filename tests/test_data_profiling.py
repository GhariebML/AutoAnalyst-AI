"""Unit tests for the Data Profiling module using pytest."""

import pytest
import pandas as pd
from autoanalyst.data_profiling.profiler import (
    generate_basic_profile,
    get_duplicate_count,
    get_missing_values_report,
    DataProfilingAgent,
)


def test_generate_basic_profile_valid():
    """Test profiling with a standard valid DataFrame."""
    df = pd.DataFrame({
        "age": [20, 30, 30],
        "income": [1000, 2000, 2000],
        "city": ["Cairo", "Giza", "Giza"]
    })
    
    profile = generate_basic_profile(df)
    
    assert profile["rows"] == 3
    assert profile["columns"] == 3
    assert "age" in profile["column_names"]
    assert profile["dtypes"]["age"] == "int64"
    assert profile["missing_values_total"] == 0
    # There is 1 duplicate row: index 2 is exact copy of index 1
    assert profile["duplicate_rows"] == 1
    
    # Ensure types are standard Python types
    assert isinstance(profile["rows"], int)
    assert isinstance(profile["columns"], int)
    assert isinstance(profile["missing_values_total"], int)
    assert isinstance(profile["duplicate_rows"], int)


def test_generate_basic_profile_empty():
    """Test that profiling an empty DataFrame raises ValueError."""
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError, match="Cannot profile an empty DataFrame"):
        generate_basic_profile(empty_df)


def test_get_duplicate_count():
    """Test duplicate count function."""
    df = pd.DataFrame({
        "A": [1, 2, 2, 3],
        "B": ["a", "b", "b", "c"]
    })
    assert get_duplicate_count(df) == 1


def test_get_missing_values_report():
    """Test missing values report generation."""
    df = pd.DataFrame({
        "A": [1, None, 3],
        "B": ["a", "b", None]
    })
    
    report = get_missing_values_report(df)
    assert len(report) == 2
    
    a_row = report[report["column"] == "A"].iloc[0]
    b_row = report[report["column"] == "B"].iloc[0]
    
    assert a_row["missing_count"] == 1
    assert abs(a_row["percentage"] - 33.33) < 0.1
    assert b_row["missing_count"] == 1


def test_profiling_agent_recommendations():
    """Test that the agent correctly generates recommendations based on data issues."""
    df = pd.DataFrame({
        "constant_col": [1, 1, 1, 1],
        "missing_col": [1, None, None, None],  # 75% missing
        "normal_cat": ["A", "B", "A", "B"],
        "normal_num": [10.0, 12.0, 15.0, 11.0],
        "dups": [1, 1, 1, 1]
    })
    
    agent = DataProfilingAgent(df)
    quality = agent.analyze_data_quality()
    recs = agent.generate_recommendations()
    
    assert len(quality["constant_columns"]) >= 2
    assert "constant_col" in quality["constant_columns"]
    assert "dups" in quality["constant_columns"]
    
    # Check that recommendations address the specific issues
    assert any("constant column" in r for r in recs)
    assert any("75.0% missing values" in r for r in recs)
    assert any("One-Hot Encoding" in r for r in recs)
