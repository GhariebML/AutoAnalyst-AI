# Phase 2 – Team Task Assignment

This document outlines the specific responsibilities for each team member during Phase 2 of AdPilot. It includes
* what needs to be done, 
* where the code lives, 
* how to test, and 
* what documentation to update.

---

## 1️⃣ Team Roles & Primary Owners

| Team Member | Primary Role | Focus Area | Key Deliverable(s) | Sprint Target |
|-------------|--------------|------------|--------------------|---------------|
| **Gharieb** | Lead Engineer (Strategy & Orchestrator) | **Strategy Agent** and **Orchestrator** | Validated `StrategyAgent.run` + orchestrator integration | Sprint 1 |
| **Awni**    | Research / Data Engineering | **Research Agent** & **Data persistence** | Finalized `ResearchAgent.run`, DB schema for research data | Sprint 2 |
| **Sleem**   | Content & Front‑End | **Content Agent** & **Dashboard** | Live content generation, UI for campaign briefs | Sprint 3 |
| **Khaled**  | Analytics & DevOps | **Analytics Agent**, CI/CD pipeline | Analytics Agent integration, Docker CI, monitoring | Sprint 4 |
| **Karem**   | Design & UX | **Design Agent** & **Design assets** | Automated visual specs, design preview UI | Sprint 5 |

---

## 2️⃣ Detailed Task Breakdown

> Each task is formulated as a *GitHub Issue* and linked in the feature branch. Please keep the branch name descriptive and short (e.g., `feature/<role>-<task>`).**

### 2.1 Strategy Agent (Gharieb)

- **Location:** `src/adpilot/agents/strategy_agent.py`
- **Implementation Steps:**
  1. Refactor the placeholder `_placeholder_output` into a private method `_generate_strategy` that builds the prompt.
  2. Use `LLMClient` to call the configured LLM with `temperature=0.0` for deterministic output.
  3. Implement streaming support (if the provider offers it) and collect the full response before JSON extraction.
  4. Add exponential back‑off retry logic (max 3 attempts, jitter 100‑300 ms).
  5. Store the raw LLM response in a new `StrategyRunLog` table for audit purposes.
- **Configuration:** Ensure an OpenAI (or alternative) API key is defined in `.env` as `OPENAI_API_KEY`. Add the key name to `.env.example` with a placeholder value.
- **Unit Tests:**
  - Create `tests/test_strategy_agent.py` with at least two test cases:
    * **Happy Path:** Mock `LLMClient.chat` to return a valid JSON payload; assert the returned `StrategyAgentOutput` matches the schema.
    * **Failure Path:** Mock a network error; verify the fallback `_placeholder_output` is used and that a warning is logged.
  - Use `pytest-mock` for mocking and `pytest-asyncio` for async test support.
- **Acceptance Criteria:**
  1. `StrategyAgent.run` returns a fully validated `StrategyAgentOutput` object.
  2. All new unit tests pass (`pytest -q` returns 0).
  3. CI pipeline runs `ruff check .` and `mypy` with no errors.
  4. The strategy run log is persisted without raising DB errors.
- **Documentation Updates:**
  - Extend `docs/USAGE.md` with a "Strategy Agent" section showing a sample Python snippet, the required `.env` variables, and the expected JSON response.
  - Add a new page `docs/STRATEGY_AGENT.md` describing the prompt design, model parameters, and fallback behavior.

**Review Process:**
- Submit a PR titled `feat(strategy): LLM integration & logging`.
- Require at least one reviewer from the team (preferably Khaled for DevOps feedback).
- Ensure the CI checks pass before merging.

---

### 2.2 Research Agent (Awni)

- **Location:** `src/adpilot/agents/research_agent.py` and `src/adpilot/services/db/` (Postgres tables for research data).
- **Implementation Steps:**
  1. Replace the deterministic placeholder with a real LLM call using `LLMClient` (same retry strategy as Strategy Agent).
  2. Serialize the raw LLM response into a new `ResearchRunLog` table for traceability.
  3. Map the validated `ResearchAgentOutput` into the `ResearchDocument` ORM model and persist it.
  4. Add a repository layer (`src/adpilot/services/research_repo.py`) exposing `save_research(document: ResearchDocument)`.
- **Data Model Details:**
  ```python
  class ResearchDocument(Base):
      __tablename__ = "research_documents"
      id: int = Column(Integer, primary_key=True, autoincrement=True)
      campaign_id: str = Column(String, index=True, nullable=False)
      competitor_analysis: JSON = Column(JSON, nullable=False)
      market_insights: JSON = Column(JSON, nullable=False)
      audience_personas: JSON = Column(JSON, nullable=False)
      research_summary: str = Column(Text, nullable=False)
      created_at: datetime = Column(DateTime, default=datetime.utcnow)
  ```
