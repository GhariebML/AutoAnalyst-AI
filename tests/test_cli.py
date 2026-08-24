"""Unit tests for the AutoAnalyst AI command-line interface (CLI)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from autoanalyst.cli import main


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "age": [25, 30, 35, 40, 45],
            "income": [50000, 60000, 75000, 80000, 95000],
            "default": [0, 0, 1, 0, 1],
        }
    )
    path = tmp_path / "cli_sample.csv"
    df.to_csv(path, index=False)
    return path


class TestCLI:
    def test_cli_help(self) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_cli_profile(self, sample_csv: Path) -> None:
        exit_code = main(["profile", "--data", str(sample_csv)])
        assert exit_code == 0

    def test_cli_profile_json(self, sample_csv: Path) -> None:
        exit_code = main(["profile", "--data", str(sample_csv), "--json"])
        assert exit_code == 0

    def test_cli_run_classification(self, sample_csv: Path, tmp_path: Path) -> None:
        report_file = tmp_path / "cli_report.html"
        exit_code = main(
            [
                "run",
                "--data",
                str(sample_csv),
                "--target",
                "default",
                "--output-report",
                str(report_file),
                "--format",
                "html",
            ]
        )
        assert exit_code == 0
        assert report_file.exists()
