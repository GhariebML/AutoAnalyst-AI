# Project Phase Plan

## Phase 0 - Repository Setup and Team Alignment

Goal: Prepare the team and repository for safe collaboration.

Tasks:

- Confirm repository remote and branch strategy.
- Assign 14 members into 7 squads.
- Create GitHub Issues for each squad.
- Confirm environment setup instructions.
- Run baseline tests.

Acceptance Criteria:

- All members can clone and run the project.
- All squads know their branches and deliverables.
- `pytest` passes on the base project.

## Phase 1 - Foundation Modules

Goal: Strengthen the existing Python modules.

Squads involved:

- Squad 2: Data loading and profiling
- Squad 3: EDA
- Squad 4: Preprocessing and features
- Squad 5: Modeling and evaluation

Acceptance Criteria:

- Core modules have clear functions and docstrings.
- Important edge cases are tested.
- No syntax errors using `python -m compileall -q app src tests`.

## Phase 2 - Agentic Architecture with LangChain and LangGraph

Goal: Design the AI workflow layer.

Squads involved:

- Squad 6 leads.
- Other squads provide tool functions that agents can call.

Acceptance Criteria:

- Documented graph state.
- Nodes for profiling, EDA, cleaning, modeling, insights, and reporting.
- Deterministic dry-run path works without requiring secret API keys.
- Optional LLM integration is clearly isolated behind environment variables.

## Phase 3 - Dashboard and Reporting Integration

Goal: Turn backend modules into a usable product.

Squads involved:

- Squad 7 leads.
- Squad 2-6 provide integrations.

Acceptance Criteria:

- User can upload a dataset.
- Dashboard shows profile, EDA summary, insights, and report export.
- Errors are shown clearly to the user.
- No hardcoded local paths.

## Phase 4 - Testing, QA, and Documentation

Goal: Prepare the project for professional presentation.

Tasks:

- Add missing tests.
- Run full validation.
- Review docs for consistency.
- Prepare final report and demo.

Acceptance Criteria:

- `python -m compileall -q app src tests` passes.
- `pytest` passes.
- README and docs explain setup, usage, workflow, and architecture.
- Final report is complete.

## Phase 5 - Final Demo and Delivery

Goal: Present the working project.

Deliverables:

- Final Streamlit demo.
- Final report.
- GitHub repository walkthrough.
- Team contribution summary.
- Future improvements list.
