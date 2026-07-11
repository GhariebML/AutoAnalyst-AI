"""AdPilot Phase 2 – application entry point.

Run locally with:
    uvicorn adpilot.api.main:app --reload --host 0.0.0.0 --port 8000

Or via this module:
    python -m adpilot.main
"""

from __future__ import annotations

import uvicorn


def main() -> None:  # pragma: no cover
    uvicorn.run(
        "adpilot.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":  # pragma: no cover
    main()
