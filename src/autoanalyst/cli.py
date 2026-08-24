"""Command-line interface (CLI) for AutoAnalyst AI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from autoanalyst.data_loading.loader import load_dataset
from autoanalyst.data_profiling.profiler import profile_dataframe
from autoanalyst.pipeline import PipelineConfig, run_analysis_pipeline
from autoanalyst.reporting.report_generator import create_full_report, create_html_report, create_json_report


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="autoanalyst",
        description="AutoAnalyst AI — Autonomous Data Intelligence Platform & ML Engine",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. run subcommand
    run_parser = subparsers.add_parser("run", help="Run end-to-end autonomous analysis on a dataset")
    run_parser.add_argument("--data", required=True, help="Path to CSV, Excel, Parquet, JSON, or SQLite file")
    run_parser.add_argument("--target", default=None, help="Optional target column for ML modeling")
    run_parser.add_argument(
        "--task", default="auto", choices=["auto", "classification", "regression"], help="ML task type"
    )
    run_parser.add_argument("--strategy", default="median", help="Missing value imputation strategy")
    run_parser.add_argument(
        "--output-report", default="reports/autoanalyst_report.html", help="Path to save output report"
    )
    run_parser.add_argument("--format", default="html", choices=["html", "md", "json"], help="Output report format")

    # 2. profile subcommand
    profile_parser = subparsers.add_parser("profile", help="Generate a fast summary profile of a dataset")
    profile_parser.add_argument("--data", required=True, help="Path to dataset file")
    profile_parser.add_argument("--json", action="store_true", help="Output profile as JSON")

    # 3. serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Launch the interactive Streamlit dashboard")
    serve_parser.add_argument("--port", default=8501, type=int, help="Port to host Streamlit on")
    serve_parser.add_argument("--host", default="localhost", help="Host address")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "run":
        return _handle_run(args)
    elif args.command == "profile":
        return _handle_profile(args)
    elif args.command == "serve":
        return _handle_serve(args)

    return 0


def _handle_run(args: argparse.Namespace) -> int:
    print(f"📊 AutoAnalyst AI: Starting pipeline on '{args.data}'...")
    try:
        config = PipelineConfig(
            target_column=args.target,
            model_task=args.task,
            missing_strategy=args.strategy,
        )
        result = run_analysis_pipeline(args.data, config=config)

        print(f"✅ Analysis complete: {result.raw_df.shape[0]} rows, {result.raw_df.shape[1]} columns.")
        if result.model_results:
            print(f"🤖 Champion Model: {result.model_results.get('model_name')}")
            if result.evaluation_results:
                scalars = {k: v for k, v in result.evaluation_results.items() if isinstance(v, (int, float))}
                print(f"📈 Evaluation Metrics: {scalars}")

        # Save Report
        out_path = Path(args.output_report)
        if args.format == "html" or out_path.suffix == ".html":
            create_html_report(
                str(out_path),
                title="AutoAnalyst AI Autonomous Report",
                profile=result.profile,
                insights=result.insights,
                missing_report=result.missing_values_report,
                eda_results=result.eda_results,
                model_results=result.model_results,
                evaluation_results=result.evaluation_results,
                warnings=result.warnings,
            )
        elif args.format == "json" or out_path.suffix == ".json":
            create_json_report(
                str(out_path),
                title="AutoAnalyst AI Autonomous Report",
                profile=result.profile,
                insights=result.insights,
                model_results=result.model_results,
                evaluation_results=result.evaluation_results,
                warnings=result.warnings,
            )
        else:
            create_full_report(
                str(out_path),
                title="AutoAnalyst AI Autonomous Report",
                profile=result.profile,
                insights=result.insights,
                missing_report=result.missing_values_report,
                eda_results=result.eda_results,
                model_results=result.model_results,
                evaluation_results=result.evaluation_results,
                warnings=result.warnings,
            )

        print(f"📄 Report saved to: {out_path.resolve()}")
        return 0
    except Exception as exc:
        print(f"❌ Error during execution: {exc}", file=sys.stderr)
        return 1


def _handle_profile(args: argparse.Namespace) -> int:
    try:
        df = load_dataset(args.data)
        profile = profile_dataframe(df)
        if args.json:
            print(json.dumps(profile.to_dict(), indent=2, default=str))
        else:
            print(f"\n📊 Dataset Profile: {args.data}")
            print(f"   Rows: {profile.rows:,} | Columns: {profile.columns}")
            score = profile.quality_report.health_score
            grade = profile.quality_report.grade
            print(f"   Quality Health Score: {score:.1f}% (Grade: {grade})")
            print(f"   Missing Values: {profile.missing_values_total:,} ({profile.missing_cells_percentage:.1f}%)")
            print(f"   Duplicate Rows: {profile.duplicate_rows:,}")
            print(f"   Memory Footprint: {profile.memory_footprint_formatted}\n")
        return 0
    except Exception as exc:
        print(f"❌ Error profiling dataset: {exc}", file=sys.stderr)
        return 1


def _handle_serve(args: argparse.Namespace) -> int:
    app_path = Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py"
    print(f"🚀 Starting AutoAnalyst AI Streamlit Dashboard at http://{args.host}:{args.port}...")
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(args.port),
        "--server.address",
        str(args.host),
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
