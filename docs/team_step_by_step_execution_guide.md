# Team Step-by-Step Execution Guide

This guide explains how each AutoAnalyst AI team should finish its assigned tasks from start to Pull Request. Use it together with the team-specific guides in `docs/teams/`, the weekly tasks in `docs/weekly_tasks/`, and the central integration strategy in `docs/end_to_end_integration_strategy.md`.

## Universal Workflow for Every Team

Follow this workflow before starting any task:

1. Open the latest `develop` branch.

   ```bash
   git checkout develop
   git pull origin develop
   ```

2. Switch to your assigned feature branch.

   ```bash
   git checkout feature/your-team-branch
   git pull origin feature/your-team-branch
   git merge develop
   ```

3. Read your current task documents:
   - `docs/team_branch_assignments.md`
   - Your file under `docs/teams/`
   - Current week file under `docs/weekly_tasks/`
   - Any related architecture or workflow document.

4. Create a short checklist before editing:
   - What file will you change?
   - What function, section, chart, or report will you add?
   - What output should another team receive from your work?
   - How will you test or manually verify the result?

5. Make small focused changes. Avoid mixing unrelated work in one commit.

6. Run the smallest useful validation:

   ```bash
   python -m compileall -q app src tests
   pytest
   ```

   If tests cannot run, document the reason in the Pull Request.

7. Update your weekly progress file in `docs/weekly_updates/week_XX.md` with:
   - Completed work
   - Changed files
   - Testing or manual verification
   - Blockers
   - Next steps

8. Commit with a clear message.

   ```bash
   git add <changed-files>
   git commit -m "type(scope): short description"
   git push origin feature/your-team-branch
   ```

9. Open a Pull Request into `develop`, not `main`.

10. Request review, respond to comments, and only merge when approved.

## Team 1 â€” Project Management & GitHub / System Integration

**Members:** Mohamed Gharieb
**Branch:** `feature/project-management`

### Main Goal

Keep the repository organized, keep team documentation clear, manage GitHub workflow, and coordinate integration across all team outputs.

### Step-by-Step Tasks

1. Review repository status:
   - Confirm `main` and `develop` exist.
   - Confirm all feature branches exist.
   - Confirm PRs target `develop`.

2. Review documentation consistency:
   - Check `README.md`.
   - Check `docs/team_branch_assignments.md`.
   - Check `docs/team_plan_8_weeks.md`.
   - Check `docs/weekly_tasks/`.
   - Make sure team names, branches, and responsibilities match.

3. Create or update GitHub Issues:
   - One issue per team or major task.
   - Include objective, files to edit, deliverables, and Definition of Done.
   - Add labels such as `docs`, `feature`, `testing`, or team labels if available.

4. Coordinate integration:
   - Check that each team output connects to `src/autoanalyst/pipeline.py`.
   - Identify missing input/output contracts.
   - Ask teams to document blockers early.

5. Review Pull Requests:
   - Check branch name.
   - Check PR target is `develop`.
   - Check summary and testing notes.
   - Check no secrets, local paths, or broken Markdown are added.

6. Finalize weekly status:
   - Update weekly progress notes.
   - Summarize merged PRs, blockers, and next-week priorities.

### Done When

- All teams know their branch and task.
- Documentation is consistent.
- Integration blockers are visible.
- PRs are reviewed before merge.

## Team 2 â€” Data Understanding & Profiling

**Members:** Ø­Ø§Ø²Ù… + Ù…Ø­Ù…ÙˆØ¯ Ù…Ø§Ù‡Ø±
**Branch:** `feature/data-profiling`

### Main Goal

Understand the dataset, document its columns, and produce profiling outputs that other teams can use.

### Step-by-Step Tasks

1. Choose or confirm the dataset:
   - Record dataset name, source, license if available, size, and target column.
   - Confirm whether the problem is classification or regression.

2. Create or update `docs/data_dictionary.md`:
   - Add every important column.
   - Explain meaning, type, example values, and expected use.
   - Mark the target column clearly.

3. Improve data loading:
   - Review `src/autoanalyst/data_loading/`.
   - Make CSV/Excel loading return clear errors for missing files, unsupported formats, or empty files.

4. Build profiling outputs:
   - Rows and columns count.
   - Column names and data types.
   - Missing count and missing percentage.
   - Duplicate row count.
   - Unique value count per column.
   - Basic numeric summary where useful.

5. Save outputs in reusable structures:
   - Prefer dictionaries, DataFrames, or simple dataclasses.
   - Avoid printing only to console.
   - Make outputs easy for dashboard and reporting teams to consume.

