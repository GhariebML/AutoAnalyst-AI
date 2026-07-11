"""Safe tests for LangChain infrastructure."""

from __future__ import annotations

from adpilot.agents.strategy_agent import StrategyAgent
from adpilot.core.base_agent import BaseAgent
from adpilot.core.config import AdPilotConfig
from adpilot.schemas.agent_schemas import StrategyAgentInput, StrategyAgentOutput


def test_base_agent_class_exists() -> None:
    assert BaseAgent is not None
    assert hasattr(BaseAgent, "call_llm")


def test_strategy_agent_models() -> None:
    assert StrategyAgent.input_model is StrategyAgentInput
    assert StrategyAgent.output_model is StrategyAgentOutput


def test_config_loads_safely_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("TEMPERATURE", "0.1")
    monkeypatch.setenv("ENVIRONMENT", "test")

    settings = AdPilotConfig()

    assert settings.llm_provider == "openai"
    assert settings.openai_api_key == ""
    assert settings.openai_model == "test-model"
    assert settings.model_name == "test-model"
    assert settings.temperature == 0.1
    assert settings.environment == "test"
