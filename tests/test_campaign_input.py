"""Tests for the CampaignInput schema using the sample JSON file."""

import json
from pathlib import Path

import pytest

from adpilot.schemas.agent_schemas import CampaignInput


def load_sample() -> dict:
    sample_path = Path(__file__).parent.parent / "data" / "samples" / "campaign_input_sample.json"
    return json.loads(sample_path.read_text(encoding="utf-8"))


def test_campaign_input_valid():
    data = load_sample()
    model = CampaignInput.model_validate(data)
    assert model.business_name
    assert model.budget_usd > 0


def test_invalid_budget_raises():
    data = load_sample()
    data["budget_usd"] = -10
    with pytest.raises(Exception):
        CampaignInput.model_validate(data)


def test_invalid_hex_color_raises():
    data = load_sample()
    data["brand_colors"] = ["not-a-hex"]
    with pytest.raises(Exception):
        CampaignInput.model_validate(data)