6. Add tests or manual checks:
   - Valid CSV.
   - Empty CSV.
   - File not found.
   - Dataset with missing values.

7. Document findings:
   - Dataset limitations.
   - Columns with many missing values.
   - Potential leakage columns.
   - Suggested cleaning decisions for Team 4.

### Done When

- Data dictionary exists and is understandable.
- Profiling function returns structured output.
- Missing and duplicate reports are available.
- Team 3, Team 4, and Team 7 can use the outputs.

## Team 3 â€” EDA & Visualization

**Members:** Ø£ÙŠÙ‡ + Ø¢ÙŠÙ‡ Ø¹Ù…Ø§Ø¯
**Branch:** `feature/eda-visualization`

### Main Goal

Create exploratory summaries and visualizations that explain the dataset clearly.

### Step-by-Step Tasks

1. Read the data dictionary and profile summary from Team 2.

2. Define EDA questions:
   - What is the target distribution?
   - Which features are numeric?
   - Which features are categorical?
   - Which features may affect the target?
   - Are there outliers or strange values?

3. Implement EDA helpers in `src/autoanalyst/eda/`:
   - Numeric summary.
   - Categorical summary.
   - Correlation matrix.
   - Target distribution summary.

4. Implement visualizations:
   - Histograms for numeric columns.
   - Bar charts for categorical columns.
   - Box plots for outlier checks.
   - Correlation heatmap.
   - Feature vs target charts when possible.

5. Save chart outputs:
   - Save figures under `reports/figures/` when appropriate.
   - Use clear filenames.
   - Avoid hard-coded local machine paths.

6. Write EDA notes:
   - Key patterns.
   - Important relationships.
   - Outliers or data issues.
   - Recommendations for preprocessing and modeling.

7. Validate:
   - Run EDA on sample dataset.
   - Confirm charts render without errors.
   - Confirm functions handle missing values safely.

### Done When

- EDA functions run on the selected dataset.
- At least three useful chart types are available.
- Notes explain what the charts mean.
- Outputs can be used by reporting and dashboard teams.

## Team 4 â€” Preprocessing & Feature Engineering

**Members:** Ø¨Ø³Ù…Ù‡ + Ø±Ø¶ÙˆÙŠ
**Branch:** `feature/preprocessing-features`

### Main Goal

Prepare clean, model-ready data without losing important information.

### Step-by-Step Tasks

1. Read Team 2 profiling notes and Team 3 EDA notes.

2. Identify preprocessing needs:
   - Missing values.
   - Duplicate rows.
   - Categorical columns.
   - Numeric columns.
   - Date/time columns.
   - Columns to drop.

3. Implement cleaning functions:
   - Remove duplicates.
   - Handle missing numeric values.
   - Handle missing categorical values.
   - Preserve original DataFrame unless explicitly documented.

4. Implement preprocessing functions:
   - Encode categorical variables.
   - Scale numeric variables if needed.
   - Split features and target.
   - Train/test split helper if appropriate.

5. Implement feature engineering:
   - Datetime features such as year, month, day, weekday.
   - Simple derived numeric features when useful.
   - Avoid features that leak the target.

6. Return clean outputs:
   - Clean DataFrame.
   - Feature matrix `X`.
   - Target `y`.
   - Notes about transformations applied.

7. Add tests:
   - Missing values are handled correctly.
   - Encoding creates usable numeric columns.
   - Original data is not unexpectedly mutated.
   - Output shape is expected.

8. Document decisions:
   - Why each column was dropped, encoded, scaled, or transformed.

### Done When

- Cleaned data can be passed to Team 5 models.
- Preprocessing decisions are documented.
- Tests or manual verification prove the pipeline works.

## Team 5 â€” Machine Learning

**Members:** Ø§Ù„ÙƒÙˆÙ…ÙŠ + Ø§Ù„Ø´Ø§ÙŠØ¨
**Branch:** `feature/modeling`

### Main Goal

Train baseline machine learning models and provide clear model comparison results.

### Step-by-Step Tasks

1. Read cleaned dataset output from Team 4.

2. Confirm task type:
   - Classification if target is categories/classes.
   - Regression if target is numeric continuous value.

3. Prepare model input:
   - Confirm `X` contains numeric features.
   - Confirm `y` exists and has valid values.
   - Split into train/test if not already split.

4. Implement baseline models:
   - Classification: Logistic Regression, Decision Tree, Random Forest if suitable.
   - Regression: Linear Regression, Decision Tree Regressor, Random Forest Regressor if suitable.

5. Add model wrapper functions:
   - Input: `X_train`, `X_test`, `y_train`, `y_test`.
   - Output: trained model, predictions, and metadata.

