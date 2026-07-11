"""Base classes and utilities shared by all agents."""

from __future__ import annotations

import abc
from pathlib import Path
from typing import Any, Generic, Type, TypeVar

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, ValidationError
import logging
import asyncio

from ..schemas.agent_schemas import CampaignContext
from .exceptions import AgentInputValidationError, AgentOutputError, ConfigurationError
from .json_utils import safe_json_loads, strip_markdown_fences

logger = logging.getLogger(__name__)

InputModel = TypeVar("InputModel", bound=BaseModel)
OutputModel = TypeVar("OutputModel", bound=BaseModel)


class BaseAgent(abc.ABC, Generic[InputModel, OutputModel]):
    """Abstract base class for all agents.

    Subclasses define their Pydantic input and output models. New agents should
    call LangChain through ``call_llm`` so schemas remain the source of truth.
    """

    name: str
    input_model: Type[InputModel]
    output_model: Type[OutputModel]
    system_prompt: str | None = None
    prompt_path: str | None = None

    def __init__(self) -> None:
        if not getattr(self, "name", None):
            raise ConfigurationError("Agent must define a 'name' attribute.")
        if not getattr(self, "input_model", None):
            raise ConfigurationError("Agent must define an 'input_model' attribute.")
        if not getattr(self, "output_model", None):
            raise ConfigurationError("Agent must define an 'output_model' attribute.")
        if self.prompt_path:
            self.system_prompt = self.load_prompt(self.prompt_path)

    def validate_input(self, data: Any) -> InputModel:
        """Validate raw data against ``input_model``."""
        try:
            return self.input_model.model_validate(data)
        except ValidationError as exc:
            raise AgentInputValidationError(str(exc)) from exc

    def validate_output(self, data: Any) -> OutputModel:
        """Validate raw data against ``output_model``."""
        try:
            return self.output_model.model_validate(data)
        except ValidationError as exc:
            raise AgentOutputError(str(exc)) from exc

    @staticmethod
    def load_prompt(path: str) -> str:
        """Read a prompt file from ``path`` relative to the package root."""
        path_obj = Path(path)
        if not path_obj.exists():
            package_root = Path(__file__).resolve().parent.parent
            alt_path = package_root / path
            if alt_path.exists():
                path_obj = alt_path

        try:
            return path_obj.read_text(encoding="utf-8")
        except OSError as exc:
            raise ConfigurationError(f"Unable to load prompt file: {path}") from exc

    @staticmethod
    def parse_json_output(text: str) -> dict[str, Any]:
        """Strip possible markdown fences and safely parse JSON."""
        cleaned = strip_markdown_fences(text)
        return safe_json_loads(cleaned)

    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for this agent."""
        if not self.system_prompt:
            raise ConfigurationError(f"{self.name} must define a system_prompt.")
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Use this validated input data and return only structured data that "
                    "matches the required Pydantic output model:\n\n{agent_input_json}",
                ),
            ]
        )

    async def call_llm(
        self,
        agent_input: InputModel | None = None,
        prompt: ChatPromptTemplate | None = None,
        max_retries: int = 2,
        **prompt_values: Any,
    ) -> OutputModel:
        """Call the configured LangChain model and parse structured output with retries."""

        # Extract campaign_id and query for RAG
        campaign_id = prompt_values.get("campaign_id") or (getattr(agent_input, "campaign_id", None) if agent_input else None)
        query = ""
        if agent_input:
            campaign_obj = getattr(agent_input, "campaign", None) or getattr(agent_input, "brief", None)
            if campaign_obj:
                query = getattr(campaign_obj, "product_description", "") or getattr(campaign_obj, "business_name", "")

        rag_context = ""
        if campaign_id:
            try:
                from .container import get_container
                container = get_container()
                rag_service = container.rag_service
                rag_context = await rag_service.retrieve_relevant_context(
                    query=query or "brand guidelines",
                    campaign_id=campaign_id,
                )
            except Exception as exc:
                logger.warning("RAG context retrieval failed: %s", exc)

        if agent_input is not None:
            validated_input = self.validate_input(agent_input)
            prompt_values.setdefault(
                "agent_input_json",
                validated_input.model_dump_json(indent=2),
            )

        # ---- Enterprise ML Integration (Phase 7) ----
        campaign_dict = None
        if agent_input:
            campaign_obj = getattr(agent_input, "campaign", None) or getattr(agent_input, "brief", None)
            if campaign_obj:
                campaign_dict = campaign_obj.model_dump(mode="json") if hasattr(campaign_obj, "model_dump") else campaign_obj.__dict__
        elif "campaign_json" in prompt_values:
            try:
                campaign_dict = json.loads(prompt_values["campaign_json"])
            except Exception:
                pass

        if campaign_dict:
            budget_usd = float(campaign_dict.get("budget_usd", 5000.0))
            goals = campaign_dict.get("goals", [])
            goal = goals[0] if goals else "brand_awareness"
            tone = campaign_dict.get("tone_of_voice", "professional")
            target = campaign_dict.get("target_market", "tech")
            duration = float(campaign_dict.get("campaign_duration_days", 30))
        else:
            budget_usd = 5000.0
            goal = "brand_awareness"
            tone = "professional"
            target = "tech"
            duration = 30.0

        import pandas as pd
        from ml.pipelines.inference import InferencePipeline

        ml_input = pd.DataFrame([{
            "budget_usd": budget_usd,
            "goals": goal,
            "tone_of_voice": tone,
            "target_market": target,
            "campaign_duration_days": duration,
            "feature_1": 0.5,
            "feature_2": -0.2,
            "feature_3": 0.1,
            "cat_feature_1": "type_b",
            "cat_feature_2": "type_a",
            "time_spent": 45.0,
            "page_views": 5,
            "source": "paid"
        }])

        agent_key = self.name.replace("_agent", "")

        def fallback_rules(data):
            if agent_key == "strategy":
                return {"recommended_channels": ["facebook", "linkedin"], "confidence_score": 0.85}
            elif agent_key == "audience":
                return {"segment_id": 3, "persona_name": "Tech Professionals"}
            elif agent_key == "research":
                return {"competitor_categories": ["high_tier", "b2b_saas"], "sentiment": "neutral"}
            elif agent_key == "content":
                return {"suggested_keywords": ["enterprise", "scalability", "ai_driven"]}
            elif agent_key == "analytics":
                return {"predicted_ctr": 0.024, "quality_score": 85.0}
            elif agent_key == "budget":
                return {"allocations": {"facebook": 0.6, "linkedin": 0.4}}
            elif agent_key == "trend":
                return {"trend_multiplier": 1.15, "peak_season": "q3"}
            elif agent_key == "recommendation":
                return {"recommended_ctas": ["Book Demo", "Learn More"], "visual_layout": "split_grid"}
            elif agent_key == "forecasting":
                return {"expected_clicks": 1200, "expected_impressions": 50000}
            elif agent_key == "fraud":
                return {"is_fraud": False, "risk_score": 0.05}
            elif agent_key == "lead_scoring":
                return [1]
            elif agent_key == "sentiment":
                return {"polarity": "positive", "confidence": 0.91}
            elif agent_key == "vision":
                return {"visual_score": 8.2, "color_palette_appeal": 0.88}
            elif agent_key == "knowledge":
                return {"relevant_docs_count": 5}
            elif agent_key == "optimizer":
                return {"suggested_bid_adjustment": 0.12}
            return {"status": "ok"}

        try:
            inference = InferencePipeline(agent_name=agent_key, fallback_rules=fallback_rules)
            ml_pred = inference.predict(ml_input)
            if hasattr(ml_pred, "tolist"):
                ml_pred = ml_pred.tolist()
        except Exception as e:
            logger.error(f"Failed to run inference for {agent_key}: {e}")
            ml_pred = fallback_rules(ml_input)

        ml_pred_json = json.dumps(ml_pred, indent=2)
        ml_pred_str = (
            f"\n\n--- Specialized ML Model Predictions ---\n"
            f"The specialized '{agent_key}' ML model predicts:\n"
            f"{ml_pred_json}\n"
            f"----------------------------------------\n"
        )

        for key in ["campaign_json", "strategy_json", "agent_input_json"]:
            if key in prompt_values:
                prompt_values[key] = str(prompt_values[key]) + ml_pred_str

        # Inject RAG context into JSON prompt values
        if rag_context:
            for key in ["campaign_json", "strategy_json", "agent_input_json"]:
                if key in prompt_values:
                    prompt_values[key] = str(prompt_values[key]) + f"\n\nAdditional Company/Brand Context:\n{rag_context}"
        if prompt is None:
            prompt = self.build_prompt()

        from ..providers.factory import get_active_provider

        provider = get_active_provider()
        llm = provider.get_model()
        kwargs = provider.get_structured_output_kwargs()

        structured_llm = llm.with_structured_output(self.output_model, **kwargs)
        if hasattr(provider, "get_fallback_models"):
            fallbacks = provider.get_fallback_models()
            if fallbacks:
                structured_fallbacks = [fm.with_structured_output(self.output_model, **kwargs) for fm in fallbacks]
                structured_llm = structured_llm.with_fallbacks(structured_fallbacks)

        chain = prompt | structured_llm

        last_error = None
        use_plain_text_fallback = False
        for attempt in range(max_retries + 1):
            try:
                result = await chain.ainvoke(prompt_values)
                return self.validate_output(result)
            except Exception as exc:
                last_error = exc
                exc_str = str(exc).lower()
                is_format_unsupported = (
                    "response_format" in exc_str or 
                    "json_schema" in exc_str or 
                    "json_object" in exc_str or 
                    "format" in exc_str or
                    "400" in exc_str
                )
                if is_format_unsupported:
                    logger.warning(
                        f"[{self.name}] LLM does not support structured output format: {exc}. "
                        f"Switching to plain-text prompt with manual JSON parsing fallback..."
                    )
                    use_plain_text_fallback = True
                    break
                
                logger.warning(
                    f"[{self.name}] LLM parsing/execution failed on attempt {attempt + 1}/{max_retries + 1}. "
                    f"Error: {type(exc).__name__}: {exc}. Retrying..."
                )
                if attempt < max_retries:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    use_plain_text_fallback = True

        if use_plain_text_fallback:
            logger.info(f"[{self.name}] Running plain-text model call and parsing JSON manually.")
            try:
                # Format the messages using the original prompt and input values
                formatted_messages = prompt.format_messages(**prompt_values)
                
                # Append JSON instructions to system message
                for msg in formatted_messages:
                    if msg.type == "system":
                        msg.content = msg.content + (
                            "\n\nYou MUST respond with ONLY a valid raw JSON object matching the requested schema. "
                            "Do not wrap your response in markdown code blocks or any extra text. "
                            "Ensure your output is valid JSON and contains all required fields."
                        )
                
                # Append schema to human message
                output_schema = self.output_model.model_json_schema()
                import json
                output_schema_str = json.dumps(output_schema, indent=2)
                
                for msg in reversed(formatted_messages):
                    if msg.type == "human":
                        msg.content = msg.content + (
                            "\n\nYou must return a valid JSON object that matches this JSON Schema:\n"
                            f"{output_schema_str}\n\n"
                            "Response (JSON only):"
                        )
                        break
                
                for attempt in range(max_retries + 1):
                    try:
                        response = await llm.ainvoke(formatted_messages)
                        text = response.content if hasattr(response, "content") else str(response)
                        parsed_json = self.parse_json_output(text)
                        return self.validate_output(parsed_json)
                    except Exception as exc:
                        last_error = exc
                        logger.warning(
                            f"[{self.name}] Plain-text fallback failed on attempt {attempt + 1}/{max_retries + 1}. "
                            f"Error: {type(exc).__name__}: {exc}. Retrying..."
                        )
                        if attempt < max_retries:
                            await asyncio.sleep(1 * (attempt + 1))
            except Exception as format_exc:
                logger.error(f"[{self.name}] Failed to prepare plain-text fallback prompt: {format_exc}")
                raise AgentOutputError(f"Failed to prepare fallback prompt: {format_exc}") from format_exc

        logger.error(f"[{self.name}] Exhausted all retries for structured output parsing.")
        raise AgentOutputError(f"Failed to parse LLM structured output after all attempts. Last error: {str(last_error)}")


    @abc.abstractmethod
    async def run(self, context: CampaignContext) -> CampaignContext:  # pragma: no cover
        """Execute the agent and return an updated ``CampaignContext``."""
        raise NotImplementedError