- **Unit Tests:**
  - **Success Test:** Mock `LLMClient.chat` to return a valid JSON; assert that `ResearchRepo.save_research` is called with a correctly populated `ResearchDocument`.
  - **DB Failure Test:** Simulate a DB integrity error; ensure the agent raises `AgentExecutionError` and the transaction rolls back.
  - Use `pytest-asyncio` and `pytest-mock` for async and mocking support.
- **Acceptance Criteria:**
  1. LLM‑driven research returns a validated `ResearchAgentOutput`.
  2. The output is persisted to the `research_documents` table without duplication.
  3. All new tests pass and CI reports 100 % coverage for the new repo layer.
  4. Rate‑limit handling respects the provider’s `X‑RateLimit‑Remaining` header (if present).
- **Documentation Updates:**
  - Create `docs/RESEARCH.md` covering the agent’s workflow, required environment variables, database schema, and example payloads.
  - Add a quick‑start snippet to `docs/USAGE.md` for running the research agent via CLI.

**Review Process:**
- PR title: `feat(research): LLM integration, persistence & logging`.
- Mandatory review by Khaled (DevOps) and Karem (UX) for data handling concerns.
- Ensure migrations are generated (`alembic revision --autogenerate`).

---

### 2.3 Content Agent & Dashboard (Sleem)

- **Content Agent Location:** `src/adpilot/agents/content_agent.py`
- **Implementation Steps:**
  1. Refactor the agent to use streaming (if supported) and assemble the final JSON only after the full stream is received.
  2. Add a configurable `CONTENT_TEMPERATURE` env variable to control creativity.
  3. Persist the raw content generation log to a new `ContentRunLog` table.
  4. Ensure the agent validates the output against `ContentAgentOutput` and raises `AgentOutputError` on mismatch.
- **API Integration:**
  - Create a FastAPI route `POST /campaigns/{id}/content` that triggers the agent and returns a task ID.
  - Implement a status endpoint `GET /tasks/{task_id}` that reports `pending`, `in_progress`, or `completed`.
- **Frontend Dashboard:**
  - **Form:** Build a React component `CampaignBriefForm` (TypeScript) that captures the required fields (business name, product, budget, goals, etc.). Use `react-hook-form` for validation.
  - **Progress Viewer:** `CampaignProgress` component polls the task status every 5 seconds, shows a spinner, and displays a summary once completed.
  - **Result Display:** Render the generated ads, email sequences, and social posts in a tabbed view with copy‑to‑clipboard buttons.
  - **Styling:** Use Tailwind CSS; ensure WCAG AA contrast compliance.
- **Testing Strategy:**
  - **Backend:** Integration test that posts a brief, receives a task ID, polls until `completed`, and asserts the JSON structure.
  - **Frontend:** Jest + React Testing Library tests for form validation, API error handling, and proper rendering of the progress bar.
  - **E2E (optional):** Cypress test that runs through the whole flow in a headless browser.
- **Documentation Updates:**
  - Add `docs/CONTENT.md` with an API usage example and a description of the content schema.
  - Add `docs/DASHBOARD.md` covering the React architecture, state management, and how to run the UI locally (`npm install && npm run dev`).
- **Acceptance Criteria:**
  1. Content agent returns a valid `ContentAgentOutput` for both mocked and real LLM runs.
  2. The FastAPI endpoint returns a correctly formatted task response (202 Accepted).
  3. The React UI shows real‑time progress and final assets without crashes.
  4. All unit, integration, and UI tests pass on CI.

**Review Process:**
- PR title: `feat(content): streaming, API & UI integration`.
- Required reviewers: Awni (API design) and Karem (UX/accessibility).
- Ensure the PR passes linting (`eslint` for frontend, `ruff` for backend) and the CI pipeline.

---

### 2.4 Analytics Agent & CI/CD (Khaled)

- **Analytics Agent Location:** `src/adpilot/agents/analytics_agent.py`
- **Implementation Steps:**
  1. Replace the placeholder logic with a real LLM call using `LLMClient`. Pass the full strategy, research, and content payloads.
  2. Cache the LLM response in Redis (or an in‑memory dict for dev) keyed by a hash of the input payload to avoid duplicate calls.
  3. Add validation for each `MetricPrediction` ensuring `confidence` is between 0‑100 and `basis` is a non‑empty string.
  4. Write the raw response and the hashed input into an `AnalyticsRunLog` table for audit.
- **CI/CD Pipeline:**
  - **Workflow File:** `.github/workflows/ci.yml`
    * **Jobs:** `lint`, `type_check`, `test`, `docker_build`, `docker_push`.
    * **Lint:** `ruff check .` with `--exit-zero` disabled (fail on warnings).
    * **Type‑check:** `mypy src/ tests/`.
    * **Test:** `pytest -q --cov=src`.
    * **Docker Build:** Multi‑stage Dockerfile; push image to `ghcr.io/ghariebml/adpilot` with tag `${{ github.sha }}`.
  - **Branch Protection:** Require passing CI before merge to `main`.
