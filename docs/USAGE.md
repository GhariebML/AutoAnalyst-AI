# AdPilot Usage Guide

## Quick Start

```bash
# Clone the repository
git clone https://github.com/GhariebML/ADPilot.git
cd ADPilot

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest -q

# Validate schemas
python scripts/validate_schemas.py
```

## Agent Workflow Usage

### 1. Strategy Agent

```python
from src.adpilot.agents.strategy_agent import StrategyAgent
from src.adpilot.schemas.agent_schemas import StrategyAgentInput, CampaignInput

# Create input
campaign = CampaignInput(
    business_name="Example Startup",
    product_description="AI-powered marketing tool",
    target_market="Tech startups",
    budget_usd=10000,
    goals=["brand_awareness", "lead_generation"],
    channels=["linkedin", "twitter"],
    tone_of_voice="professional",
    brand_colors=["#0066CC", "#FFFFFF"],
    competitors=["CompetitorA", "CompetitorB"],
    campaign_duration_days=30
)

# Run strategy agent
agent = StrategyAgent()
output = await agent.run(StrategyAgentInput(campaign=campaign))
```

### 2. Analytics Agent

```python
from src.adpilot.agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent()
analytics_output = await agent.run(AnalyticsAgentInput(
    campaign=campaign,
    strategy=strategy_output,
    research=research_output,
    content=content_output
))
```

## Pipeline Execution

```python
# Full pipeline (future Phase 2)
from src.adpilot.orchestration.orchestrator import Orchestrator

orchestrator = Orchestrator()
final_package = await orchestrator.run(campaign_input)
```

## Configuration

Set environment variables in `.env`:

```env
OPENAI_API_KEY=<your-openai-key>
SERPAPI_API_KEY=<your-serpapi-key>
```

## Development Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run all tests |
| `ruff check .` | Lint code |
| `python scripts/validate_schemas.py` | Validate Pydantic schemas |
| `python -m adpilot` | Run module directly |

## Testing Individual Agents

```bash
# Run specific test file
pytest tests/test_strategy_agent.py -v

# Run with coverage
pytest --cov=src/adpilot tests/
```
