"""Modeling module for AutoAnalyst AI — Team 5.

Exports the three model wrappers and the comparison utilities so other
modules (pipeline.py, agents, tests) can import from one place.
"""

from autoanalyst.modeling.classification import ClassificationModel
from autoanalyst.modeling.clustering import ClusteringModel
from autoanalyst.modeling.regression import RegressionModel
from autoanalyst.modeling.comparator import (
    compare_classification_models,
    compare_regression_models,
)

__all__ = [
    "ClassificationModel",
    "RegressionModel",
    "ClusteringModel",
    "compare_classification_models",
    "compare_regression_models",
]
