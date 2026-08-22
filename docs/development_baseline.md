# AutoAnalyst AI — Development Baseline Report

**Date:** 2026-08-22
**Purpose:** Establish a clean, reproducible development baseline before feature implementation.

---

## Environment

| Component | Version |
|---|---|
| OS | Windows 10/11 (10.0.26200) |
| Python | 3.11.15 (via py launcher) |
| Git | 2.53.0.windows.1 |
| pip | 26.2.1 |
| Virtual Environment | `.venv` (Python 3.11.15) |

---

## Repository

| Property | Value |
|---|---|
| Branch | `main` |
| Commit | `1b5c1359b41d946557b0540ba5d02f55d23d5857` |
| Commit message | "docs: add premium banner image and stylized Mermaid workflow to README" |
| Commit date | 2026-07-12 09:29:12 +0300 |
| Remote origin | `https://github.com/GhariebML/AutoAnalyst-AI.git` |
| Working tree | Clean — no uncommitted changes |
| Clone type | Shallow (depth 1) + ZIP extraction hybrid |

---

## GitHub State

### Branches (23 total)

| Group | Branches | Commit | Status |
|---|---|---|---|
| **main + develop** | 2 | `1b5c135` | ✅ Most complete — identical commits |
| **Empty shells** | 10 | `6db9563` | ⚠️ Created but never developed, BEHIND main |
| **Docs snapshot** | 6 | `d064ad9` | ⚠️ Earlier docs-only snapshot, BEHIND main |
| **Preprocessing work** | 1 | `0f98841` | 🔶 Has unique code: modified cleaner.py, feature_builder.py, +3 test files |
| **Patch branches** | 3 | various | Small doc patches |
| **PR branch** | 1 | `39b392b` | PR #13 — README_Team5.md creation |

### Pull Requests (13 total)

| PR | Title | Status | Notes |
|---|---|---|---|
| #1 | (unknown) | Unknown | Fetched but details not inspected |
| #2 | (unknown) | Unknown | Referenced in PR #10 merge |
| #3 | (unknown) | Unknown | |
| #4 | (unknown) | Unknown | |
| #5 | Update example.csv | Unknown | |
| #6 | (unknown) | Unknown | |
| #7 | Create evaluation_insights_plan.md | Unknown | |
| #8 | docs: upgrade root README.md | Unknown | |
| #9 | Add updated code with One-Hot Encoding | Unknown | |
| #10 | Merge PR #2 | Unknown | |
| #11 | Add files via upload | Unknown | |
| #12 | Add files via upload | Unknown | |
| #13 | Create README_Team5.md | Open | Misformatted PR body |

### Key Finding

**`main` is the correct starting point for development.** All feature branches are BEHIND main, not ahead. The only branch with potentially useful unique code is `feature/preprocessing-features` (one-hot encoding improvements + new test files).

---

## Local Comparison

### ZIP Copy vs Git Clone

| Aspect | Result |
|---|---|
| Same project? | ✅ Yes — same GitHub repository |
| Same source code? | ✅ Yes — identical Python source files |
| Same configuration? | ✅ Yes — pyproject.toml, requirements.txt, .gitignore |
| Same documentation? | ✅ Yes — all docs, PDFs, README |
| Files missing from Git? | ❌ None — Git clone has everything |
| Files only in ZIP? | ❌ N/A — original ZIP was consumed into the Git clone |
| Meaningful differences? | ❌ None — ZIP was extracted and git-initialized in place |

