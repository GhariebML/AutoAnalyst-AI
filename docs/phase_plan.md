# Project Phase Plan

## Phase 0 - Repository Setup and Team Alignment

Goal: Prepare the team and repository for safe collaboration.

Tasks:

- Confirm repository remote and branch strategy.
- Confirm the final 7-team assignment and branch ownership.
- Create GitHub Issues for each team.
- Confirm environment setup instructions.
- Run baseline tests.

Acceptance Criteria:

- All members can clone and run the project.
- All teams know their branches and deliverables.
- `pytest` passes on the base project.

## Phase 1 - Foundation Modules

Goal: Strengthen the existing Python modules.

Teams involved:

- Team 2: Data Understanding & Profiling
- Team 3: EDA & Visualization
- Team 4: Preprocessing & Feature Engineering
- Team 5: Machine Learning

Acceptance Criteria:

- Core modules have clear functions and docstrings.
- Important edge cases are tested.
- No syntax errors using `python -m compileall -q app src tests`.

## Phase 2 - Evaluation and Insights

Goal: Evaluate model outputs and convert technical metrics into clear insights.

Teams involved:

- Team 6 leads Evaluation & Insights.
- Team 5 provides model predictions and model comparison outputs.
- Team 2-4 provide profiling, EDA, and preprocessing context for insight generation.

Acceptance Criteria:

- Classification and regression metrics are documented and tested.
- Evaluation outputs are structured for `PipelineResult.evaluation_results`.
- Insight outputs are structured for `PipelineResult.insights`.
- Recommendations are clear, grounded, and safe for non-technical readers.

## Phase 3 - Dashboard and Reporting Integration

Goal: Turn backend modules into a usable product.

Teams involved:

- Team 7 leads Reporting & Dashboard.
- Teams 2-6 provide integration outputs.

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
