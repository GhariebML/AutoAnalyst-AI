"""Module 13 — Automatic Reporting.

Renders a `ProfileResult` (loading metadata + validation + full profile)
into JSON, an HTML report, a Markdown report, a plain dict, or a console
summary string.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape

from autoanalyst.exceptions import ReportGenerationError
from autoanalyst.utils.helpers import get_logger, json_safe

logger = get_logger(__name__)

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AutoAnalyst Data Profile Report</title>
<style>
  :root {{
    --bg: #0b0f19; --panel: #131a2b; --border: #232b40; --text: #e6e9f2;
    --muted: #8b93a7; --accent: #5b8def; --good: #3ecf8e; --warn: #f5b942; --bad: #f2545b;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text); font-family: 'Segoe UI', Roboto, Arial, sans-serif; line-height:1.5; }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px 80px; }}
  h1 {{ font-size: 26px; margin-bottom:4px; }}
  h2 {{ font-size: 19px; margin-top:40px; border-bottom:1px solid var(--border); padding-bottom:8px; }}
  .subtitle {{ color: var(--muted); margin-bottom: 24px; font-size: 14px; }}
  .grade-badge {{ display:inline-block; font-size:34px; font-weight:700; padding:6px 22px; border-radius:12px; background:var(--panel); border:1px solid var(--border); }}
  .grade-A, .grade-Aplus {{ color: var(--good); }}
  .grade-B {{ color: #9fd85b; }}
  .grade-C {{ color: var(--warn); }}
  .grade-D, .grade-F {{ color: var(--bad); }}
  .score-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(150px,1fr)); gap:12px; margin-top:16px; }}
  .score-card {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:14px; }}
  .score-card .label {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
  .score-card .value {{ font-size:22px; font-weight:700; margin-top:4px; }}
  table {{ width:100%; border-collapse: collapse; margin-top:12px; font-size: 13px; }}
  th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--border); vertical-align:top; }}
  th {{ color:var(--muted); font-weight:600; text-transform:uppercase; font-size:11px; letter-spacing:.03em; }}
  tr:hover td {{ background: rgba(255,255,255,0.02); }}
  .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; background:var(--panel); border:1px solid var(--border); margin:2px 4px 2px 0; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 6px; }}
  .insight-list li {{ background: var(--panel); border:1px solid var(--border); border-radius:8px; padding:10px 14px; list-style:none; margin-bottom:8px; }}
  .insight-list {{ padding-left:0; }}
  .section-note {{ color:var(--muted); font-size:13px; }}
  code {{ background:var(--panel); padding:1px 6px; border-radius:4px; font-size:12px; }}
  .flex-row {{ display:flex; gap:24px; flex-wrap:wrap; align-items:flex-start; }}
  .col {{ flex:1; min-width:280px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>AutoAnalyst — Data Profile Report</h1>
  <div class="subtitle">Generated {generated_at} &middot; Source: <code>{file_name}</code> &middot; {n_rows} rows &times; {n_cols} columns</div>

  <div class="flex-row">
    <div class="col">
      <span class="grade-badge grade-{grade_class}">{grade}</span>
      <div class="section-note" style="margin-top:8px;">Overall Quality Score: <strong>{overall_score}/100</strong></div>
    </div>
    <div class="col">
      <div class="score-grid">{score_cards}</div>
    </div>
  </div>

  <h2>Executive Summary</h2>
  <ul class="insight-list">{insight_items}</ul>

  <h2>Dataset Overview</h2>
  <p class="section-note">{purpose}</p>
  <table>
    <tr><th>Rows</th><td>{n_rows}</td><th>Columns</th><td>{n_cols}</td></tr>
    <tr><th>Primary Key Candidate</th><td>{pk}</td><th>Inferred Problem Type</th><td>{problem_type}</td></tr>
    <tr><th>Target Candidate(s)</th><td colspan="3">{targets}</td></tr>
  </table>
  <p class="section-note">Numeric: {numeric_pills}</p>
  <p class="section-note">Categorical: {categorical_pills}</p>
  <p class="section-note">Datetime: {datetime_pills}</p>

  <h2>Validation Results</h2>
  <p>Status: <strong>{validation_status}</strong></p>
  {validation_tables}

  <h2>Missing Value Analysis</h2>
  <p class="section-note">Mechanism guess: <strong>{missing_mechanism}</strong> — {missing_explanation}</p>
  {missing_table}

  <h2>Duplicate Analysis</h2>
  <table>
    <tr><th>Duplicate Rows</th><td>{dup_rows} ({dup_pct}%)</td>
        <th>Duplicate Column Groups</th><td>{dup_col_groups}</td></tr>
  </table>

  <h2>Feature Statistics</h2>
  {column_table}

  <h2>Recommendations</h2>
  {recommendations_table}

</div>
</body>
</html>
"""