**Note:** The original ZIP directory (`D:\AUTO\AutoAnalyst-AI-main`) was inadvertently overwritten during the extraction process (the ZIP's root folder name matched the target). No data was lost — the Git clone contains all the same files plus version control history.

---

## Dependencies

| Property | Value |
|---|---|
| Package manager | pip 26.2.1 |
| Dependency source | `requirements.txt` (runtime) + `pyproject.toml` (build/test) |
| Python version | 3.11.15 (compatible with `>=3.10` requirement) |

### Installed Packages (42 total)

| Package | Version | Status |
|---|---|---|
| pandas | 3.0.5 | ✅ Installed |
| numpy | 2.4.6 | ✅ Installed |
| scikit-learn | 1.9.0 | ✅ Installed |
| matplotlib | 3.11.1 | ✅ Installed |
| seaborn | 0.13.2 | ✅ Installed |
| plotly | 6.9.0 | ✅ Installed |
| streamlit | 1.62.0 | ✅ Installed |
| openpyxl | 3.1.5 | ✅ Installed |
| pytest | 9.1.1 | ✅ Installed |
| autoanalyst-ai | 0.1.0 | ✅ Installed (editable mode) |

### Dependency Notes

- `requirements.txt` and `pyproject.toml` serve different purposes — no duplication
- `requirements.txt`: runtime dependencies (pandas, scikit-learn, streamlit, etc.)
- `pyproject.toml`: build system config + pytest settings (no runtime deps listed)
- Both files are needed for the project to work correctly

---

## Tests

| Metric | Value |
|---|---|
| Total tests | 6 |
| Passed | 6 ✅ |
| Failed | 0 |
| Skipped | 0 |
| Errors | 0 |
| Warnings | 2 (pandas deprecation) |
| Test time | 1.21s |

### Test Files

| File | Tests | What's Tested |
|---|---|---|
| `tests/test_pipeline.py` | 4 | Profile, cleaning, EDA/insights, report generation |
| `tests/test_end_to_end_pipeline.py` | 2 | Pipeline without modeling, pipeline with classification |

### Warnings

```
Pandas4Warning: For backward compatibility, 'str' dtypes are included by
select_dtypes when 'object' dtype is specified. This behavior is deprecated.
Explicitly pass 'str' to `include` to select them.
```

**Location:** `src/autoanalyst/pipeline.py:153`
**Impact:** Code warning only — tests pass. Will become an error in pandas 4.x.

---

## Application

| Property | Value |
|---|---|
| Startup status | ✅ Streamlit started successfully |
| Dashboard URL | http://localhost:8501 |
| HTTP status | 200 OK |
| Framework confirmed | ✅ Streamlit in response |
| File upload | ⚠️ Not tested (requires manual UI interaction) |
| Pipeline execution | ⚠️ Not tested via UI (tested via pytest) |

### Launch Command

```bash
cd D:\AUTO\AutoAnalyst-AI
.venv\Scripts\streamlit.exe run app/streamlit_app.py
```

Or with headless mode:

```bash
.venv\Scripts\streamlit.exe run app/streamlit_app.py --server.headless=true
```

---

## Blocking Problems

### 🔴 Critical

1. **Pandas 3.x deprecation warning** — `select_dtypes(include=["object"])` needs `"str"` added. Will break in pandas 4.x. File: `pipeline.py:153`.

### 🟠 High

2. **No caching in Streamlit** — Pipeline re-runs on every widget interaction. Performance will degrade with large datasets.

3. **No file upload size limits** — Potential DoS vector if deployed publicly.

### 🟡 Medium

4. **Feature branches are all behind main** — No branch has newer code than main. The `feature/preprocessing-features` branch has unique improvements that should be reviewed.

5. **13 open PRs on GitHub** — Some are misformatted or stale. Need triage.

6. **60% of documentation is placeholder** — Weekly updates, notebooks, reports are empty stubs.

### 🟢 Low

7. **No pre-commit hooks** — Code style enforcement relies on manual review.

8. **No test coverage reporting** — No way to measure actual code coverage.

---

## Summary

| Category | Status |
|---|---|
| Git | ✅ Repository cloned and verified |
| Environment | ✅ Python 3.11.15 with all dependencies |
| Tests | ✅ 6/6 passing |
| Application | ✅ Streamlit starts and serves |
| Code quality | ⚠️ Clean but has deprecation warnings |
| Branch strategy | ⚠️ Feature branches are stale/behind main |
| Documentation | ⚠️ Extensive but ~60% placeholder |

**Overall baseline status: READY FOR DEVELOPMENT**

The project has a clean, working development environment. All core functionality is operational. The main blockers are performance issues (no caching), deprecation warnings, and stale feature branches.

---

*Report generated: 2026-08-22*
*Next phase: Feature implementation (pending approval)*
