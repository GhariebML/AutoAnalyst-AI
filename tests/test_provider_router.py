"""Tests for ProviderRouter and fallback logic."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from adpilot.services.provider_router import ProviderRouter
from adpilot.core.config import AdPilotConfig


import os

@pytest.fixture
def mock_config(monkeypatch):
    """Return a configured AdPilotConfig for testing, completely ignoring .env."""
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-oa-test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("HF_TOKEN", "hf-test")
    
    # We pass _env_file=None so Pydantic doesn't read the .env file.
    return AdPilotConfig(_env_file=None)


class MockModel:
    def __init__(self):
        self.ainvoke_called = False
        self.ainvoke_result = "Success"
        self.ainvoke_error = None
        self.structured_called = False

    def with_structured_output(self, schema, **kwargs):
        self.structured_called = True
        return self

    async def ainvoke(self, *args, **kwargs):
        print(f"MockModel.ainvoke called! error={self.ainvoke_error}, result={self.ainvoke_result}")
        self.ainvoke_called = True
        if self.ainvoke_error:
            raise self.ainvoke_error
        return self.ainvoke_result


@pytest.fixture
def router(mock_config):
    """Return a ProviderRouter with mocked inner models."""
    with patch("adpilot.services.provider_router.get_config", return_value=mock_config):
        r = ProviderRouter()
        
        mock_models = {
            "openrouter": MockModel(),
            "openai": MockModel(),
            "anthropic": MockModel(),
            "ollama": MockModel(),
            "huggingface": MockModel()
        }
        
        with patch("adpilot.providers.openrouter_provider.OpenRouterProvider.get_model", return_value=mock_models["openrouter"]), \
             patch("adpilot.providers.openai_provider.OpenAIProvider.get_model", return_value=mock_models["openai"]), \
             patch("adpilot.providers.anthropic_provider.AnthropicProvider.get_model", return_value=mock_models["anthropic"]), \
             patch("adpilot.providers.ollama_provider.OllamaProvider.get_model", return_value=mock_models["ollama"]), \
             patch("adpilot.providers.huggingface_provider.HuggingFaceProvider.get_model", return_value=mock_models["huggingface"]):
             
            # Expose the mocks on the router for the tests to configure them easily
            r.mock_models = mock_models
            
            yield r


@pytest.mark.asyncio
async def test_openrouter_success(router):
    """Test primary provider success without fallback."""
    router.mock_models["openrouter"].ainvoke_result = "Success"
    wrapper = router.get_model()
    
    res = await wrapper.ainvoke("test")
    assert res == "Success"
    assert router.mock_models["openrouter"].ainvoke_called
    assert not router.mock_models["openai"].ainvoke_called


@pytest.mark.asyncio
async def test_openrouter_rate_limit_fallback_openai(router):
    """Test Rate Limit triggers OpenAI fallback."""
    print(f"\n--- test_openrouter_rate_limit_fallback_openai ---")
    mock_or = router.mock_models["openrouter"]
    mock_or.ainvoke_error = Exception("429 Rate Limit Exceeded")
    
    mock_oa = router.mock_models["openai"]
    mock_oa.ainvoke_result = "OpenAI Success"
    
    wrapper = router.get_model()
    with patch("asyncio.sleep", new_callable=AsyncMock):  # skip backoff sleep
        res = await wrapper.ainvoke("test")
        
    print(f"Test got res: {res}")
    assert res == "OpenAI Success"
    assert router.mock_models["openai"].ainvoke_called


@pytest.mark.asyncio
async def test_openrouter_payment_required_fallback_openai(router):
    """Test Payment Required triggers OpenAI fallback."""
    router.mock_models["openrouter"].ainvoke_error = Exception("402 Payment Required")
    router.mock_models["openai"].ainvoke_result = "OpenAI Success"
    
    wrapper = router.get_model()
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = await wrapper.ainvoke("test")
        
    assert res == "OpenAI Success"


@pytest.mark.asyncio
async def test_authentication_error_fallback_next(router):
    """Test Authentication Error triggers the next provider in chain (OpenAI)."""
    router.mock_models["openrouter"].ainvoke_error = Exception("401 Authentication Failed")
    router.mock_models["openai"].ainvoke_result = "OpenAI Success"
    
    wrapper = router.get_model()
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = await wrapper.ainvoke("test")
        
    assert res == "OpenAI Success"
    assert router.mock_models["openai"].ainvoke_called


@pytest.mark.asyncio
async def test_timeout_fallback_next(router):
    """Test Timeout triggers the next provider in chain (OpenAI)."""
    router.mock_models["openrouter"].ainvoke_error = Exception("APITimeoutError")
    router.mock_models["openai"].ainvoke_result = "OpenAI Success"
    
    wrapper = router.get_model()
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = await wrapper.ainvoke("test")
        
    assert res == "OpenAI Success"
    assert router.mock_models["openai"].ainvoke_called


@pytest.mark.asyncio
async def test_huggingface_disabled_by_default(router):
    """Test HF fails when explicitly used but disabled in config."""
    # HF is disabled in the config fixture because llm_provider="openrouter"
    router.mock_models["huggingface"].ainvoke_result = "Should not return"
    wrapper = router.get_model()
    
    with pytest.raises(ValueError, match="HuggingFace is disabled by default for automatic routing"):
        # We manually try to execute HF
        await wrapper._execute_with_retry(router.huggingface, "test", None)


@pytest.mark.asyncio
async def test_huggingface_payment_required_fails_fast(monkeypatch):
    """Test HF returns custom error message when credits exhausted without fallback."""
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    mock_config = AdPilotConfig(_env_file=None)
    with patch("adpilot.services.provider_router.get_config", return_value=mock_config):
        with patch("adpilot.providers.huggingface_provider.HuggingFaceProvider.get_model") as hf_mock:
            r = ProviderRouter()
            mock_model = MockModel()
            mock_model.ainvoke_error = Exception("402 Payment Required")
            hf_mock.return_value = mock_model
            
            wrapper = r.get_model()
            with pytest.raises(Exception, match="Switching providers is recommended"):
                await wrapper.ainvoke("test")


@pytest.mark.asyncio
async def test_missing_api_keys_fallbacks(router):
    """Test fallback chain works completely through to Ollama when keys fail."""
    # OR Rate limits, OpenAI Auth fails, Claude Rate limits -> Ollama
    router.mock_models["openrouter"].ainvoke_error = Exception("429 Rate Limit")
    router.mock_models["openai"].ainvoke_error = Exception("401 Auth Failed")
    router.mock_models["anthropic"].ainvoke_error = Exception("429 Rate Limit")
    router.mock_models["ollama"].ainvoke_result = "Ollama Rescue"
    
    wrapper = router.get_model()
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = await wrapper.ainvoke("test")
        
    assert res == "Ollama Rescue"
    assert router.mock_models["openrouter"].ainvoke_called
    assert router.mock_models["openai"].ainvoke_called
    assert router.mock_models["anthropic"].ainvoke_called
    assert router.mock_models["ollama"].ainvoke_called
