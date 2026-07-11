# AdPilot Project Overview

## Project Name

AdPilot - AI-Powered Autonomous Marketing Agency

## Project Purpose

AdPilot is a multi-agent marketing automation platform that converts a structured campaign brief into a complete campaign package. The system coordinates specialized AI agents for strategy, research, content, analytics, design, and campaign management while keeping Pydantic schemas as the source of truth for structured data contracts.

## Main Features

- LangChain-based structured output through shared `BaseAgent`.
- Multi-provider LLM configuration for OpenAI, OpenRouter, and Hugging Face Inference Providers.
- Specialized agents for strategy, research, content, analytics, design, and campaign planning.
- FastAPI backend with pipeline and dashboard-compatible endpoints.
- React/Vite dashboard for local campaign submission, progress polling, and result display.
- Phase 1 runner scripts for each agent and the full pipeline.
- Test coverage for schemas, agent patterns, provider configuration, and dashboard behavior.

## Tech Stack

- Python 3.12+
- FastAPI
- Pydantic v2 and pydantic-settings
- LangChain and langchain-openai
- OpenAI-compatible provider APIs
- React 18, TypeScript, Vite, Tailwind CSS
- Pytest and Ruff

## Folder Structure

```text
src/adpilot/          Core Python package
src/adpilot/agents/   Specialized AI agents
src/adpilot/api/      FastAPI application
src/adpilot/core/     Configuration, base classes, shared utilities
src/adpilot/schemas/  Pydantic contracts used by agents and services
src/adpilot/services/ LLM, search, image, and task orchestration services
scripts/              Local agent and pipeline runners
tests/                Backend tests
frontend/             React/Vite dashboard
data/samples/         Example schema payloads
docs/                 Project and collaboration documentation
```

## How the System Works

1. A campaign brief is submitted as structured input.
2. `StrategyAgent` creates positioning, channels, and funnel strategy.
3. `ResearchAgent` creates Phase 1 synthetic audience and competitor research.
4. `ContentAgent` generates ads, email sequences, social posts, blog outlines, and CTA variants.
5. `AnalyticsAgent` scores the campaign and recommends improvements.
6. `DesignAgent` creates visual briefs and DALL-E-ready prompts without calling image APIs in Phase 1.
7. `CampaignManagerAgent` creates budget allocation, schedule, ad sets, A/B tests, and KPI targets when schemas are available.
8. The FastAPI layer exposes both direct pipeline endpoints and dashboard-friendly task endpoints.

## Main Modules

- `BaseAgent`: Shared LangChain structured-output execution pattern.
- `llm_client`: Provider selection and `ChatOpenAI` configuration.
- `config`: Environment-driven settings loaded through pydantic-settings.
- `task_manager`: Async orchestration of the multi-agent DAG.
- `api/main.py`: FastAPI routes for health, analytics evaluation, campaign runs, and dashboard tasks.
- `frontend/src`: Dashboard interface, API client, polling hook, and result components.

## Current Project Status

The project is prepared for collaborative GitHub development. Phase 1 agent integration is implemented with structured LLM output, multiple LLM providers are supported, and the local dashboard can run with professional demo output by default or the real pipeline when provider credentials are configured.

