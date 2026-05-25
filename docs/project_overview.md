# AutoAnalyst AI - Project Overview

## Project Name

AutoAnalyst AI

## Vision

Build a professional AI-powered data analysis assistant that can accept a dataset, understand its structure, profile data quality, perform exploratory analysis, clean and transform data, train baseline models, evaluate results, generate insights, and produce a readable report through an interactive dashboard.

## Product Goal

AutoAnalyst AI should help students, analysts, and junior data practitioners move from raw dataset to structured analytical findings with less manual work and better workflow discipline.

## Core Capabilities

1. Upload or load CSV/Excel datasets.
2. Generate automatic data profile summaries.
3. Detect missing values, duplicate rows, data types, and basic quality issues.
4. Run EDA summaries and visual analysis.
5. Clean data using configurable preprocessing strategies.
6. Engineer useful features for machine learning.
7. Train baseline classification and regression models.
8. Evaluate models using standard metrics.
9. Generate human-readable analytical insights.
10. Export Markdown reports.
11. Present the workflow through a Streamlit dashboard.
12. Extend the system with LangChain and LangGraph agent workflows.

## Target Users

- Data science students
- Junior data analysts
- AI/Data Science project teams
- Educators who need a structured team project
- Portfolio builders who want a professional GitHub repository

## Current Technical Base

- Python package under `src/autoanalyst/`
- Streamlit app under `app/`
- Tests under `tests/`
- Documentation under `docs/`
- GitHub workflow templates under `.github/`

## Future Direction

The project should evolve from a basic modular analytics toolkit into an agentic data-analysis system powered by LangChain and LangGraph. Agents should coordinate loading, profiling, EDA, cleaning, modeling, evaluation, insight writing, and report generation.
