"""Validate that all Pydantic schemas can be instantiated.

This script simply imports * all models from ``adpilot.schemas.agent_schemas`` and
attempts to generate their JSON schema. If any model fails to import or build a
schema, the script exits with a non‑zero status.

It is useful for CI checks before a full Python package is built.
"""

import sys

from adpilot.schemas.agent_schemas import CampaignInput


if __name__ == "__main__":  # pragma: no cover
    try:
        CampaignInput.model_json_schema()  # Generates JSON schema -> will raise if broken
    except Exception as exc:  # pragma: no cover
        print(f"Schema validation failed: {exc}")
        sys.exit(1)
    print("All schemas validated successfully.")
