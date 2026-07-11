# Project Structure

The repository follows a classic Python package layout with a clear separation of
concerns:

```
adpilot/
├── src/adpilot/       # Package source code
│   ├── __init__…
│   ├── main.py          # Entry‑point (runs the orchestrator in Phase 2)
│   ├── agents/          # One module per pipeline stage
│   ├── core/            # Base classes, exceptions, utilities
│   ├── orchestration/   # Orchestrator controller
│   ├── prompts/         # Typed prompt templates
│   ├── schemas/         # Pydantic v2 contracts
│   ├── services/        # Abstract external API wrappers
│   └── utils/           # Misc helpers
├── data/                # Sample input / placeholder output
├── docs/                # Human‑readable docs for each phase
├── scripts/             # Convenience one‑liners (validation, demo)
├── tests/               # Pytest test‑suite
├── pyproject.toml
└── ...
```

All agents should import models from ``adpilot.schemas`` and will output
instances of the associated ``output_model``.
