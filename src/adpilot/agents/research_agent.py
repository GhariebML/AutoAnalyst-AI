import logging
import json
from langchain_core.prompts import ChatPromptTemplate

from ..core.base_agent import BaseAgent
from ..schemas.agent_schemas import CampaignContext, ResearchAgentInput, ResearchAgentOutput

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent[ResearchAgentInput, ResearchAgentOutput]):
    """Generate validated Phase 1 market research using structured output."""

    name = "research_agent"
    input_model = ResearchAgentInput
    output_model = ResearchAgentOutput

    system_prompt = (
        "You are AdPilot's Lead Market Research Analyst. Produce comprehensive, enterprise-grade "
        "market intelligence based on the supplied campaign brief. Formulate rigorous audience "
        "personas, deep competitive analyses, accurate channel benchmarks, and actionable market "
        "insights. Use sophisticated, analytical language suitable for executive strategy sessions. "
        "Do not claim that real-time web search or paid tools were used; treat search_queries_used "
        "as proposed research avenues. Ensure every field is thoroughly populated and exactly matches "
        "the ResearchAgentOutput schema. No markdown, preamble, or explanation."
    )

    async def run(self, context: CampaignContext) -> CampaignContext:
        """Generate research from campaign input and update context."""
        agent_input = ResearchAgentInput(campaign=context.brief)
        validated_input = self.validate_input(agent_input)
        output = await self.call_llm(
            prompt=self.build_prompt(),
            campaign_json=json.dumps(validated_input.campaign.model_dump(mode="json"), indent=2),
            campaign_id=context.campaign_id,
        )

        # ML Model prediction step
        try:
            from ..services.model_loader import ModelLoader
            model = ModelLoader().load_model("research/models/research/research_model.pkl")
            tokenizer = ModelLoader().load_model("research/models/research/research_tokenizer.pkl")
            scaler = ModelLoader().load_model("research/models/research/research_scaler.pkl")
            if model is not None and tokenizer is not None and scaler is not None:
                text_input = f"{context.brief.product_name or ''} {context.brief.product_description or ''}"
                feat = tokenizer.transform([text_input])
                scaled_feat = scaler.transform(feat)
                topic = int(model.predict(scaled_feat)[0])
                logger.info("Research ML Model topic prediction: class %s", topic)
            else:
                logger.info("Research ML Model files loaded as None. Skipping prediction.")
        except Exception as e:
            logger.warning("Failed research model prediction: %s", str(e))

        context.research = output
        return context


    def build_prompt(self) -> ChatPromptTemplate:
        """Build the LangChain prompt template for research generation."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Create a realistic synthetic Phase 1 research package for this campaign:\n\n"
                    "{campaign_json}\n\n"
                    "Use the campaign channels and competitors where available. Ensure every "
                    "field satisfies the required Pydantic output model.",
                ),
            ]
        )
