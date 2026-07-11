"""Demo script that loads the sample input and runs the orchestrator placeholder.

The orchestrator currently raises ``NotImplementedError`` – this script is a
scaffold for future development.
"""

import json
from pathlib import Path

from adpilot.orchestration.orchestrator import Orchestrator
from adpilot.schemas.agent_schemas import OrchestratorInput


def main() -> None:
    sample_path = Path(__file__).parent.parent / "data" / "samples" / "campaign_input_sample.json"
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    orchestrator = Orchestrator()
    try:
        result = orchestrator.run(OrchestratorInput(campaign=data))
        print(result)
    except NotImplementedError as exc:
        print("Orchestrator not implemented yet:", exc)


if __name__ == "__main__":
    main()
