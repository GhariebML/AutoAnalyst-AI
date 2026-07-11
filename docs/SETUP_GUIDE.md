# Setup Guide

## Requirements

- Python 3.12 or newer
- Node.js 20 or newer
- npm
- Git
- Optional: OpenAI, OpenRouter, or Hugging Face provider credentials

## Backend Installation

```powershell
git clone https://github.com/GhariebML/ADPilot.git
cd ADPilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Frontend Installation

```powershell
cd frontend
npm install
```

## Environment Variables

Copy the safe example file:

```powershell
Copy-Item .env.example .env
```

Required variables depend on the selected provider:

```env
LLM_PROVIDER=openrouter
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
HF_TOKEN=
HF_MODEL=deepseek-ai/DeepSeek-R1
HF_BASE_URL=https://router.huggingface.co/v1
TEMPERATURE=0.2
ENVIRONMENT=development
```

Do not commit `.env`.

## Run Backend Locally

```powershell
$env:PYTHONPATH="src"
python -m uvicorn adpilot.api.main:app --host 127.0.0.1 --port 8000
```

Backend URLs:

- Health: `http://127.0.0.1:8000/healthz`
- API docs: `http://127.0.0.1:8000/docs`

## Run Frontend Locally

```powershell
cd frontend
npm run dev -- --host 127.0.0.1
```

Frontend URL:

- `http://127.0.0.1:3000/` or the port printed by Vite

## Run Phase 1 Pipeline

```powershell
$env:LLM_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="<your-openrouter-key>"
python scripts/run_phase1_pipeline.py
```

For Hugging Face:

```powershell
$env:LLM_PROVIDER="huggingface"
$env:HF_TOKEN="<your-huggingface-token>"
$env:HF_MODEL="deepseek-ai/DeepSeek-R1"
python scripts/run_phase1_pipeline.py
```

## Run Tests and Checks

```powershell
ruff check .
pytest -q
cd frontend
npm run build
```

## Troubleshooting

- `ModuleNotFoundError: adpilot`: set `PYTHONPATH=src` or run scripts from the repository root.
- Missing provider key: set the key required by `LLM_PROVIDER`.
- Dashboard does not call real LLMs: set `ADPILOT_DASHBOARD_USE_REAL_LLM=true`.
- Structured output failures: try a stronger model or OpenAI for stricter schema adherence.
- Vite port differs: use the local URL printed by `npm run dev`.

