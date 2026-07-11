# Phase 1 – Agent Pipeline Foundation

## Goal
Create a clean, testable codebase that defines the data contracts and the
placeholder agent classes required for the multi‑agent marketing pipeline.

## Scope (What **is** built)
- Project skeleton, packaging, CI & lint configuration.
- Pydantic v2 schemas for every stage.
- Abstract ``BaseAgent`` with validation helpers.
- Placeholder agent classes (Strategy, Research, Content, Analytics, Design,
  CampaignManager) exposing ``async run`` signatures.
- Orchestrator class with method stubs that will later sequence the agents.
- Prompt template files with role, input/output schema references and the
  *return ONLY JSON* rule.
- Sample JSON payloads in ``data/samples``.
- Pytest test suite covering schema validation and project layout.

## What **is NOT** built
- Any real LLM or external API integration.
- Business logic inside agents.
- Database, web server, deployment, or UI.
- Full orchestrator execution.

## Definition of Done per Agent
| Agent | Expected Output (placeholder) |
|------|------------------------------|
| Strategy | ``StrategyAgentOutput`` model stub |
| Research | ``ResearchAgentOutput`` model stub |
| Content | ``ContentAgentOutput`` model stub |
| Analytics | ``AnalyticsAgentOutput`` model stub |
| Design | ``DesignAgentOutput`` model stub |
| CampaignManager | ``CampaignManagerOutput`` model stub |

Each placeholder raises ``NotImplementedError`` – the test suite merely checks
that the classes exist and have correct ``name``, ``input_model`` and
``output_model`` attributes.