6. Add model comparison:
   - Compare at least two models.
   - Return results as dictionary or DataFrame.
   - Include model name, metrics, and notes.

7. Save or document model artifacts if needed:
   - Do not commit large binary files unless agreed.
   - Prefer reproducible code and documented results.

8. Validate:
   - Run model on sample dataset.
   - Confirm no data leakage.
   - Confirm errors are clear when target column is missing.

### Done When

- Baseline model training works.
- Model comparison results are available.
- Team 6 can evaluate predictions and metrics.

## Team 6 â€” Evaluation & Insights

**Members:** Ø³Ù‡Ø§Ø¯ + Ù…Ø±ÙˆØ©
**Branch:** `feature/evaluation-insights`

### Main Goal

Evaluate model performance and convert technical outputs into understandable insights.

### Step-by-Step Tasks

1. Receive model predictions and test labels from Team 5.

2. Select metrics by task type:
   - Classification: accuracy, precision, recall, F1-score, confusion matrix.
   - Regression: MAE, MSE/RMSE, RÂ².

3. Implement evaluation helpers in `src/autoanalyst/evaluation/`:
   - One function for classification metrics.
   - One function for regression metrics.
   - Return structured dictionaries or DataFrames.

4. Generate insights in `src/autoanalyst/insights/`:
   - Explain strongest results.
   - Explain weak results.
   - Mention likely data limitations.
   - Suggest practical next steps.

5. Keep insights safe and deterministic:
   - Avoid unsupported claims.
   - Base insights on available metrics and data summaries.
   - Use clear beginner-friendly language.

6. Prepare outputs for report and dashboard:
   - Evaluation summary.
   - Metric table.
   - Confusion matrix or regression error summary.
   - Insight bullet list.

7. Validate:
   - Test classification metric function.
   - Test regression metric function.
   - Test insight output for missing or weak metrics.

### Done When

- Evaluation metrics are correct and readable.
- Insights explain model results clearly.
- Team 7 can display results in dashboard and report.

## Team 7 â€” Reporting & Dashboard

**Members:** ÙŠÙ…Ù†ÙŠ + Ù…Ø­Ù…Ø¯ ÙƒÙ…Ø§Ù„
**Branch:** `feature/reporting-dashboard`

### Main Goal

Create a user-friendly dashboard and final report that present the full analysis workflow.

### Step-by-Step Tasks

1. Review central pipeline usage:

   ```python
   from autoanalyst.pipeline import PipelineConfig, run_analysis_pipeline
   ```

2. Improve Streamlit upload flow:
   - Allow CSV upload.
   - Show dataset preview.
   - Show rows, columns, and target selection where needed.

3. Display pipeline outputs:
   - Data profile summary.
   - Missing values and duplicates.
   - EDA charts.
   - Preprocessing summary.
   - Model comparison.
   - Evaluation metrics.
   - Insight bullets.

4. Improve report generation:
   - Generate Markdown report.
   - Include dataset overview.
   - Include charts or chart references.
   - Include model and evaluation summaries.
   - Include recommendations.

5. Add user-friendly error handling:
   - No file uploaded.
   - Unsupported file.
   - Missing target column.
   - Model cannot train.

6. Prepare demo materials:
   - Screenshots.
   - Demo script.
   - Final presentation outline.

7. Validate:
   - Run `streamlit run app/streamlit_app.py`.
   - Upload sample CSV.
   - Confirm report can be generated.
   - Confirm dashboard does not duplicate backend logic unnecessarily.

### Done When

- Dashboard runs successfully.
- User can upload a dataset and see useful results.
- Report and demo materials are ready.

## Pull Request Template Checklist

Every PR should include this information in the description:

```markdown
## Summary
- What changed?
- Which team/task does this complete?

## Files Changed
- `path/to/file.py` â€” why it changed
- `path/to/doc.md` â€” why it changed

## Validation
- [ ] `python -m compileall -q app src tests`
- [ ] `pytest`
- [ ] Manual test or screenshot if dashboard/report changed

## Integration Notes
- What output does another team need from this work?
- Does this connect to `src/autoanalyst/pipeline.py`?

## Blockers
- None, or list blockers clearly.
```

## Common Mistakes to Avoid

- Do not push directly to `main`.
- Do not open PRs into `main`; target `develop`.
- Do not commit secrets, API keys, private datasets, or local machine paths.
- Do not make huge mixed commits that combine unrelated work.
- Do not duplicate central pipeline logic in dashboard or reports.
- Do not leave placeholder names in final team-facing documentation.
- Do not ignore tests or manual validation notes.
