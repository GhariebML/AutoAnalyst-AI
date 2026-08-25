"""Autonomous decision engine for the Modeling Agent (Team 5).

``ModelDecider`` inspects a cleaned DataFrame, the optional target column,
and an optional profiling report, then decides:

1. **Task type**   – classification, regression, or clustering.
2. **Algorithm**   – the best-fit scikit-learn estimator for this data.
3. **Hyperparameters** – sensible defaults adjusted for data characteristics.
4. **Splitting strategy** – whether to stratify the train/test split.

The decider is intentionally *rule-based* so the system works without any
LLM API key.  An optional LLM reasoning layer can be layered on top later
(Phase C in the architecture plan).

Decision rules are transparent and logged so the Evaluation Agent and the
end-user can understand *why* a particular model was chosen.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ── Type aliases ──────────────────────────────────────────────────────────────
TaskType = Literal["classification", "regression", "clustering"]


@dataclass
class DecisionResult:
    """Structured output produced by :class:`ModelDecider`."""

    task_type: TaskType
    """The inferred machine-learning task."""

    primary_algorithm: str
    """Recommended primary algorithm identifier (e.g. ``"random_forest"``)."""

    comparison_algorithms: list[str]
    """Additional algorithms to train for comparison purposes."""

    hyperparameters: dict[str, Any]
    """Recommended hyperparameters for the primary algorithm."""

    stratify: bool
    """Whether to use stratified train/test splitting."""

    decision_log: list[str] = field(default_factory=list)
    """Step-by-step log explaining every decision made."""


class ModelDecider:
    """Rule-based decision engine that selects the optimal modelling strategy.

    Parameters
    ----------
    df:
        The cleaned, encoded, numeric-only DataFrame ready for modelling.
    target_column:
        Name of the target column.  Pass ``None`` to force clustering mode.
    profile:
        Optional profiling dict produced by the Profiling Agent.  Used to
        extract missing-value counts and cardinality stats.
    random_state:
        Global random seed for reproducibility.
    """

    # ── Thresholds ────────────────────────────────────────────────────────────
    _REGRESSION_CARDINALITY_THRESHOLD: int = 15
    """Unique-value count above which a numeric target is treated as continuous."""

    _SMALL_DATASET_THRESHOLD: int = 300
    """Row count below which simpler models are preferred."""

    _LARGE_DATASET_THRESHOLD: int = 10_000
    """Row count above which scalable models are preferred."""

    _IMBALANCE_THRESHOLD: float = 0.15
    """Minimum frequency of the minority class (fraction of total).
    Below this, class-imbalance correction is applied."""

    def __init__(
        self,
        df: pd.DataFrame,
        target_column: str | None = None,
        profile: dict[str, Any] | None = None,
        random_state: int = 42,
    ) -> None:
        self._df = df
        self._target_column = target_column
        self._profile = profile or {}
        self._random_state = random_state
        self._log: list[str] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def decide(self) -> DecisionResult:
        """Run the full decision pipeline and return a :class:`DecisionResult`."""
        self._log.clear()

        task = self._infer_task()
        self._log.append(f"Inferred task type: '{task}'.")

        if task == "clustering":
            return self._decide_clustering()
        if task == "classification":
            return self._decide_classification()
        return self._decide_regression()

    # ── Task inference ────────────────────────────────────────────────────────

    def _infer_task(self) -> TaskType:
        """Determine whether the problem is classification, regression, or clustering."""
        if self._target_column is None or self._target_column not in self._df.columns:
            self._log.append(
                "No target column found → switching to unsupervised clustering."
            )
            return "clustering"

        target: pd.Series = self._df[self._target_column]

        # Categorical dtype or object → classification
        if not pd.api.types.is_numeric_dtype(target):
            self._log.append(
                f"Target '{self._target_column}' is non-numeric "
                f"(dtype={target.dtype}) → classification."
            )
            return "classification"

        # Numeric but low cardinality → classification
        n_unique = int(target.nunique())
        if n_unique <= self._REGRESSION_CARDINALITY_THRESHOLD:
            self._log.append(
                f"Target '{self._target_column}' is numeric but has only "
                f"{n_unique} unique values (≤{self._REGRESSION_CARDINALITY_THRESHOLD}) → classification."
            )
            return "classification"

        self._log.append(
            f"Target '{self._target_column}' is numeric with {n_unique} unique "
            f"values → regression."
        )
        return "regression"

    # ── Classification decisions ──────────────────────────────────────────────

    def _decide_classification(self) -> DecisionResult:
        target = self._df[self._target_column]  # type: ignore[index]
        n_rows, n_features = self._df.shape
        n_classes = int(target.nunique())
        imbalance_ratio = self._compute_imbalance_ratio(target)
        stratify = self._can_stratify(target)

        self._log.append(
            f"Dataset: {n_rows} rows × {n_features} cols, "
            f"{n_classes} classes, imbalance_ratio={imbalance_ratio:.2%}."
        )

        # ── Algorithm selection ───────────────────────────────────────────────
        if n_rows < self._SMALL_DATASET_THRESHOLD:
            primary = "logistic_regression"
            comparison = ["decision_tree", "random_forest"]
            self._log.append(
                f"Small dataset ({n_rows} rows) → prefer 'logistic_regression' "
                f"(fast, interpretable)."
            )
        else:
            primary = "random_forest"
            comparison = ["logistic_regression", "decision_tree"]
            self._log.append(
                f"Medium/large dataset ({n_rows} rows) → prefer 'random_forest' "
                f"(robust, handles non-linearity)."
            )

        # ── Hyperparameters ───────────────────────────────────────────────────
        hp: dict[str, Any] = {"random_state": self._random_state}
        if primary == "random_forest":
            hp["n_estimators"] = 200 if n_rows >= self._LARGE_DATASET_THRESHOLD else 100
            hp["max_depth"] = None
            if imbalance_ratio < self._IMBALANCE_THRESHOLD:
                hp["class_weight"] = "balanced"
                self._log.append(
                    f"Class imbalance detected (minority={imbalance_ratio:.2%}) → "
                    f"setting class_weight='balanced'."
                )
        elif primary == "logistic_regression":
            hp["max_iter"] = 1000
            hp["solver"] = "lbfgs"
            # multi_class removed in sklearn 1.9+
            if imbalance_ratio < self._IMBALANCE_THRESHOLD:
                hp["class_weight"] = "balanced"

        if stratify:
            self._log.append("Stratified train/test split will be used.")
        else:
            self._log.append(
                "Stratification skipped (class frequency too low for safe split)."
            )

        return DecisionResult(
            task_type="classification",
            primary_algorithm=primary,
            comparison_algorithms=comparison,
            hyperparameters=hp,
            stratify=stratify,
            decision_log=list(self._log),
        )

    # ── Regression decisions ──────────────────────────────────────────────────

    def _decide_regression(self) -> DecisionResult:
        n_rows, n_features = self._df.shape
        self._log.append(
            f"Dataset: {n_rows} rows × {n_features} cols."
        )

        if n_rows < self._SMALL_DATASET_THRESHOLD:
            primary = "linear_regression"
            comparison = ["ridge", "random_forest"]
            self._log.append(
                f"Small dataset ({n_rows} rows) → prefer 'linear_regression' "
                f"(interpretable, no overfitting risk on small sets)."
            )
        else:
            primary = "random_forest"
            comparison = ["linear_regression", "ridge"]
            self._log.append(
                f"Medium/large dataset ({n_rows} rows) → prefer 'random_forest' "
                f"(captures non-linear relationships)."
            )

        # linear_regression does not accept random_state
        hp: dict[str, Any] = {} if primary == "linear_regression" else {"random_state": self._random_state}
        if primary == "random_forest":
            hp["n_estimators"] = 200 if n_rows >= self._LARGE_DATASET_THRESHOLD else 100
            hp["max_depth"] = None

        return DecisionResult(
            task_type="regression",
            primary_algorithm=primary,
            comparison_algorithms=comparison,
            hyperparameters=hp,
            stratify=False,
            decision_log=list(self._log),
        )

    # ── Clustering decisions ──────────────────────────────────────────────────

    def _decide_clustering(self) -> DecisionResult:
        n_rows, n_features = self._df.shape
        self._log.append(
            f"Dataset: {n_rows} rows × {n_features} cols (no target column)."
        )

        # Heuristic for k: sqrt(n / 2) clamped to [2, 10]
        k = int(np.clip(round(np.sqrt(n_rows / 2)), 2, 10))
        self._log.append(
            f"Estimated number of clusters k={k} using √(n/2) heuristic."
        )

        hp: dict[str, Any] = {
            "n_clusters": k,
            "random_state": self._random_state,
            "n_init": 10,
        }

        return DecisionResult(
            task_type="clustering",
            primary_algorithm="kmeans",
            comparison_algorithms=["agglomerative"],
            hyperparameters=hp,
            stratify=False,
            decision_log=list(self._log),
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _compute_imbalance_ratio(target: pd.Series) -> float:
        """Return the frequency of the minority class as a fraction of total."""
        counts = target.value_counts(normalize=True)
        return float(counts.min()) if not counts.empty else 1.0

    @staticmethod
    def _can_stratify(target: pd.Series) -> bool:
        """Return True only when every class has ≥2 samples AND ≥2 classes exist."""
        counts = target.value_counts()
        return bool(
            len(counts) >= 2          # at least 2 distinct classes
            and (counts >= 2).all()   # every class has ≥2 samples
        )
