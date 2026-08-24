"""Module hardening tests (M4): EDA expansion, evaluation metrics, modeling, reporting."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from autoanalyst.eda.analyzer import (
    detect_outliers_iqr,
    get_categorical_frequencies,
    get_distribution_overview,
)
from autoanalyst.evaluation.evaluator import evaluate_classification, evaluate_regression
from autoanalyst.modeling.classification import ClassificationModel
from autoanalyst.modeling.regression import RegressionModel
from autoanalyst.reporting.report_generator import create_full_report


@pytest.fixture()
def outlier_df() -> pd.DataFrame:
    return pd.DataFrame({"value": [10, 12, 11, 13, 12, 11, 12, 500]})


class TestDistributionOverview:
    def test_returns_skew_and_kurtosis(self) -> None:
        overview = get_distribution_overview(pd.DataFrame({"a": [1, 2, 3, 4, 100]}))
        assert "skewness" in overview.columns
        assert "kurtosis" in overview.columns
        assert overview.loc["a", "skewness"] > 2

    def test_empty_numeric_raises(self) -> None:
        with pytest.raises(ValueError, match="[Nn]o numeric"):
            get_distribution_overview(pd.DataFrame({"cat": ["x"]}))


class TestOutlierDetectionIQR:
    def test_detects_single_outlier(self, outlier_df: pd.DataFrame) -> None:
        result = detect_outliers_iqr(outlier_df, "value")
        assert result["count"] == 1
        assert result["fraction"] > 0
        assert result["lower_bound"] < result["upper_bound"]
        assert 500 > result["upper_bound"]

    def test_no_outliers_in_symmetric_data(self) -> None:
        result = detect_outliers_iqr(pd.DataFrame({"v": [1, 2, 3, 4, 5]}), "v")
        assert result["count"] == 0

    def test_unknown_column_raises(self) -> None:
        with pytest.raises(KeyError, match="Column not found"):
            detect_outliers_iqr(pd.DataFrame({"a": [1]}), "missing")

    def test_non_numeric_raises(self) -> None:
        with pytest.raises(ValueError, match="numeric"):
            detect_outliers_iqr(pd.DataFrame({"cat": ["x", "y"]}), "cat")

    def test_all_null_raises(self) -> None:
        df = pd.DataFrame({"v": pd.Series([None, None], dtype="float64")})
        with pytest.raises(ValueError, match="no values"):
            detect_outliers_iqr(df, "v")


class TestCategoricalFrequencies:
    def test_counts_and_percentages(self) -> None:
        df = pd.DataFrame({"city": ["Cairo", "Cairo", "Giza", "Alex"]})
        table = get_categorical_frequencies(df, "city")
        assert list(table.iloc[0][["value", "count"]]) == ["Cairo", 2]
        assert table.iloc[0]["percent"] == 50.0
        assert len(table) == 3

    def test_unknown_column_raises(self) -> None:
        with pytest.raises(KeyError):
            get_categorical_frequencies(pd.DataFrame({"a": [1]}), "nope")


def _binary_case() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y_true = np.array([0, 0, 0, 1, 1, 1])
    y_pred = np.array([0, 0, 1, 1, 1, 1])
    y_proba = np.array([[0.9, 0.1], [0.8, 0.2], [0.7, 0.3], [0.2, 0.8], [0.1, 0.9], [0.4, 0.6]])
    return y_true, y_pred, y_proba


class TestClassificationMetrics:
    def test_flattened_metrics_present(self) -> None:
        y_true, y_pred, _ = _binary_case()
        metrics = evaluate_classification(y_true, y_pred)

        for key in ("accuracy", "precision_macro", "recall_macro", "f1_macro", "f1_weighted"):
            assert key in metrics
        cm = metrics["confusion_matrix"]
        assert np.asarray(cm).sum() == len(y_true)
        # one false positive, zero false negatives
        assert cm == [[2, 1], [0, 3]]

    def test_roc_auc_with_probabilities(self) -> None:
        y_true, y_pred, y_proba = _binary_case()
        metrics = evaluate_classification(y_true, y_pred, y_proba=y_proba)
        # every positive scores higher than every negative -> perfect ranking
        assert metrics["roc_auc"] == pytest.approx(1.0)

    def test_roc_auc_omitted_without_proba_or_single_class(self) -> None:
        y_true, y_pred, _ = _binary_case()
        assert "roc_auc" not in evaluate_classification(y_true, y_pred)
        single = evaluate_classification(np.zeros(3), np.zeros(3), y_proba=np.full((3, 2), 0.5), labels=[0, 1])
        assert "roc_auc" not in single
        # explicit labels keep the matrix well-shaped for degenerate splits
        assert np.asarray(single["confusion_matrix"]).shape == (2, 2)

    def test_multiclass_auc_macro_ovr(self) -> None:
        rng = np.random.default_rng(7)
        proba = rng.dirichlet([1, 1, 1], size=30)
        y_true = np.argmax(proba, axis=1)
        metrics = evaluate_classification(y_true, y_true, y_proba=proba)
        assert metrics["roc_auc"] > 0.99


class TestRegressionMetrics:
    def test_rmse_is_sqrt_mse(self) -> None:
        y = pd.Series([1.0, 2.0, 3.0])
        pred = pd.Series([1.0, 2.0, 4.0])
        metrics = evaluate_regression(y, pred)
        assert metrics["rmse"] == pytest.approx(metrics["mse"] ** 0.5)
        assert {"mae", "mse", "r2"} <= set(metrics)


def _tiny_xy() -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(42)
    X = pd.DataFrame({"x1": range(60), "x2": [float(v % 7) for v in range(60)]})
    signal = (X["x1"] * 0.3 + X["x2"] + rng.normal(0, 0.5, 60)).to_numpy()
    y = pd.Series(np.where(signal > np.median(signal), "high", "low"), name="label")
    return X, y


class TestModelHyperparameters:
    def test_kwargs_override_estimator_params(self) -> None:
        model = ClassificationModel(n_estimators=7, max_depth=3)
        assert model.model.get_params()["n_estimators"] == 7
        assert model.model.get_params()["max_depth"] == 3

    def test_regression_kwargs_override(self) -> None:
        model = RegressionModel(n_estimators=5)
        assert model.model.get_params()["n_estimators"] == 5


class TestCrossValidation:
    def test_classification_cv_aggregates(self) -> None:
        X, y = _tiny_xy()
        scores = ClassificationModel(n_estimators=10).cross_validate(X, y, cv=3)
        assert scores["folds"] == 3
        assert 0 <= scores["accuracy_mean"] <= 1
        assert scores["f1_macro_std"] >= 0

    def test_regression_cv_aggregates(self) -> None:
        # stationary target so tree interpolation (not extrapolation) is tested
        rng = np.random.default_rng(0)
        X = pd.DataFrame({"x": rng.uniform(0, 100, size=150)})
        y = pd.Series((X["x"] % 20).to_numpy() + rng.normal(0, 0.5, 150))
        scores = RegressionModel(n_estimators=25).cross_validate(X, y, cv=3)
        # trees approximate the steep sawtooth only approximately; 0.5 shows
        # real signal capture without over-constraining the fixture
        assert scores["r2_mean"] > 0.5
        assert scores["rmse_mean"] >= 0


class TestPersistence:
    def test_classifier_save_load_roundtrip(self, tmp_path: Path) -> None:
        X, y = _tiny_xy()
        original = ClassificationModel(n_estimators=10)
        original.train(X, y, test_size=0.2)
        path = original.save(tmp_path / "model.joblib")

        restored = ClassificationModel.load(path)
        sample = X.head(5)
        np.testing.assert_array_equal(original.predict(sample), restored.predict(sample))

    def test_regressor_save_load_roundtrip(self, tmp_path: Path) -> None:
        X = pd.DataFrame({"x": np.arange(40, dtype=float)})
        y = pd.Series(np.arange(40, dtype=float) * 3)
        original = RegressionModel(n_estimators=10)
        original.train(X, y, test_size=0.25)
        path = original.save(tmp_path / "reg.joblib")

        restored = RegressionModel.load(path)
        np.testing.assert_allclose(original.predict(X.head(3)), restored.predict(X.head(3)))


class TestFullReport:
    def test_complete_report_contains_all_sections(self, tmp_path: Path, outlier_df: pd.DataFrame) -> None:
        profile = {"rows": 29, "columns": 3, "duplicate_rows": 0}
        eda_results = {
            "numeric_summary": get_distribution_overview(outlier_df),
            "correlation_matrix": pd.DataFrame({"value": [1.0]}, index=["value"]),
        }
        evaluation = evaluate_classification(*_binary_case()[:2], y_proba=_binary_case()[2])
        path = create_full_report(
            output_path=str(tmp_path / "full.md"),
            title="Full Report",
            profile=profile,
            insights=["Dataset has outliers."],
            missing_report=pd.DataFrame({"column": ["a"], "missing_count": [0], "missing_percent": [0.0]}),
            eda_results=eda_results,
            cleaning_log=["Removed 1 duplicate row(s)."],
            model_results={"task": "classification", "model_name": "RandomForestClassifier"},
            evaluation_results=evaluation,
            warnings=["High-cardinality column detected."],
        )

        text = path.read_text(encoding="utf-8")
        for section in (
            "# Full Report",
            "## Dataset Overview",
            "## Missing Values",
            "## Exploratory Analysis — Numeric Summary",
            "### Correlation Matrix",
            "## Cleaning Log",
            "## Model Results",
            "## Evaluation Metrics",
            "**Confusion matrix**",
            "**Per-class metrics**",
            "## Key Insights",
            "## Warnings",
        ):
            assert section in text, f"missing section: {section}"

    def test_minimal_report_only_required_sections(self, tmp_path: Path) -> None:
        path = create_full_report(
            output_path=str(tmp_path / "min.md"),
            title="Minimal",
            profile={},
            insights=[],
        )
        text = path.read_text(encoding="utf-8")
        assert "## Key Insights" in text
        assert "_No insights generated._" in text
        assert "## Model Results" not in text

    def test_empty_title_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="title"):
            create_full_report(output_path=str(tmp_path / "x.md"), title="", profile={}, insights=[])


class TestGraphIntegrationM4:
    def test_golden_run_surfaces_new_capabilities(self) -> None:
        example_csv = Path(__file__).resolve().parents[1] / "data" / "sample" / "example.csv"
        if not example_csv.exists():
            pytest.skip("data/sample/example.csv not present")
        from autoanalyst.agents.graph import AutoAnalystConfig, run_agent_pipeline

        report_path = example_csv.parent.parent / "reports" / "_m4_smoke.md"
        result = run_agent_pipeline(
            AutoAnalystConfig(
                dataset_path=str(example_csv),
                target_column="loan_status",
                report_path=str(report_path),
            )
        )

        assert "f1_macro" in result.evaluation_results
        assert "confusion_matrix" in result.evaluation_results
        text = (Path(result.report_path)).read_text(encoding="utf-8")
        assert "## Evaluation Metrics" in text
        report_path.unlink(missing_ok=True)
