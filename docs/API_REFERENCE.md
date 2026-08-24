# AutoAnalyst AI — REST API & SSE Reference

---

## 1. Overview

The AutoAnalyst AI backend exposes a REST API powered by **FastAPI 0.115** and **Server-Sent Events (SSE)** for real-time multi-agent execution streaming.

- **Base URL**: `http://localhost:8000/api/v1`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **OpenAPI Schema JSON**: `http://localhost:8000/openapi.json`

---

## 2. API Endpoints

### 📊 Dashboard & Telemetry

#### `GET /api/v1/dashboard/summary`
Returns aggregate platform KPI statistics across all runs, datasets, and models.

**Response Schema (`200 OK`)**:
```json
{
  "total_runs": 12,
  "completed_runs": 10,
  "running_runs": 1,
  "failed_runs": 1,
  "total_datasets": 5,
  "total_insights": 48,
  "total_models_trained": 10,
  "avg_quality_score": 98.4,
  "avg_duration_ms": 3840.0,
  "champion_models": ["RandomForestRegressor", "GradientBoostingClassifier"]
}
```

#### `GET /api/v1/dashboard/runs-timeline`
Returns time-series aggregated analysis runs by day.

**Query Parameters**:
- `days` (integer, optional, default: `7`, min: `1`, max: `90`): Number of historical days to retrieve.

**Response Schema (`200 OK`)**:
```json
[
  {
    "date": "2026-08-24",
    "completed": 6,
    "running": 0,
    "failed": 0,
    "total": 6
  }
]
```

#### `GET /api/v1/dashboard/agents-activity`
Returns execution frequency, success rates, average duration, and tools used per agent.

**Response Schema (`200 OK`)**:
```json
[
  {
    "agent_name": "ml_agent",
    "display_name": "Machine Learning Agent",
    "category": "Predictive Modeling",
    "total_executions": 10,
    "success_rate_pct": 100.0,
    "avg_duration_ms": 1850.0,
    "tools_used": ["infer_ml_task", "benchmark_models", "train_champion"]
  }
]
```

---

### 🩺 System Diagnostics & Tool Catalog

#### `GET /api/v1/system/health`
Returns deep multi-subsystem operational health report.

**Response Schema (`200 OK`)**:
```json
{
  "status": "healthy",
  "app_version": "1.0.0",
  "subsystems": [
    {
      "name": "Database (SQLite)",
      "status": "operational",
      "latency_ms": 0.45,
      "details": "SQLite database initialized and read/write verified."
    },
    {
      "name": "LLM Gateway (OpenRouter)",
      "status": "operational",
      "latency_ms": 520.0,
      "details": "Model: openai/gpt-4o-mini • Fallback: anthropic/claude-3.5-haiku"
    }
  ],
  "llm_gateway": {
    "provider": "openrouter",
    "status": "healthy",
    "model": "openai/gpt-4o-mini",
    "total_requests": 14
  },
  "timestamp": "2026-08-24T14:20:00Z"
}
```

#### `GET /api/v1/system/tools`
Returns the complete registry catalog of all 15 deterministic analytical tools.

---

### 🗄️ Dataset Management

#### `POST /api/v1/datasets`
Uploads and profiles a tabular dataset file (`multipart/form-data`).

**Request**:
- `file`: Multipart file (`.csv`, `.parquet`, `.xlsx`, `.xls`).

**Response Schema (`201 Created`)**:
```json
{
  "id": "ds_6df19801dad3",
  "filename": "sales_records.csv",
  "file_size_bytes": 1048576,
  "file_format": "csv",
  "rows": 8800,
  "columns": 14,
  "health_score": 99.2,
  "created_at": "2026-08-24T14:00:00Z"
}
```

#### `GET /api/v1/datasets/{id}/preview`
Retrieves column data types, column profiles, missingness, and the first 25 preview records.

---

### 🤖 Multi-Agent Analysis Runs

#### `POST /api/v1/analyses`
Launches an autonomous multi-agent analysis run.

**Request Body**:
```json
{
  "dataset_id": "ds_6df19801dad3",
  "target_column": "sales_amount",
  "model_task": "auto",
  "require_approval": false
}
```

#### `GET /api/v1/runs/{id}/events`
**Server-Sent Events (SSE)** real-time stream. Emits life-cycle events as agents execute tools and make decisions.

**Event Payloads**:
```json
{
  "type": "AGENT_STARTED",
  "run_id": "anl_d41d887348b8",
  "agent_name": "profiling_agent",
  "timestamp": "2026-08-24T14:05:01Z"
}
```

```json
{
  "type": "AGENT_COMPLETED",
  "run_id": "anl_d41d887348b8",
  "agent_name": "ml_agent",
  "data": {
    "duration_ms": 1420,
    "actions_taken": [
      {
        "tool": "benchmark_models",
        "status": "ok",
        "duration_ms": 1380,
        "summary": "Trained 4 candidate models. Champion: RandomForestRegressor (R2: 0.942)"
      }
    ],
    "findings": [
      {
        "category": "Model Performance",
        "fact": "RandomForestRegressor achieved top cross-validation R2 of 0.942.",
        "evidence": "5-fold stratified cross validation score across 8,800 rows.",
        "interpretation": "Ensemble decision trees captured non-linear feature interactions.",
        "confidence": 0.98
      }
    ]
  }
}
```

#### `POST /api/v1/runs/{id}/approve`
Approves or modifies a paused Human-In-The-Loop (HITL) cleaning and modeling plan.

---

### 📑 Artifacts & Exports

#### `GET /api/v1/artifacts/{id}/download?format={html|json|csv}`
Downloads compiled analysis outputs:
- `format=html`: Interactive Cyber Dark HTML report with Chart.js charts.
- `format=json`: Machine-readable structured analytical artifact.
- `format=csv`: Cleaned and imputed tabular dataset.

---

### 💬 Grounded AI Analyst Copilot

#### `POST /api/v1/chat`
Answers questions against the active analysis run state with factual grounding.

**Request Body**:
```json
{
  "analysis_id": "anl_d41d887348b8",
  "query": "Which features had the highest permutation importance for sales predictions?"
}
```
