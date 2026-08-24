"""Unit tests for the reporting module (Markdown, HTML, JSON report generation)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from autoanalyst.reporting.report_generator import (
    create_full_report,
    create_html_report,
    create_json_report,
    create_markdown_report,
)


@pytest.fixture
def dummy_report_data() -> dict[str, Any]:
    return {
        "title": "Test Enterprise Report",
        "profile": {"rows": 100, "columns": 5, "health_score": 92.5, "quality_grade": "A"},
        "insights": ["Insight 1: High quality data.", "Insight 2: No extreme outliers."],
        "model_results": {"task": "classification", "model_name": "RandomForestClassifier"},
        "evaluation_results": {"accuracy": 0.885, "f1_macro": 0.875},
        "executive_summary": "Autonomous analysis conducted on customer dataset.",
    }


class TestReportingGenerators:
    def test_create_markdown_report(self, tmp_path: Path) -> None:
        out = tmp_path / "test.md"
        res = create_markdown_report("Title", ["Insight A", "Insight B"], str(out))
        assert res.exists()
        text = res.read_text(encoding="utf-8")
        assert "# Title" in text
        assert "Insight A" in text

    def test_create_full_markdown_report(self, dummy_report_data: dict[str, Any], tmp_path: Path) -> None:
        out = tmp_path / "full.md"
        res = create_full_report(
            output_path=str(out),
            title=dummy_report_data["title"],
            profile=dummy_report_data["profile"],
            insights=dummy_report_data["insights"],
            model_results=dummy_report_data["model_results"],
            evaluation_results=dummy_report_data["evaluation_results"],
            executive_summary=dummy_report_data["executive_summary"],
        )
        assert res.exists()
        text = res.read_text(encoding="utf-8")
        assert "## Executive Summary" in text
        assert "## Dataset Overview" in text
        assert "## Evaluation Metrics" in text

    def test_create_html_report(self, dummy_report_data: dict[str, Any], tmp_path: Path) -> None:
        out = tmp_path / "full.html"
        res = create_html_report(
            output_path=str(out),
            title=dummy_report_data["title"],
            profile=dummy_report_data["profile"],
            insights=dummy_report_data["insights"],
            model_results=dummy_report_data["model_results"],
            evaluation_results=dummy_report_data["evaluation_results"],
            executive_summary=dummy_report_data["executive_summary"],
        )
        assert res.exists()
        html = res.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html
        assert "Data Quality Health" in html
        assert "Test Enterprise Report" in html

    def test_create_json_report(self, dummy_report_data: dict[str, Any], tmp_path: Path) -> None:
        out = tmp_path / "full.json"
        res = create_json_report(
            output_path=str(out),
            title=dummy_report_data["title"],
            profile=dummy_report_data["profile"],
            insights=dummy_report_data["insights"],
            model_results=dummy_report_data["model_results"],
            evaluation_results=dummy_report_data["evaluation_results"],
            executive_summary=dummy_report_data["executive_summary"],
        )
        assert res.exists()
        data = json.loads(res.read_text(encoding="utf-8"))
        assert data["title"] == "Test Enterprise Report"
        assert data["profile"]["rows"] == 100
