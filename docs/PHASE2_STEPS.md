# Phase 2 – Professional Next‑Step Guide

**Objective:** Transition the AdPilot prototype from a Phase 1 skeleton to a fully functional, production‑ready multi‑agent marketing automation platform.

---

## 1️⃣ Core Development Milestones

| Milestone | Description | Owner(s) | Deliverable | Target Sprint |
|-----------|-------------|----------|-------------|---------------|
| **2.1 LLM Integration** | Replace placeholder logic with real LLM calls (OpenAI / Azure / OpenRouter). Implement streaming, retry, and rate‑limit handling. | Gharieb (Strategy), Sleem (Content) | Fully functional `run` methods returning validated JSON. | Sprint 1 |
| **2.2 Orchestrator Enhancement** | Implement end‑to‑end pipeline orchestration, error propagation, and partial‑run retries. | Khaled (Analytics) | `Orchestrator` class with async orchestration, fallback handling, and logging. | Sprint 2 |
| **2.3 Persistent Storage** | Add PostgreSQL (or SQLite for dev) to store campaign inputs, intermediate outputs, and final packages. | Karem (Design) | DB schema + CRUD services in `src/adpilot/services/db`. | Sprint 3 |
| **2.4 API Layer** | Expose the pipeline via a FastAPI REST endpoint with OpenAPI docs, auth (JWT), and rate limiting. | Awni (Research) | `src/adpilot/api` module, `/run_campaign` endpoint. | Sprint 4 |
| **2.5 Front‑end Dashboard** | Build a React dashboard to submit briefs, monitor progress, and view final assets. | Whole team (UI/UX) | Deployable dashboard under `frontend/`. | Sprint 5 |
| **2.6 CI/CD & Deploy** | Configure GitHub Actions for linting, testing, building Docker image, and pushing to a container registry. Deploy to Azure App Service or Railway. | DevOps (Khaled) | Fully automated pipeline, production‑ready Docker image. | Sprint 6 |

---

## 2️⃣ Detailed Task Breakdown

### 2.1 LLM Integration
1. **Add LLM client configuration** – Extend `src/adpilot/services/llm_client.py` to support multiple providers, timeout, and exponential back‑off.
2. **Update agents** – Replace placeholder `_placeholder_output` with real `client.chat(messages)` calls.
3. **Response parsing** – Centralise JSON extraction and schema validation (common helper).
4. **Unit tests** – Mock LLM responses and verify output validation.
5. **Documentation** – Add usage examples to `docs/LLM_INTEGRATION.md`.

### 2.2 Orchestrator Enhancement
1. **Define orchestrator flow** – Sequence: Strategy → Research → Content → Analytics → Design → Campaign Manager.
2. **Parallel execution** – Run independent agents concurrently when possible (e.g., Research & Content).
3. **Retry policy** – If any agent fails, retry up to 2 times with jitter before aborting.
4. **Logging & telemetry** – Emit structured logs (JSON) and metrics (duration, success/failure).

### 2.3 Persistent Storage
1. **Model mapping** – Create SQLAlchemy models corresponding to each agent’s output schema.
2. **Migrations** – Use Alembic for schema versioning.
3. **Repository layer** – Simple CRUD service (`src/adpilot/services/repository.py`).
4. **Tests** – In‑memory SQLite for unit tests.

### 2.4 API Layer
1. **FastAPI app skeleton** – `src/adpilot/api/main.py` with CORS and exception handlers.
2. **Authentication** – JWT‑based auth, admin scopes for write operations.
3. **Endpoint spec** – `POST /campaigns` (submit brief), `GET /campaigns/{id}` (status, assets).
4. **OpenAPI docs** – Auto‑generated, include example payloads.

### 2.5 Front‑end Dashboard
1. **Project bootstrap** – Create React app with TypeScript (`create-react-app` or Vite).
2. **UI components** – Brief form, live progress bar, result viewer with download links.
3. **State management** – Use React Query for async API calls and caching.
4. **Styling** – Tailwind CSS for rapid, consistent UI.
5. **Deployment** – Build static assets and serve via FastAPI static mount or Netlify.

### 2.6 CI/CD & Deploy
1. **GitHub Actions** – Lint (ruff), type‑check (mypy), test (pytest), build Docker image.
2. **Dockerfile** – Multi‑stage build: builder + runtime.
3. **Deploy** – Push Docker image to GitHub Packages; deploy to Azure Web App for Containers.
4. **Monitoring** – Add basic health‑check endpoint and integrate with Azure Application Insights.

---

## 3️⃣ Communication & Process

- **Sprint Planning** – Weekly 30‑min sync to confirm sprint goals and blockers.
- **Pull‑Request Workflow** – Feature branches from `develop`, require at least one review, and CI must pass before merge.
- **Documentation Ownership** – Each owner updates the corresponding `docs/` section after completing their milestone.
- **Retrospective** – End of each sprint, discuss what went well, what can improve, and adjust the roadmap.

---

## 4️⃣ Resources & References

- **AdPilot Architecture Diagram** – `docs/ARCHITECTURE.md`
- **LLM Provider Docs** – OpenAI, Azure OpenAI, OpenRouter.
- **FastAPI Best Practices** – https://fastapi.tiangolo.com/tutorial/
- **React + TypeScript Boilerplate** – https://github.com/ViteJS/vite-react-ts-starter
- **Docker Multi‑Stage Guide** – https://docs.docker.com/develop/develop-images/multistage-build/

---

*Prepared by Medo for Gharieb’s team – professional, actionable, and ready for immediate execution.*
