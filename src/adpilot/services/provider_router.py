"""Enterprise LLM Provider Router."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional


from ..providers.openai_provider import OpenAIProvider
from ..providers.openrouter_provider import OpenRouterProvider
from ..providers.anthropic_provider import AnthropicProvider
from ..providers.ollama_provider import OllamaProvider
from ..providers.huggingface_provider import HuggingFaceProvider
from ..providers.base import LLMProvider
from ..core.config import get_config
from .cost_tracker import CostTrackingCallbackHandler

logger = logging.getLogger(__name__)


class ProviderRouter(LLMProvider):
    """Routes LLM requests to different providers with fallbacks and retries."""

    def __init__(self) -> None:
        self.config = get_config()
        self.openrouter = OpenRouterProvider()
        self.openai = OpenAIProvider()
        self.anthropic = AnthropicProvider()
        self.ollama = OllamaProvider()
        self.huggingface = HuggingFaceProvider()

        # The active primary provider chosen in config
        self.primary_provider_name = self.config.llm_provider.strip().lower()

    def get_model(self) -> Any:
        """Return a wrapper that routes requests dynamically."""
        return RoutedModelWrapper(self, self.primary_provider_name)

    def get_structured_output_kwargs(self) -> dict:
        """Handled internally by the active provider in RoutedModelWrapper."""
        return {}


class RoutedModelWrapper:
    """Wrapper that mimics a LangChain ChatModel and handles automatic routing."""

    def __init__(
        self, 
        router: ProviderRouter, 
        primary_provider_name: str, 
        structured_schema: Any = None, 
        structured_kwargs: Dict[str, Any] = None
    ) -> None:
        self.router = router
        self.primary_provider_name = primary_provider_name
        self.structured_schema = structured_schema
        self.structured_kwargs = structured_kwargs or {}

    def with_structured_output(self, schema: Any, **kwargs: Any) -> "RoutedModelWrapper":
        """Configure structured output and return self/new wrapper."""
        return RoutedModelWrapper(
            router=self.router,
            primary_provider_name=self.primary_provider_name,
            structured_schema=schema,
            structured_kwargs=kwargs
        )
        
    def with_fallbacks(self, fallbacks: Any) -> "RoutedModelWrapper":
        """Mock method since we handle fallbacks internally."""
        return self

    async def _execute_with_retry(self, provider, messages, config, **kwargs):
        """Execute a provider with exponential backoff."""
        max_retries = 3
        backoff_delays = [1, 2, 4]

        # Check if HF is disabled/selected
        if provider == self.router.huggingface and self.primary_provider_name != "huggingface":
            raise ValueError("HuggingFace is disabled by default for automatic routing.")

        for attempt in range(max_retries + 1):
            try:
                # Prepare the provider model
                model = provider.get_model()
                
                # Apply structured output if requested
                if self.structured_schema:
                    p_kwargs = provider.get_structured_output_kwargs()
                    # Merge structured kwargs
                    merged_kwargs = {**p_kwargs, **self.structured_kwargs}
                    model = model.with_structured_output(self.structured_schema, **merged_kwargs)
                
                # Set up cost tracking callback
                # We extract agent name and campaign id from prompt_values if available, 
                # but since we are at model execution, kwargs might contain tags or metadata.
                # Since kwargs might not have campaign_id, we just default to 'unknown' if not injected earlier.
                # Cost tracking uses CostTrackingCallbackHandler
                tracker = CostTrackingCallbackHandler(
                    campaign_id="unknown_campaign", 
                    agent_name="unknown_agent",
                    provider_name=provider.__class__.__name__,
                    model_name=self.router.config.openai_model if provider == self.router.openai else self.router.config.openrouter_model if provider == self.router.openrouter else self.router.config.anthropic_model if provider == self.router.anthropic else self.router.config.ollama_model if provider == self.router.ollama else self.router.config.hf_model
                )
                
                # Append callback to config
                if config is None:
                    config = {"callbacks": [tracker]}
                else:
                    if "callbacks" not in config or config["callbacks"] is None:
                        config["callbacks"] = [tracker]
                    else:
                        if isinstance(config["callbacks"], list):
                            config["callbacks"].append(tracker)

                # Execute
                return await model.ainvoke(messages, config=config, **kwargs)

            except Exception as e:
                error_str = str(e).lower()
                logger.warning(f"Provider {provider.__class__.__name__} attempt {attempt + 1} failed: {e}")
                
                # Let specific HTTP errors bubble up immediately for routing unless it's just a transient timeout
                if "402" in error_str or "payment required" in error_str:
                    raise  # Bubble up immediately for router to handle
                if "429" in error_str or "rate limit" in error_str:
                    raise
                if "401" in error_str or "403" in error_str or "authentication" in error_str:
                    raise
                
                if attempt < max_retries:
                    delay = backoff_delays[attempt]
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise e

    async def ainvoke(self, input: Any, config: Optional[Any] = None, **kwargs: Any) -> Any:
        """Route the request based on provider failures."""
        
        # If HF is the primary provider manually configured, use it directly without fallback
        if self.primary_provider_name == "huggingface":
            try:
                return await self._execute_with_retry(self.router.huggingface, input, config, **kwargs)
            except Exception as e:
                if "402" in str(e) or "payment required" in str(e).lower():
                    raise Exception("402 Payment Required\n\nHuggingFace monthly credits exhausted.\nSwitching providers is recommended.")
                raise e

        # Standard Failover Logic
        # Predefined priority chain
        fallback_chain = [
            self.router.openrouter,
            self.router.openai,
            self.router.anthropic,
            self.router.ollama
        ]
        
        last_exception = None
        
        for provider in fallback_chain:
            try:
                return await self._execute_with_retry(provider, input, config, **kwargs)
            except Exception as e:
                last_exception = e
                logger.error(f"{provider.__class__.__name__} failed with: {e}")
                # Continue to the next provider in the chain
                logger.info(f"Falling back to next provider in chain...")
                
        # If all providers fail, raise the last exception
        raise last_exception

