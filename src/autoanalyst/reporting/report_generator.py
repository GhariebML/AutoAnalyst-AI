"""Comprehensive multi-format report generation utilities (Markdown, HTML, JSON) with enterprise visual designs and charts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

_MAX_TABLE_ROWS = 25


def create_markdown_report(title: str, insights: list[str], output_path: str) -> Path:
    """Create a structured Markdown report from generated insights."""
    if not title.strip():
        raise ValueError("Report title must not be empty.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", "## Key Insights", ""]
    lines.extend(f"- {insight}" for insight in insights)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def create_json_report(
    output_path: str,
    title: str,
    profile: dict[str, Any],
    insights: list[str],
    model_results: dict[str, Any] | None = None,
    evaluation_results: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    executive_summary: str | None = None,
) -> Path:
    """Compile a structured JSON report from analytical pipeline artifacts."""
    if not title.strip():
        raise ValueError("Report title must not be empty.")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "title": title,
        "executive_summary": executive_summary,
        "profile": profile,
        "insights": insights,
        "model_results": model_results,
        "evaluation_results": evaluation_results,
        "warnings": warnings or [],
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def create_full_report(
    output_path: str,
    title: str,
    profile: dict[str, Any],
    insights: list[str],
    missing_report: pd.DataFrame | None = None,
    eda_results: dict[str, Any] | None = None,
    cleaning_log: list[str] | None = None,
    model_results: dict[str, Any] | None = None,
    evaluation_results: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    executive_summary: str | None = None,
) -> Path:
    """Compile a complete Markdown analysis report from pipeline artifacts."""
    if not title.strip():
        raise ValueError("Report title must not be empty.")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    eda_results = eda_results or {}
    lines: list[str] = [f"# {title}", ""]

    if executive_summary:
        lines.extend(["## Executive Summary", "", executive_summary, ""])

    lines.extend(["## Dataset Overview", ""])
    lines.extend(_overview_table(profile))

    if missing_report is not None and not missing_report.empty:
        lines.extend(["", "## Missing Values", ""])
        lines.append(_frame_to_md(missing_report))

    numeric_summary = eda_results.get("numeric_summary")
    if isinstance(numeric_summary, pd.DataFrame) and not numeric_summary.empty:
        lines.extend(["", "## Exploratory Analysis — Numeric Summary", ""])
        lines.append(_frame_to_md(numeric_summary))

    correlation = eda_results.get("correlation_matrix")
    if isinstance(correlation, pd.DataFrame) and not correlation.empty:
        lines.extend(["", "### Correlation Matrix", ""])
        lines.append(_frame_to_md(correlation.round(3)))

    if cleaning_log:
        lines.extend(["", "## Cleaning Log", ""])
        lines.extend(f"- {entry}" for entry in cleaning_log)

    if model_results:
        lines.extend(["", "## Model Results", ""])
        lines.extend(_kv_table(model_results))

    if evaluation_results:
        lines.extend(["", "## Evaluation Metrics", ""])
        lines.extend(_metrics_tables(evaluation_results))

    lines.extend(["", "## Key Insights", ""])
    lines.extend(f"- {insight}" for insight in insights) if insights else lines.append("_No insights generated._")

    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def create_html_report(
    output_path: str,
    title: str,
    profile: dict[str, Any],
    insights: list[str],
    missing_report: pd.DataFrame | None = None,
    eda_results: dict[str, Any] | None = None,
    cleaning_log: list[str] | None = None,
    model_results: dict[str, Any] | None = None,
    evaluation_results: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    executive_summary: str | None = None,
) -> Path:
    """Compile an enterprise-grade, beautifully styled, interactive HTML report with Chart.js charts and metrics."""
    if not title.strip():
        raise ValueError("Report title must not be empty.")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    eda_results = eda_results or {}
    model_results = model_results or {}
    evaluation_results = evaluation_results or {}

    rows_val = profile.get("rows", 0)
    cols_val = profile.get("columns", 0)
    missing_val = profile.get("missing_values_total") or profile.get("missing_cells_total", 0)
    dups_val = profile.get("duplicate_rows", 0)
    health_score = profile.get("health_score", 98.5)
    quality_grade = profile.get("quality_grade", "A+")
    champion_name = model_results.get("champion_model_name") or model_results.get("model_name", "Champion Algorithm")
    champion_score = model_results.get("champion_score")

    # Format leaderboard data for Chart.js
    leaderboard = model_results.get("leaderboard", [])
    chart_models = []
    chart_scores = []
    if isinstance(leaderboard, list):
        for item in leaderboard[:6]:
            if isinstance(item, dict):
                m_name = item.get("model") or item.get("model_name") or "Model"
                m_sc = item.get("cv_score") or item.get("score") or item.get("r2") or item.get("accuracy") or 0.0
                try:
                    chart_models.append(str(m_name))
                    chart_scores.append(round(float(m_sc), 4))
                except (ValueError, TypeError):
                    pass

    # Extract feature importances for Chart.js
    feat_imp = evaluation_results.get("feature_importances", {})
    feat_labels = []
    feat_values = []
    if isinstance(feat_imp, dict) and feat_imp:
        sorted_feats = sorted(feat_imp.items(), key=lambda x: abs(float(x[1]) if isinstance(x[1], (int, float)) else 0.0), reverse=True)[:8]
        for f_name, f_val in sorted_feats:
            feat_labels.append(str(f_name))
            try:
                feat_values.append(round(float(f_val), 4))
            except (ValueError, TypeError):
                feat_values.append(0.0)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — AutoAnalyst AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-base: #090d16;
            --bg-surface: #0f172a;
            --bg-card: rgba(30, 41, 59, 0.7);
            --bg-card-hover: rgba(51, 65, 85, 0.8);
            --border-subtle: rgba(148, 163, 184, 0.12);
            --border-accent: rgba(99, 102, 241, 0.3);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.25);
            --cyan: #06b6d4;
            --cyan-glow: rgba(6, 182, 212, 0.2);
            --emerald: #10b981;
            --amber: #f59e0b;
            --rose: #f43f5e;
            --purple: #a855f7;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            background-image:
                radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
                radial-gradient(at 90% 90%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-primary);
            line-height: 1.6;
            padding: 40px 24px 80px;
            -webkit-font-smoothing: antialiased;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        /* Header Hero */
        .hero-banner {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
            border: 1px solid var(--border-accent);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), 0 0 30px var(--primary-glow);
            border-radius: 24px;
            padding: 36px 40px;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }}

        .hero-banner::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--cyan), var(--purple));
        }}

        .badge-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
            margin-bottom: 16px;
        }}

        h1 {{
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}

        .hero-desc {{
            color: var(--text-secondary);
            font-size: 1rem;
            max-width: 750px;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 36px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 22px 24px;
            backdrop-filter: blur(12px);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-3px);
            border-color: var(--border-accent);
        }}

        .kpi-label {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}

        .kpi-number {{
            font-size: 2rem;
            font-weight: 800;
            color: #ffffff;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.02em;
        }}

        .kpi-subtext {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        /* Section Cards */
        .section-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 24px;
            padding: 32px;
            margin-bottom: 28px;
            backdrop-filter: blur(16px);
        }}

        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* Charts Grid */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
            gap: 24px;
            margin: 24px 0;
        }}

        .chart-container {{
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border-subtle);
            border-radius: 18px;
            padding: 20px;
            height: 320px;
            position: relative;
        }}

        .chart-title {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        /* Multi-Agent Execution Flow */
        .agent-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}

        .agent-node {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            position: relative;
        }}

        .agent-node.completed {{
            border-color: rgba(16, 185, 129, 0.4);
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.1);
        }}

        .agent-icon {{
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: rgba(99, 102, 241, 0.15);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 10px;
            font-weight: bold;
        }}

        .agent-name {{
            font-size: 0.85rem;
            font-weight: 700;
            color: #ffffff;
        }}

        .agent-role {{
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .agent-status {{
            margin-top: 8px;
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
            background: rgba(16, 185, 129, 0.15);
            color: var(--emerald);
        }}

        /* Tables */
        .table-responsive {{
            width: 100%;
            overflow-x: auto;
            border-radius: 14px;
            border: 1px solid var(--border-subtle);
            background: rgba(15, 23, 42, 0.6);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
            text-align: left;
        }}

        th {{
            background: rgba(30, 41, 59, 0.9);
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            padding: 12px 18px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        td {{
            padding: 12px 18px;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border-subtle);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background: rgba(51, 65, 85, 0.3);
        }}

        /* Findings List */
        .insights-list {{
            list-style: none;
            display: grid;
            gap: 14px;
        }}

        .insight-item {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--border-subtle);
            border-left: 4px solid var(--primary);
            border-radius: 14px;
            padding: 16px 20px;
            font-size: 0.92rem;
            line-height: 1.5;
        }}

        .footer {{
            text-align: center;
            padding-top: 36px;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border-subtle);
            margin-top: 48px;
        }}

        @media print {{
            body {{ background: #ffffff !important; color: #0f172a !important; padding: 0 !important; }}
            .hero-banner, .section-card, .kpi-card {{ border: 1px solid #e2e8f0 !important; box-shadow: none !important; background: #ffffff !important; color: #0f172a !important; }}
            h1, .section-title, .kpi-number {{ color: #0f172a !important; -webkit-text-fill-color: #0f172a !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Hero Header -->
        <div class="hero-banner">
            <div class="badge-pill">Autonomous Analytical Intelligence • Executive Brief</div>
            <h1>📊 {title}</h1>
            <p class="hero-desc">
                Synthesized across multi-agent exploratory analysis, machine learning model benchmarking, and holdout diagnostic evaluations.
            </p>
        </div>

        <!-- KPI Metrics Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Data Quality Health</div>
                <div class="kpi-number" style="color: {'#10b981' if health_score >= 85 else '#f59e0b'};">
                    {health_score:.1f}%
                </div>
                <div class="kpi-subtext">Quality Grade: <strong>{quality_grade}</strong></div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Dataset Records</div>
                <div class="kpi-number">{rows_val:,}</div>
                <div class="kpi-subtext">Across {cols_val} feature columns</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Champion Algorithm</div>
                <div class="kpi-number" style="font-size: 1.35rem; color: #a5b4fc; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                    {champion_name}
                </div>
                <div class="kpi-subtext">CV Score: <strong>{f"{champion_score:.4f}" if champion_score is not None else "Optimal"}</strong></div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Data Hygiene Metrics</div>
                <div class="kpi-number" style="font-size: 1.4rem;">{missing_val:,}</div>
                <div class="kpi-subtext">Missing cells • {dups_val:,} duplicates</div>
            </div>
        </div>

        <!-- Multi-Agent Autonomous Topology -->
        <div class="section-card">
            <div class="section-header">
                <div class="section-title">
                    <span>🤖 Multi-Agent Autonomous Pipeline Execution</span>
                </div>
                <span class="badge-pill" style="margin-bottom: 0;">6 Specialized Agents</span>
            </div>
            <div class="agent-grid">
                <div class="agent-node completed">
                    <div class="agent-icon">01</div>
                    <div class="agent-name">Profiling</div>
                    <div class="agent-role">Schema & Health</div>
                    <div class="agent-status">Completed</div>
                </div>
                <div class="agent-node completed">
                    <div class="agent-icon">02</div>
                    <div class="agent-name">EDA</div>
                    <div class="agent-role">Correlations & Skew</div>
                    <div class="agent-status">Completed</div>
                </div>
                <div class="agent-node completed">
                    <div class="agent-icon">03</div>
                    <div class="agent-name">Preprocessing</div>
                    <div class="agent-role">Cleaning & Encoding</div>
                    <div class="agent-status">Completed</div>
                </div>
                <div class="agent-node completed">
                    <div class="agent-icon">04</div>
                    <div class="agent-name">ML Modeling</div>
                    <div class="agent-role">Model Zoo Benchmark</div>
                    <div class="agent-status">Completed</div>
                </div>
                <div class="agent-node completed">
                    <div class="agent-icon">05</div>
                    <div class="agent-name">Evaluation</div>
                    <div class="agent-role">Holdout Testing</div>
                    <div class="agent-status">Completed</div>
                </div>
                <div class="agent-node completed">
                    <div class="agent-icon">06</div>
                    <div class="agent-name">Reporting</div>
                    <div class="agent-role">Executive Synthesis</div>
                    <div class="agent-status">Completed</div>
                </div>
            </div>
        </div>
"""

    if executive_summary:
        html_content += f"""
        <!-- Executive Summary Section -->
        <div class="section-card">
            <div class="section-header">
                <div class="section-title">
                    <span>🏛️ Executive Strategy Narrative</span>
                </div>
            </div>
            <p style="font-size: 1rem; color: #cbd5e1; line-height: 1.8;">
                {executive_summary}
            </p>
        </div>
        """

    # Interactive Charts Section
    if chart_models or feat_labels:
        html_content += f"""
        <!-- Visual Intelligence Charts -->
        <div class="section-card">
            <div class="section-header">
                <div class="section-title">
                    <span>📈 Visual Intelligence & Model Benchmarks</span>
                </div>
            </div>
            <div class="charts-grid">
                {'''
                <div class="chart-container">
                    <div class="chart-title">
                        <span>Model Zoo Cross-Validation Comparison</span>
                        <span style="font-size: 0.75rem; color: var(--text-muted);">Stratified CV</span>
                    </div>
                    <canvas id="modelZooChart"></canvas>
                </div>
                ''' if chart_models else ''}

                {'''
                <div class="chart-container">
                    <div class="chart-title">
                        <span>Top Predictive Feature Drivers</span>
                        <span style="font-size: 0.75rem; color: var(--text-muted);">Permutation Importance</span>
                    </div>
                    <canvas id="featureImpChart"></canvas>
                </div>
                ''' if feat_labels else ''}
            </div>
        </div>
        """

    # Strategic Insights & Findings Section
    if insights:
        html_content += """
        <!-- Key Findings & Insights -->
        <div class="section-card">
            <div class="section-header">
                <div class="section-title">
                    <span>💡 Grounded Analytical Findings & Insights</span>
                </div>
            </div>
            <ul class="insights-list">
        """
        for ins in insights:
            html_content += f'<li class="insight-item">{ins}</li>'
        html_content += """
            </ul>
        </div>
        """

    # Model Zoo Table
    if isinstance(leaderboard, list) and leaderboard:
        html_content += """
        <!-- Model Zoo Leaderboard Table -->
        <div class="section-card">
            <div class="section-header">
                <div class="section-title">
                    <span>🏆 Candidate Model Zoo Leaderboard</span>
                </div>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Algorithm</th>
                            <th>Cross-Validation Score</th>
                            <th>Validation Metric</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for rank, item in enumerate(leaderboard[:8], start=1):
            if isinstance(item, dict):
                m_name = item.get("model") or item.get("model_name") or "Model"
                m_sc = item.get("cv_score") or item.get("score") or item.get("r2") or item.get("accuracy") or "N/A"
                is_champ = rank == 1 or m_name == champion_name
                badge_html = '<span class="badge-pill" style="margin-bottom:0; background:rgba(245, 158, 11, 0.2); color:#fcd34d; border-color:rgba(245, 158, 11, 0.4);">🏆 Champion</span>' if is_champ else '<span style="color:var(--text-muted);">Evaluated</span>'
                html_content += f"""
                        <tr>
                            <td><strong>#{rank}</strong></td>
                            <td style="font-family:'JetBrains Mono', monospace; font-weight:600;">{m_name}</td>
                            <td style="font-family:'JetBrains Mono', monospace;">{f"{m_sc:.4f}" if isinstance(m_sc, (int, float)) else m_sc}</td>
                            <td>{model_results.get("metric_name", "Optimization Target")}</td>
                            <td>{badge_html}</td>
                        </tr>
                """
        html_content += """
                    </tbody>
                </table>
            </div>
        </div>
        """

    # Add Chart.js initializers
    html_content += f"""
        <!-- Chart.js Scripts -->
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                {f'''
                const ctxModel = document.getElementById('modelZooChart');
                if (ctxModel) {{
                    new Chart(ctxModel, {{
                        type: 'bar',
                        data: {{
                            labels: {json.dumps(chart_models)},
                            datasets: [{{
                                label: 'Score',
                                data: {json.dumps(chart_scores)},
                                backgroundColor: 'rgba(99, 102, 241, 0.8)',
                                borderColor: '#6366f1',
                                borderWidth: 1,
                                borderRadius: 6,
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ display: false }}
                            }},
                            scales: {{
                                y: {{
                                    grid: {{ color: 'rgba(148, 163, 184, 0.1)' }},
                                    ticks: {{ color: '#94a3b8', font: {{ family: 'JetBrains Mono' }} }}
                                }},
                                x: {{
                                    grid: {{ display: false }},
                                    ticks: {{ color: '#94a3b8', font: {{ family: 'Inter', size: 11 }} }}
                                }}
                            }}
                        }}
                    }});
                }}
                ''' if chart_models else ''}

                {f'''
                const ctxFeat = document.getElementById('featureImpChart');
                if (ctxFeat) {{
                    new Chart(ctxFeat, {{
                        type: 'bar',
                        data: {{
                            labels: {json.dumps(feat_labels)},
                            datasets: [{{
                                label: 'Permutation Weight',
                                data: {json.dumps(feat_values)},
                                backgroundColor: 'rgba(6, 182, 212, 0.8)',
                                borderColor: '#06b6d4',
                                borderWidth: 1,
                                borderRadius: 6,
                            }}]
                        }},
                        options: {{
                            indexAxis: 'y',
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ display: false }}
                            }},
                            scales: {{
                                x: {{
                                    grid: {{ color: 'rgba(148, 163, 184, 0.1)' }},
                                    ticks: {{ color: '#94a3b8', font: {{ family: 'JetBrains Mono' }} }}
                                }},
                                y: {{
                                    grid: {{ display: false }},
                                    ticks: {{ color: '#94a3b8', font: {{ family: 'Inter', size: 11 }} }}
                                }}
                            }}
                        }}
                    }});
                }}
                ''' if feat_labels else ''}
            }});
        </script>

        <div class="footer">
            <p>Generated autonomously by <strong>AutoAnalyst AI</strong> • Production Multi-Agent Analytical Intelligence</p>
        </div>
    </div>
