"""Test that the project skeleton contains all required files."""

import pathlib

ROOT = pathlib.Path(__file__).parent.parent


def _exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def test_critical_folders_exist():
    critical = [
        "src/adpilot",
        "src/adpilot/agents",
        "src/adpilot/core",
        "src/adpilot/orchestration",
        "src/adpilot/schemas",
        "src/adpilot/prompts",
        "src/adpilot/services",
        "src/adpilot/utils",
        "data/samples",
        "data/outputs",
        "docs",
        "scripts",
        "tests",
    ]
    for folder in critical:
        assert _exists(folder), f"Missing folder: {folder}"


def test_agent_schemas_file_exists():
    assert _exists("src/adpilot/schemas/agent_schemas.py")


def test_agent_files_exist():
    agents = [
        "strategy_agent.py",
        "research_agent.py",
        "content_agent.py",
        "analytics_agent.py",
        "design_agent.py",
        "campaign_manager_agent.py",
    ]
    for agent in agents:
        assert _exists(f"src/adpilot/agents/{agent}"), f"Missing agent: {agent}"


def test_prompt_files_exist():
    prompts = [
        "strategy_system_prompt.md",
        "research_system_prompt.md",
        "content_system_prompt.md",
        "analytics_system_prompt.md",
        "design_system_prompt.md",
        "campaign_manager_system_prompt.md",
        "orchestrator_system_prompt.md",
    ]
    for prompt in prompts:
        assert _exists(f"src/adpilot/prompts/{prompt}"), f"Missing prompt: {prompt}"