class ReportGenerator:
    """Renders profile results into multiple output formats."""

    def to_dict(self, result: dict) -> dict:
        return json_safe(result)

    def to_json(self, result: dict, indent: int = 2) -> str:
        try:
            return json.dumps(self.to_dict(result), indent=indent, ensure_ascii=False)
        except Exception as exc:  # noqa: BLE001
            raise ReportGenerationError(f"Failed to serialize report to JSON: {exc}") from exc

    def console_summary(self, result: dict) -> str:
        meta = result["load_metadata"]
        quality = result["profile"]["data_quality"]
        understanding = result["profile"]["data_understanding"]
        lines = [
            "=" * 60,
            " AUTOANALYST — DATA PROFILE SUMMARY",
            "=" * 60,
            f" File            : {meta['file_path']}",
            f" Format          : {meta['file_format']}",
            f" Shape           : {understanding['n_rows']:,} rows x {understanding['n_columns']} columns",
            f" Validation      : {result['validation']['status']}",
            f" Quality Score   : {quality['overall_quality_score']}/100 (Grade {quality['quality_grade']})",
            f" Problem Type    : {understanding['inferred_problem_type']}",
            f" Target Guess    : {', '.join(understanding['target_candidates']) or 'n/a'}",
            "-" * 60,
            " TOP INSIGHTS:",
        ]
        for insight in result["profile"]["business_insights"][:8]:
            lines.append(f"  - {insight}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def to_markdown(self, result: dict) -> str:
        try:
            return self._render_markdown(result)
        except Exception as exc:  # noqa: BLE001
            raise ReportGenerationError(f"Failed to render Markdown report: {exc}") from exc

    def to_html(self, result: dict) -> str:
        try:
            return self._render_html(result)
        except Exception as exc:  # noqa: BLE001
            raise ReportGenerationError(f"Failed to render HTML report: {exc}") from exc

    # ------------------------------------------------------------ markdown --
    def _render_markdown(self, result: dict) -> str:
        meta = result["load_metadata"]
        validation = result["validation"]
        profile = result["profile"]
        understanding = profile["data_understanding"]
        quality = profile["data_quality"]
        missing = profile["missing_value_analysis"]
        dup = profile["duplicate_analysis"]
        recs = profile["feature_recommendations"]

        lines = [
            "# AutoAnalyst — Data Profile Report",
            "",
            f"*Generated {datetime.now(timezone.utc).isoformat()}*",
            "",
            f"**Source:** `{meta['file_path']}`  |  **Format:** {meta['file_format']}  "
            f"|  **Shape:** {understanding['n_rows']:,} rows x {understanding['n_columns']} columns",
            "",
            "## Executive Summary",
            "",
        ]
        lines += [f"- {i}" for i in profile["business_insights"]]

        lines += [
            "",
            "## Dataset Overview",
            "",
            f"- Purpose: {understanding['dataset_purpose_guess']}",
            f"- Primary key candidate: `{understanding['primary_key_candidate']}`",
            f"- Inferred problem type: **{understanding['inferred_problem_type']}**",
            f"- Target candidate(s): {', '.join(understanding['target_candidates']) or 'none'}",
            f"- Numeric columns: {len(understanding['column_roles']['numeric'])}",
            f"- Categorical columns: {len(understanding['column_roles']['categorical'])}",
            f"- Datetime columns: {len(understanding['column_roles']['datetime'])}",
            f"- Text columns: {len(understanding['column_roles']['text'])}",
            "",
            "## Validation Results",
            "",
            f"**Status:** {validation['status']}",
            "",
        ]
        if validation["errors"]:
            lines.append("**Errors:**")
            lines += [f"- {e}" for e in validation["errors"]]
        if validation["warnings"]:
            lines.append("**Warnings:**")
            lines += [f"- {w}" for w in validation["warnings"]]
        if validation["recommendations"]:
            lines.append("**Recommendations:**")
            lines += [f"- {r}" for r in validation["recommendations"]]

        lines += [
            "",
            "## Data Quality",
            "",
            "| Metric | Score |",
            "|---|---|",
            f"| Completeness | {quality['completeness_score']} |",
            f"| Consistency | {quality['consistency_score']} |",
            f"| Validity | {quality['validity_score']} |",
            f"| Uniqueness | {quality['uniqueness_score']} |",
            f"| Accuracy (heuristic) | {quality['accuracy_heuristic_score']} |",
            f"| Integrity | {quality['integrity_score']} |",
            f"| **Overall** | **{quality['overall_quality_score']} (Grade {quality['quality_grade']})** |",
            "",
            "## Missing Value Analysis",
            "",
            f"- Total missing: {missing['total_missing_pct']}% of all cells",
            f"- Mechanism guess: **{missing['missing_mechanism_guess']}** — {missing['mechanism_explanation']}",
        ]
        if missing["columns_with_missing"]:
            lines.append("")
            lines.append("| Column | Missing % |")
            lines.append("|---|---|")
            for col, p in list(missing["columns_with_missing"].items())[:20]:
                lines.append(f"| {col} | {p}% |")

        lines += [
            "",
            "## Duplicates",
            "",
            f"- Duplicate rows: {dup['duplicate_row_count']} ({dup['duplicate_row_pct']}%)",
            f"- Duplicate column groups: {len(dup['duplicate_columns'])}",
            f"- Redundant columns: {', '.join(dup['redundant_columns']) or 'none'}",
            "",
            "## Feature Statistics",
            "",
            "| Column | Role | Dtype | Missing % | Unique % |",
            "|---|---|---|---|---|",
        ]
        for name, cp in profile["column_profiles"].items():
            lines.append(f"| {name} | {cp['role']} | {cp['dtype']} | {cp['missing_pct']}% | {cp['unique_pct']}% |")

        lines += [
            "",
            "## Recommendations",
            "",
            f"- Columns to drop: {', '.join(recs['columns_to_drop']) or 'none'}",
            f"- Columns to encode: {', '.join(recs['columns_to_encode']) or 'none'}",
            f"- Columns to normalize/transform: {', '.join(recs['columns_to_normalize']) or 'none'}",
            f"- Columns to scale: {', '.join(recs['columns_to_scale']) or 'none'}",
            f"- Columns to impute: {', '.join(recs['columns_to_impute']) or 'none'}",
            f"- Potential target: {recs['potential_target_column'] or 'n/a'}",
        ]
        if recs["feature_engineering_ideas"]:
            lines.append("")
            lines.append("**Feature engineering ideas:**")
            lines += [f"- {i}" for i in recs["feature_engineering_ideas"]]

        return "\n".join(lines)

    # ---------------------------------------------------------------- html --
    def _render_html(self, result: dict) -> str:
        meta = result["load_metadata"]
        validation = result["validation"]
        profile = result["profile"]
        understanding = profile["data_understanding"]
        quality = profile["data_quality"]
        missing = profile["missing_value_analysis"]
        dup = profile["duplicate_analysis"]
        recs = profile["feature_recommendations"]

        grade = quality["quality_grade"]
        grade_class = grade.replace("+", "plus")

        score_cards = "".join(
            f'<div class="score-card"><div class="label">{label}</div><div class="value">{quality[key]}</div></div>'
            for label, key in [
                ("Completeness", "completeness_score"),
                ("Consistency", "consistency_score"),
                ("Validity", "validity_score"),
                ("Uniqueness", "uniqueness_score"),
                ("Accuracy", "accuracy_heuristic_score"),
                ("Integrity", "integrity_score"),
            ]
        )

        insight_items = "".join(f"<li>{escape(i)}</li>" for i in profile["business_insights"])

        def pills(items: list[str]) -> str:
            if not items:
                return "<span class='section-note'>none</span>"
            return "".join(f"<span class='pill'>{escape(str(x))}</span>" for x in items[:25])

        validation_blocks = []
        for label, items in [("Errors", validation["errors"]), ("Warnings", validation["warnings"]), ("Recommendations", validation["recommendations"])]:
            if items:
                validation_blocks.append(f"<h3 style='font-size:14px;margin-top:16px;'>{label}</h3><ul>" + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>")
        validation_tables = "".join(validation_blocks) or "<p class='section-note'>No issues found.</p>"

        if missing["columns_with_missing"]:
            rows = "".join(
                f"<tr><td>{escape(col)}</td><td>{p}%</td></tr>"
                for col, p in list(missing["columns_with_missing"].items())[:25]
            )
            missing_table = f"<table><tr><th>Column</th><th>Missing %</th></tr>{rows}</table>"
        else:
            missing_table = "<p class='section-note'>No missing values detected.</p>"

        col_rows = "".join(
            f"<tr><td>{escape(name)}</td><td>{cp['role']}</td><td>{cp['dtype']}</td>"
            f"<td>{cp['missing_pct']}%</td><td>{cp['unique_pct']}%</td><td>{cp['mode']}</td></tr>"
            for name, cp in profile["column_profiles"].items()
        )
        column_table = (
            "<table><tr><th>Column</th><th>Role</th><th>Dtype</th><th>Missing %</th>"
            f"<th>Unique %</th><th>Mode</th></tr>{col_rows}</table>"
        )

        rec_rows = "".join(
            f"<tr><th>{label}</th><td>{escape(', '.join(recs[key]) or 'none')}</td></tr>"
            for label, key in [
                ("Drop", "columns_to_drop"),
                ("Encode", "columns_to_encode"),
                ("Normalize", "columns_to_normalize"),
                ("Scale", "columns_to_scale"),
                ("Impute", "columns_to_impute"),
                ("Bin", "columns_to_bin"),
            ]
        )
        recommendations_table = f"<table>{rec_rows}</table>"

        return _HTML_TEMPLATE.format(
            generated_at=escape(datetime.now(timezone.utc).isoformat()),
            file_name=escape(str(meta["file_path"]).split("/")[-1]),
            n_rows=f"{understanding['n_rows']:,}",
            n_cols=understanding["n_columns"],
            grade=grade,
            grade_class=grade_class,
            overall_score=quality["overall_quality_score"],
            score_cards=score_cards,
            insight_items=insight_items,
            purpose=escape(understanding["dataset_purpose_guess"]),
            pk=escape(str(understanding["primary_key_candidate"])),
            problem_type=escape(understanding["inferred_problem_type"]),
            targets=escape(", ".join(understanding["target_candidates"]) or "none"),
            numeric_pills=pills(understanding["column_roles"]["numeric"]),
            categorical_pills=pills(understanding["column_roles"]["categorical"]),
            datetime_pills=pills(understanding["column_roles"]["datetime"]),
            validation_status=escape(validation["status"]),
            validation_tables=validation_tables,
            missing_mechanism=escape(missing["missing_mechanism_guess"]),
            missing_explanation=escape(missing["mechanism_explanation"]),
            missing_table=missing_table,
            dup_rows=dup["duplicate_row_count"],
            dup_pct=dup["duplicate_row_pct"],
            dup_col_groups=len(dup["duplicate_columns"]),
            column_table=column_table,
            recommendations_table=recommendations_table,
        )
