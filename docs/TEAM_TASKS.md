# Team Tasks – Phase 1 (Detailed Execution Plan)

> **Goal:** Every team member can independently pick up their agent, follow a strict professional workflow, and deliver a clean, tested, schema‑compliant placeholder that integrates with the orchestrator.

---

## 0. Pre‑requisites (Everyone)

1. **Clone the repository**
   ```bash
   git clone https://github.com/GhariebML/ADPilot.git
   cd ADPilot
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install all dependencies**
   ```bash
   python -m pip install -e .[dev]
   ```

4. **Verify the environment works**
   ```bash
   pytest -q
   ruff check .
   ```
   You should see **10 passed tests** and **no lint errors**.

5. **Create your own feature branch**
   ```bash
   git checkout -b feature/<your_agent_name>
   # Example: git checkout -b feature/research_agent
   ```

---

## 1. Shared Rules (Non‑negotiable)

- ✅ **All agent inputs/outputs MUST use Pydantic schemas** from  
  `src/adpilot/schemas/agent_schemas.py`
- ✅ **No raw strings between agents** – only typed objects.
- ✅ **All public methods must be `async`** (even if they raise `NotImplementedError`).
- ✅ **No real LLM calls, no external APIs** in Phase 1.
- ✅ **Every agent must have at least one pytest test** validating schema compliance.
- ✅ **Run `ruff check .` and `pytest -q` before every commit**.
- ✅ **Commit messages must follow this format:**
  ```
  feat(<agent>): add placeholder for <AgentName>

  - Define class inheriting BaseAgent
  - Add input/output typing
  - Add unit test for schema validation
  ```

---

## 2. Role‑by‑Role Task Breakdown

### 👤 Gharieb — Schemas, BaseAgent, Orchestrator, Strategy Agent

#### Step‑by‑Step
1. **Review and finalize `src/adpilot/schemas/agent_schemas.py`**
   - Ensure all enums, shared types, and validation rules are correct.
   - Add `model_config` with `json_schema_extra` examples to key models.

2. **Implement / verify `src/adpilot/core/base_agent.py`**
   - Confirm `BaseAgent` is abstract.
   - Ensure `validate_input`, `validate_output`, `parse_json_output` are present.

3. **Implement `src/adpilot/orchestration/orchestrator.py`**
   - Define execution order in comments:
     ```
     1. StrategyAgent
     2. ResearchAgent
     3. ContentAgent
     4. AnalyticsAgent
     5. DesignAgent
     6. CampaignManagerAgent
     ```
   - Add method signatures:
     - `async run()`
     - `async run_agent()`
     - `collect_run_record()`
     - `assemble_final_output()`
   - Raise `NotImplementedError` for now.

4. **Implement StrategyAgent placeholder**
   - File: `src/adpilot/agents/strategy_agent.py`
   - Class: `StrategyAgent(BaseAgent)`
   - Set:
     ```python
     name = "strategy_agent"
     input_model = StrategyAgentInput
     output_model = StrategyAgentOutput
     prompt_path = "prompts/strategy_system_prompt.md"
     ```
   - `async run()` → raises `NotImplementedError`

5. **Add tests**
   - `tests/test_schemas.py` (expand if needed)
   - `tests/test_project_structure.py` (already exists)

6. **Git & Push**
   ```bash
   git add .
   git commit -m "feat(core): finalize schemas, base agent, orchestrator, strategy agent"
   git push origin feature/strategy_agent
   ```
   Then open a **Pull Request → `develop` branch**.

---

### 👤 Awni — Research Agent

#### Step‑by‑Step
1. **Study these files carefully**
   - `src/adpilot/schemas/agent_schemas.py` → `ResearchAgentInput`, `ResearchAgentOutput`
   - `src/adpilot/core/base_agent.py`

2. **Implement ResearchAgent**
   - File: `src/adpilot/agents/research_agent.py`
   - Class: `ResearchAgent(BaseAgent)`
   - Set:
     ```python
     name = "research_agent"
     input_model = ResearchAgentInput
     output_model = ResearchAgentOutput
     prompt_path = "prompts/research_system_prompt.md"
     ```
   - `async run()` → raises `NotImplementedError`

3. **Add a test file**
   - File: `tests/test_research_agent.py`
   - Example test:
     ```python
     from adpilot.agents.research_agent import ResearchAgent
     from adpilot.schemas.agent_schemas import ResearchAgentInput, ResearchAgentOutput

     def test_research_agent_exists():
         agent = ResearchAgent()
         assert agent.name == "research_agent"
         assert agent.input_model is ResearchAgentInput
         assert agent.output_model is ResearchAgentOutput
     ```

4. **Validate**
   ```bash
   pytest tests/test_research_agent.py -v
   ruff check src/adpilot/agents/research_agent.py
   ```

5. **Push**
   ```bash
   git add .
   git commit -m "feat(research): add ResearchAgent placeholder and test"
   git push origin feature/research_agent
   ```

---

### 👤 Sleem — Content Agent

#### Step‑by‑Step
1. **Study schemas**
   - `ContentAgentInput`, `ContentAgentOutput`
   - Note: `ads` must cover at least two funnel stages later.
   - Note: `hashtags` must be lowercase.

2. **Implement ContentAgent**
   - File: `src/adpilot/agents/content_agent.py`
   - Class: `ContentAgent(BaseAgent)`
   - Set:
     ```python
     name = "content_agent"
     input_model = ContentAgentInput
     output_model = ContentAgentOutput
     prompt_path = "prompts/content_system_prompt.md"
     ```

3. **Add tests**
   - File: `tests/test_content_agent.py`
   - Validate:
     - Class exists
     - Input/output models are correct
     - Hashtags lowercasing validator exists (schema level)

4. **Push**
   ```bash
   git add .
   git commit -m "feat(content): add ContentAgent placeholder and test"
   git push origin feature/content_agent
   ```

---

### 👤 Khaled — Analytics Agent

#### Step‑by‑Step
1. **Study schemas**
   - `AnalyticsAgentInput`, `AnalyticsAgentOutput`
   - Health scores must be 0–100.
   - `improvement_suggestions` must support `SuggestionPriority`.

2. **Implement AnalyticsAgent**
   - File: `src/adpilot/agents/analytics_agent.py`
   - Class: `AnalyticsAgent(BaseAgent)`

3. **Add tests**
   - File: `tests/test_analytics_agent.py`
   - Test:
     - Invalid health score rejected
     - Priority enum works
     - Predicted metrics include `confidence` and `basis`

4. **Push**
   ```bash
   git add .
   git commit -m "feat(analytics): add AnalyticsAgent placeholder and tests"
   git push origin feature/analytics_agent
   ```

---

### 👤 Karem — Design Agent

#### Step‑by‑Step
1. **Study schemas**
   - `DesignAgentInput`, `DesignAgentOutput`
   - `DesignBrief` must include:
     - `dalle_prompt`
     - `negative_prompt`
     - `concept`
     - `rationale`
   - `format` must be `png`, `jpg`, or `webp`.

2. **Implement DesignAgent**
   - File: `src/adpilot/agents/design_agent.py`
   - Class: `DesignAgent(BaseAgent)`

3. **Add tests**
   - File: `tests/test_design_agent.py`
   - Test invalid image format rejected.
   - Test `GeneratedVisual.image_url` can be a placeholder.

4. **Push**
   ```bash
   git add .
   git commit -m "feat(design): add DesignAgent placeholder and tests"
   git push origin feature/design_agent
   ```

---

## 3. Pull Request & Code Review Workflow

1. Push your feature branch.
2. Open a **Pull Request** into `develop` (not `main`).
3. Fill PR description:
   - What agent you implemented
   - Which schemas you depend on
   - How you tested it
4. Assign **Gharieb** as reviewer.
5. CI must pass (GitHub Actions → ruff + pytest).
6. After approval → **Squash merge** into `develop`.

---

## 4. Final Integration (End of Phase 1)

Once all agents are merged into `develop`:

1. Gharieb runs:
   ```bash
   pytest -q
   python scripts/validate_schemas.py
   ```
2. Confirm `Orchestrator` can at least import all agents without error.
3. Merge `develop` → `main` with a **Release tag**:
   ```
   v0.1.0-phase1
   ```

---

## 5. What NOT to Do (Watch‑outs)

🚫 Do not:
- Call OpenAI, SerpAPI, or any external API.
- Write real business logic inside `run()`.
- Change another member’s agent file.
- Push directly to `main` or `develop`.
- Ignore failing tests or lint errors.

✅ Do:
- Keep your agent isolated.
- Trust the Pydantic schemas as the contract.
- Ask questions early if a schema feels unclear.

---

## 6. Helpful Commands Cheat Sheet

```bash
# Run all tests
pytest -q

# Run a single test file
pytest tests/test_research_agent.py -v

# Lint your code
ruff check src/adpilot/agents/research_agent.py

# Check schema import works
python -c "from adpilot.schemas.agent_schemas import ResearchAgentOutput"

# See changed files
git status

# See commit history
git log --oneline
```

---

**Good luck, team – let’s build this the right way.** 🚀
