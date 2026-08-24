"""End-to-end multi-agent pipeline stress and concurrency test suite."""

import numpy as np
import pandas as pd

from autoanalyst.agents.orchestrator import MasterOrchestrator


def generate_stress_dataset(n_rows: int = 500) -> pd.DataFrame:
    """Generate synthetic dataset for stress testing with mixed types, nulls, and outliers."""
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "feature_a": rng.normal(50, 15, size=n_rows),
            "feature_b": rng.exponential(10, size=n_rows),
            "feature_c": rng.choice(["North", "South", "East", "West", None], size=n_rows),
            "feature_d": rng.integers(1, 100, size=n_rows),
            "target": rng.normal(100, 25, size=n_rows),
        }
    )


def test_orchestrator_stress_execution():
    """Verify MasterOrchestrator executes full pipeline reliably under larger datasets."""
    df = generate_stress_dataset(250)
    orchestrator = MasterOrchestrator()

    final_state = orchestrator.run_analysis(
        dataset=df,
        target_column="target",
        require_approval=False,
    )

    assert final_state["status"] == "completed"
    assert final_state["profile"] is not None
    assert final_state["profile"]["rows"] == 250
    assert final_state["model_results"] is not None
    assert len(final_state["insights"]) > 0


def test_orchestrator_unsupervised_execution():
    """Verify orchestrator runs unsupervised EDA and clustering when target column is None."""
    df = generate_stress_dataset(60)
    orchestrator = MasterOrchestrator()

    final_state = orchestrator.run_analysis(
        dataset=df,
        target_column=None,
        require_approval=False,
    )

    assert final_state["status"] == "completed"
    assert final_state["profile"] is not None
    assert final_state["eda_results"] is not None
