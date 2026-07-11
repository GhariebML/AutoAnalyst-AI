# Changelog

## 2026-05-19

### Added

- LangChain structured-output support through the shared `BaseAgent` pattern.
- Implemented Research, Content, Analytics, Design, and Campaign Manager agents.
- Multi-provider LLM support for OpenAI, OpenRouter, and Hugging Face Inference Providers.
- Phase 1 runner scripts for individual agents and the full pipeline.
- Dashboard-compatible FastAPI endpoints for campaign submission, task polling, and local result display.
- Tests for provider selection, missing provider keys, structured-output patterns, and agent behavior.
- Professional project documentation in `docs/`.

### Changed

- Updated configuration to use `pydantic-settings` and `.env` loading.
- Updated `.env.example` for OpenAI, OpenRouter, Hugging Face, temperature, and environment settings.
- Updated README for GitHub-ready setup, usage, provider configuration, and contribution guidance.
- Improved `.gitignore` coverage for local files, caches, logs, environments, and build output.

### Fixed

- Fixed direct script execution from the repository root.
- Fixed the local dashboard workflow by aligning frontend API calls with backend routes.
- Prevented local dashboard previews from hanging on real LLM calls by using demo output unless explicitly enabled.

### Security

- Confirmed no real `.env` file is present.
- Kept secrets out of tracked files.
- Added safer ignore rules for local environment files, logs, caches, and build outputs.

### Documentation

- Added `PROJECT_OVERVIEW.md`, `UPDATE_REPORT.md`, `SETUP_GUIDE.md`, `GITHUB_WORKFLOW.md`, and `CHANGELOG.md`.
- Documented local setup, provider selection, test commands, GitHub workflow, and security notes.

