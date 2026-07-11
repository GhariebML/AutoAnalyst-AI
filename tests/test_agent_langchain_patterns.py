"""Safe tests for LangChain-backed agent patterns."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from adpilot.agents.analytics_agent import AnalyticsAgent
from adpilot.agents.campaign_manager_agent import CampaignManagerAgent
from adpilot.agents.content_agent import ContentAgent
from adpilot.agents.design_agent import DesignAgent
from adpilot.agents.research_agent import ResearchAgent
from adpilot.agents.strategy_agent import StrategyAgent
from adpilot.agents.audience_agent import AudienceAgent
from adpilot.agents.competitor_agent import CompetitorAgent
from adpilot.agents.creative_agent import CreativeAgent
from adpilot.agents.optimization_agent import OptimizationAgent
from adpilot.agents.publishing_agent import PublishingAgent
from adpilot.core.base_agent import BaseAgent
from adpilot.schemas.agent_schemas import (
    AnalyticsAgentInput,
    AnalyticsAgentOutput,
    CampaignManagerInput,
    CampaignManagerOutput,
    ContentAgentInput,
    ContentAgentOutput,
    DesignAgentInput,
    DesignAgentOutput,
    ResearchAgentInput,
    ResearchAgentOutput,
    StrategyAgentInput,
    StrategyAgentOutput,
    AudienceAgentInput,
    AudienceOutput,
    CompetitorAgentInput,
    CompetitorLandscape,
    CreativeAgentInput,
    CreativeOutput,
    OptimizationAgentInput,
    OptimizationOutput,
    PublishingAgentInput,
    PublishingPackage,
)


AGENT_CASES = [
    (StrategyAgent, "strategy_agent", StrategyAgentInput, StrategyAgentOutput),
    (ResearchAgent, "research_agent", ResearchAgentInput, ResearchAgentOutput),
    (ContentAgent, "content_agent", ContentAgentInput, ContentAgentOutput),
    (AnalyticsAgent, "analytics_agent", AnalyticsAgentInput, AnalyticsAgentOutput),
    (DesignAgent, "design_agent", DesignAgentInput, DesignAgentOutput),
    (CampaignManagerAgent, "campaign_manager_agent", CampaignManagerInput, CampaignManagerOutput),
    (AudienceAgent, "audience_agent", AudienceAgentInput, AudienceOutput),
    (CompetitorAgent, "competitor_agent", CompetitorAgentInput, CompetitorLandscape),
    (CreativeAgent, "creative_agent", CreativeAgentInput, CreativeOutput),
    (OptimizationAgent, "optimization_agent", OptimizationAgentInput, OptimizationOutput),
    (PublishingAgent, "publishing_agent", PublishingAgentInput, PublishingPackage),
]


def test_agents_follow_langchain_base_pattern() -> None:
    for agent_class, expected_name, input_model, output_model in AGENT_CASES:
        agent = agent_class()

        assert isinstance(agent, BaseAgent)
        assert agent.name == expected_name
        assert agent.input_model is input_model
        assert agent.output_model is output_model
        assert isinstance(agent.system_prompt, str)
        assert agent.system_prompt.strip()
        assert callable(agent.build_prompt)
        assert callable(agent.run)


def test_run_scripts_exist() -> None:
    scripts_dir = Path("scripts")
    expected_scripts = [
        "run_strategy_agent.py",
        "run_research_agent.py",
        "run_content_agent.py",
        "run_analytics_agent.py",
        "run_design_agent.py",
        "run_campaign_manager_agent.py",
        "run_phase1_pipeline.py",
    ]

    for script_name in expected_scripts:
        assert (scripts_dir / script_name).is_file()


def test_pipeline_script_imports_successfully() -> None:
    script_path = Path("scripts/run_phase1_pipeline.py")
    spec = importlib.util.spec_from_file_location("run_phase1_pipeline", script_path)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert callable(module.main)