- **Monitoring & Telemetry:**
  - Add `/healthz` endpoint returning JSON `{status:"ok",timestamp:...}`.
  - Integrate Azure Application Insights using the `opencensus-ext-azure` SDK; emit custom metrics for agent execution time and error rates.
- **Documentation:**
  - `docs/ANALYTICS.md` – agent workflow, cache strategy, and example KPI output.
  - `docs/CI_CD.md` – step‑by‑step guide on the CI pipeline, Docker tags, and deployment to Azure.
- **Acceptance Criteria:**
  1. Analytics agent produces a validated `AnalyticsAgentOutput` for both mocked and live LLM responses.
  2. Cache hits skip the LLM call and return the stored result.
  3. CI pipeline passes all stages on every push.
  4. Docker image builds without errors and can be run locally (`docker run -p 8000:8000 <image>`).
  5. Health endpoint returns 200 OK within 200 ms.
- **Review Process:**
  - PR title: `feat(analytics): LLM + caching + CI/CD`.
  - Mandatory reviewers: Gharieb (architecture) and Awni (API).
  - Verify that the workflow uses the `GITHUB_TOKEN` for image push and respects the rate limits of the LLM provider.

---

### 2.5 Design Agent & Visual Assets (Karem)

- **Design Agent Location:** `src/adpilot/agents/design_agent.py`
- **Implementation Steps:**
  1. Build a prompt that combines the `DesignBrief` fields (color palette, mood, format) and send it to an image generation service (OpenAI DALL·E 3 or Stable Diffusion via Replicate).
  2. Receive the generated image URL, verify HTTP status 200, and store it in a new `DesignAsset` ORM model:
     ```python
     class DesignAsset(Base):
         __tablename__ = "design_assets"
         id: int = Column(Integer, primary_key=True)
         campaign_id: str = Column(String, index=True, nullable=False)
         brief_json: JSON = Column(JSON, nullable=False)
         image_url: str = Column(String, nullable=False)
         created_at: datetime = Column(DateTime, default=datetime.utcnow)
     ```
  3. If the provider returns a base64 image, upload it to Cloudinary (or Azure Blob) and store the public URL.
  4. Add a fallback generation of placeholder images using `picsum.photos` when the API key is missing (similar to the Phase 1 placeholder).
- **Frontend Integration:**
  - Add a **Design Preview** tab in `frontend/src/components/DesignPreview.tsx` that fetches `/api/campaigns/{id}/design-assets` and displays a responsive grid of thumbnails.
  - Include a “Download all” button that bundles assets into a zip on the server (`src/adpilot/services/zip_service.py`).
- **Testing:**
  - **Backend:** Mock the image generation API; assert that `DesignAsset` records are created and the URL is saved.
  - **Frontend:** Use Cypress to verify that the preview tab loads images correctly and the download button triggers a file download.
- **Documentation:**
  - `docs/DESIGN.md` – explains prompt design, API keys (`DALL_E_API_KEY`), fallback behavior, and asset retrieval.
  - Update `docs/USAGE.md` with a “Retrieve Design Assets” code snippet.
- **Acceptance Criteria:**
  1. Design agent returns a `DesignAgentOutput` containing at least one `GeneratedVisual` with a reachable URL.
  2. Assets are persisted in the database and can be queried via the `/design-assets` endpoint.
  3. Frontend preview renders correctly on desktop and mobile viewports.
  4. All associated unit, integration, and UI tests pass.
- **Review Process:**
  - PR title: `feat(design): image generation & UI preview`.
  - Reviewers: Sleem (frontend) and Khaled (deployment).
  - Ensure the PR includes migration scripts (`alembic upgrade head`).

---

## 3️⃣ Communication & Status Tracking

| Channel | Frequency | Purpose |
|---------|-----------|---------|
| Core Team Slack | Daily | Quick questions, blockers |
| Project Repo | Continuous | Merge requests, issue updates |
| Weekly Sync | Every Friday | Sprint recap, next sprint planning |

During each sprint, please: 
1. Open a *feature* branch from `develop`.
2. Create a GitHub Issue with the task details.
3. Commit code with clear messages.
4. Push to remote and open a PR for review.
5. Update the corresponding `docs/` section.

---

## 4️⃣ Deliverables Checklist

- ✅ `StrategyAgent` LLM integration.
- ✅ `ResearchAgent` with persistent DB storage.
- ✅ `ContentAgent` + live FAQ API for the dashboard.
- ✅ `AnalyticsAgent` & CI/CD pipeline.
- ✅ `DesignAgent` with image generation.
- ✅ FastAPI with `/run_campaign` endpoint.
- ✅ React dashboard with brief form & progress viewer.
- ✅ Docker image and deployment to Azure Web App.
- ✅ Full documentation updated in `docs/`.

---

> **Key Reminder:** All functional code must pass the existing unit tests (`pytest -q`) before being merged. The CI pipeline will enforce linting, type‑checking, and testing automatically.

---

**Prepared by: Medo**
