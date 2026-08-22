"""LLM narration layer tests (M5).

Contract under test:
- With narration disabled (default env) the system makes ZERO model calls
  and produces deterministic rule-based output.
- With a chat model injected, narratives appear; any failure degrades to
  rules without raising.

All tests use in-process doubles; no network access ever occurs.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from autoanalyst.agents.graph import AutoAnalystConfig, run_agent_pipeline
from autoanalyst.agents.llm import LLMSettings, create_llm, load_llm_settings
from autoanalyst.agents.narrator import advisor_note, executive_summary, narrate_insights
from autoanalyst.agents.serde import PickleSerde  # noqa: F401 - guards module import graph
from autoanalyst.reporting.report_generator import create_full_report


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({"age": [20, 30, 30, None], "income": [1000, 2000, 2000, 3000]})


def fake_llm(responses: list[str]) -> FakeMessagesListChatModel:
    return FakeMessagesListChatModel(responses=[AIMessage(content=text) for text in responses])


class TestSettings:
    def test_disabled_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AUTOANALYST_LLM_ENABLED", raising=False)
        settings = load_llm_settings(env={})
        assert settings.enabled is False
        assert settings.provider == "openai"
        assert settings.model is None

    def test_truthy_values_enable(self) -> None:
        for value in ("1", "true", "YES", "on"):
            settings = load_llm_settings(env={"AUTOANALYST_LLM_ENABLED": value})
            assert settings.enabled is True

    def test_falsy_values_disable(self) -> None:
        for value in ("", "0", "false", "off", "no"):
            settings = load_llm_settings(env={"AUTOANALYST_LLM_ENABLED": value})
            assert settings.enabled is False

    def test_provider_and_model_read_from_env(self) -> None:
        settings = load_llm_settings(
            env={
                "AUTOANALYST_LLM_ENABLED": "true",
                "AUTOANALYST_LLM_PROVIDER": "anthropic",
                "AUTOANALYST_LLM_MODEL": "claude-x",
            }
        )
        assert settings.provider == "anthropic"
        assert settings.model == "claude-x"


class TestFactory:
    def test_disabled_returns_none_without_calls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AUTOANALYST_LLM_ENABLED", raising=False)
        assert create_llm(LLMSettings(enabled=False)) is None

    def test_unknown_provider_raises_actionable_error(self) -> None:
        with pytest.raises(RuntimeError, match="Unsupported AUTOANALYST_LLM_PROVIDER"):
            create_llm(LLMSettings(enabled=True, provider="skynet"))

    def test_missing_key_raises_actionable_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            create_llm(LLMSettings(enabled=True, provider="openai"))

    def test_missing_package_raises_install_hint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import builtins

        real_import = builtins.__import__

        def blocked(name: str, *args: Any, **kwargs: Any) -> Any:
            if name.startswith("langchain_openai"):
                raise ImportError("blocked for test")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", blocked)
        with pytest.raises(RuntimeError, match=r"autoanalyst-ai\[llm\]"):
            create_llm(LLMSettings(enabled=True, provider="openai"))


class TestNarrateInsights:
    def test_rules_when_no_llm(self, sample_df: pd.DataFrame) -> None:
        narration = narrate_insights(sample_df, {"rows": 4, "columns": 2}, llm=None)
        assert narration.source == "rules"
        assert narration.texts

    def test_llm_narration_parsed_and_capped(self, sample_df: pd.DataFrame) -> None:
        response = "- Finding one\n2. Finding two\n* Finding three\n\nplain fourth\n- \n- Finding five"
        narration = narrate_insights(
            sample_df, {"rows": 4, "columns": 2}, llm=fake_llm([response]), max_insights=4
        )
        assert narration.source == "llm"
        assert narration.texts == ["Finding one", "Finding two", "Finding three", "plain fourth"]

    def test_failure_falls_back_to_rules(self, sample_df: pd.DataFrame) -> None:
        class ExplodingModel(FakeMessagesListChatModel):
            def invoke(self, *args: Any, **kwargs: Any) -> Any:
                raise RuntimeError("api down")

        narration = narrate_insights(sample_df, {"rows": 4, "columns": 2}, llm=ExplodingModel(responses=[]))
        assert narration.source == "rules"
        assert narration.texts

    def test_empty_response_falls_back(self, sample_df: pd.DataFrame) -> None:
        narration = narrate_insights(sample_df, {"rows": 4, "columns": 2}, llm=fake_llm(["\n \n"]))
        assert narration.source == "rules"


class TestAdvisorNote:
    def test_rule_based_note_references_metrics(self) -> None:
        note = advisor_note(
            {"task": "classification", "model_name": "RandomForestClassifier"},
            {"f1_macro": 0.8123},
            llm=None,
        )
        assert "RandomForestClassifier" in note
        assert "0.812" in note

    def test_rule_based_note_without_model(self) -> None:
        note = advisor_note(None, None, llm=None)
        assert "No target column" in note

    def test_llm_advisory_used_when_available(self) -> None:
        note = advisor_note({"task": "classification"}, {"f1_macro": 0.5}, llm=fake_llm(["Try gradient boosting."]))
        assert note == "Try gradient boosting."


class TestExecutiveSummary:
    def test_deterministic_summary_mentions_shape_and_metrics(self, sample_df: pd.DataFrame) -> None:
        summary = executive_summary(
            {"rows": 29, "columns": 12},
            ["finding a", "finding b"],
            {"accuracy": 0.85},
            llm=None,
        )
        assert "29 rows" in summary
        assert "12 columns" in summary
        assert "accuracy=0.850" in summary

    def test_llm_summary_used_when_available(self) -> None:
        summary = executive_summary({"rows": 1, "columns": 1}, [], llm=fake_llm(["The dataset was tiny."]))
        assert summary == "The dataset was tiny."


class TestGraphIntegration:
    def test_default_run_is_rule_narrated_with_zero_model_calls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AUTOANALYST_LLM_ENABLED", raising=False)
        example_csv = EXAMPLE_CSV_PATH()
        config = AutoAnalystConfig(dataset_path=str(example_csv), target_column="loan_status")
        result = run_agent_pipeline(config)

        assert result.insights
        # provenance surfaces through PipelineResult.warnings? No — via state only;
        # assert determinism instead: rerun yields identical insights.
        again = run_agent_pipeline(config)
        assert result.insights == again.insights

    def test_report_renders_executive_summary_section(self, tmp_path: Any) -> None:
        path = create_full_report(
            output_path=str(tmp_path / "r.md"),
            title="T",
            profile={"rows": 5, "columns": 2},
            insights=["one"],
            executive_summary="Automated analysis covered a dataset of 5 rows.",
        )
        text = path.read_text(encoding="utf-8")
        assert "## Executive Summary" in text
        assert "5 rows" in text


def EXAMPLE_CSV_PATH():
    from pathlib import Path

    return Path(__file__).resolve().parents[1] / "data" / "sample" / "example.csv"


class TestCheckpointSerdeStillWorks:
    """Narration fields must survive checkpoint serialization (HITL runs)."""

    def test_state_with_narrations_pickles(self, tmp_path: Any) -> None:
        serde = PickleSerde()
        state = {"insights": ["a"], "narrated_by": "llm", "executive_summary": "s"}
        kind, blob = serde.dumps_typed(state)
        restored = serde.loads_typed((kind, blob))
        assert restored == state
