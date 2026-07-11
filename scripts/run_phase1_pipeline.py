"""Run the full local Phase 1 LangChain pipeline for the sample campaign."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from adpilot.orchestration.orchestrator import Orchestrator  # noqa: E402
from adpilot.schemas.agent_schemas import CampaignInput, OrchestratorInput  # noqa: E402


async def main() -> None:
    sample_path = Path("data/samples/campaign_input_sample.json")
    campaign = CampaignInput.model_validate(json.loads(sample_path.read_text(encoding="utf-8")))
    output = await Orchestrator().run(OrchestratorInput(campaign=campaign))
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
