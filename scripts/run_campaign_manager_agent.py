"""Run the sample campaign through CampaignManagerAgent dependencies."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from adpilot.agents.analytics_agent import AnalyticsAgent  # noqa: E402
from adpilot.agents.campaign_manager_agent import CampaignManagerAgent  # noqa: E402
from adpilot.agents.content_agent import ContentAgent  # noqa: E402
from adpilot.agents.design_agent import DesignAgent  # noqa: E402
from adpilot.agents.research_agent import ResearchAgent  # noqa: E402
from adpilot.agents.strategy_agent import StrategyAgent  # noqa: E402
from adpilot.schemas.agent_schemas import (  # noqa: E402
    AnalyticsAgentInput,
    CampaignInput,
    CampaignManagerInput,
    ContentAgentInput,
    DesignAgentInput,
    ResearchAgentInput,
    StrategyAgentInput,
)


async def main() -> None:
    sample_path = Path("data/samples/campaign_input_sample.json")
    campaign = CampaignInput.model_validate(json.loads(sample_path.read_text(encoding="utf-8")))
    strategy = await StrategyAgent().run(StrategyAgentInput(campaign=campaign))
    research = await ResearchAgent().run(ResearchAgentInput(campaign=campaign))
    content = await ContentAgent().run(ContentAgentInput(strategy=strategy, research=research))
    analytics = await AnalyticsAgent().run(
        AnalyticsAgentInput(campaign=campaign, strategy=strategy, research=research, content=content)
    )
    design = await DesignAgent().run(DesignAgentInput(strategy=strategy, content=content))
    output = await CampaignManagerAgent().run(
        CampaignManagerInput(
            campaign=campaign,
            strategy=strategy,
            research=research,
            content=content,
            analytics=analytics,
            design=design,
        )
    )
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
