"""Run the LangChain-backed StrategyAgent against the sample campaign input."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from adpilot.agents.strategy_agent import StrategyAgent  # noqa: E402
from adpilot.schemas.agent_schemas import CampaignInput, StrategyAgentInput  # noqa: E402


async def main() -> None:
    sample_path = Path("data/samples/campaign_input_sample.json")
    campaign_data = json.loads(sample_path.read_text(encoding="utf-8"))
    campaign = CampaignInput.model_validate(campaign_data)
    agent_input = StrategyAgentInput(campaign=campaign)

    output = await StrategyAgent().run(agent_input)
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