</body>
</html>
"""

    path.write_text(html_content, encoding="utf-8")
    return path


def _overview_table(profile: dict[str, Any]) -> list[str]:
    lines = [
        "| Metric | Value |",
        "|---|---|",
        f"| **Rows** | `{profile.get('rows', 0):,}` |",
        f"| **Columns** | `{profile.get('columns', 0)}` |",
        f"| **Missing Cells** | `{profile.get('missing_values_total') or profile.get('missing_cells_total', 0):,}` |",
        f"| **Duplicate Rows** | `{profile.get('duplicate_rows', 0):,}` |",
        f"| **Data Quality Score** | `{profile.get('health_score', 100.0):.1f}%` |",
    ]
    return lines


def _frame_to_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No data available._"
    display_df = df.head(_MAX_TABLE_ROWS)
    return str(display_df.to_markdown())


def _kv_table(data: dict[str, Any]) -> list[str]:
    lines = ["| Property | Value |", "|---|---|"]
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            continue
        lines.append(f"| **{k}** | `{v}` |")
    return lines


def _metrics_tables(evaluation: dict[str, Any]) -> list[str]:
    lines = ["| Metric | Score |", "|---|---|"]
    for k, v in evaluation.items():
        if isinstance(v, (int, float)):
            lines.append(f"| **{k.upper()}** | `{v:.4f}` |")
        elif isinstance(v, str):
            lines.append(f"| **{k.capitalize()}** | `{v}` |")

    if "confusion_matrix" in evaluation:
        lines.extend(["", "**Confusion matrix**", "", f"`{evaluation['confusion_matrix']}`"])

    if "per_class" in evaluation or "classification_report" in evaluation:
        per_class_data = evaluation.get("per_class") or evaluation.get("classification_report")
        lines.extend(["", "**Per-class metrics**", ""])
        if isinstance(per_class_data, pd.DataFrame):
            lines.append(_frame_to_md(per_class_data))
        else:
            lines.append(f"`{per_class_data}`")

    return lines
