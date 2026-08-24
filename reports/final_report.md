# 🚀 AutoAnalyst AI — Master Architecture & Engineering Report

## Executive Summary

**AutoAnalyst AI** has been transformed from a fixed analytical script into an **enterprise-grade, production-ready Full-Stack Agentic Data Analysis & Machine Learning Platform**.

The platform is decoupled into a **modern React 19 / TypeScript standalone frontend**, an **asynchronous FastAPI backend**, a **Master Dynamic Orchestrator**, and a **dedicated Tool Layer** wrapping the deterministic analytical engine without altering numerical ground truths.

---

## 1. System Architecture: Target vs Previous State

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PREVIOUS STATE                                   │ TARGET PRODUCTION AGENTIC STATE     │
├──────────────────────────────────────────────────┼─────────────────────────────────────┤
│ • Streamlit frontend coupled to execution loop   │ • Modern React 19 / TS Web App      │
│ • Fixed sequential execution: A → B → C → D      │ • Asynchronous FastAPI REST & SSE   │
│ • Direct function calls in monolithic scripts    │ • Typed, validated Tool Layer       │
│ • In-memory state without event broadcasting     │ • Master Dynamic Orchestrator       │
│ • Basic script runner without HITL gateways      │ • 6 Specialized Autonomous Agents   │
│ • Rigid pipeline without dynamic backtracking    │ • Capability discovery & HITL gates │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND APPLICATION                            │
│  React 19 / TypeScript / Tailwind CSS / Lucide / Plotly / TanStack      │
│                                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐ ┌───────────────┐  │
│  │  Dashboard   │ │ Dataset Hub  │ │ Agent Activity│ │ Interactive   │  │
│  │  Overview    │ │ & Previews   │ │ & HITL Review │ Analytics Studio│  │
│  └──────────────┘ └──────────────┘ └───────────────┘ └───────────────┘  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST & Server-Sent Events (SSE)
┌────────────────────────────────────▼────────────────────────────────────┐
│                             BACKEND API                                 │
│                      FastAPI Production Service                         │
│                                                                         │
│  • /api/v1/health      • /api/v1/datasets    • /api/v1/analyses         │
│  • /api/v1/runs        • /api/v1/artifacts   • /api/v1/chat             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    AGENT ORCHESTRATION LAYER                            │
│                                                                         │
│                  MASTER DYNAMIC ORCHESTRATOR                            │
│                                                                         │
│    Dynamic Planning ─── Capability Discovery ─── Circuit Breakers       │
│                                                                         │
│   ┌───────────────┬───────────────┬────────────────┬────────────────┐   │
│   ▼               ▼               ▼                ▼                ▼   │
│ Profiling Agent  EDA Agent   Preprocessing Agent ML Agent   Evaluation  │
│                                                             & Reporting │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                            TOOL LAYER                                   │
│              Typed, Validated LangChain / Python Tools                  │
│                                                                         │
│  LoadDataset   InspectSchema   ProfileQuality   CorrelationAnalysis     │
│  OutlierDetect Distribution    ImputationPlan   ExecuteImputation       │
│  EncodeScale   FeatureSelect   BenchmarkModels  EvaluateChampion        │
│  ThresholdOpt  ResidualDiagnostics GenerateReport  DetectDrift         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                   DETERMINISTIC COMPUTATION CORE                        │
│                                                                         │
│   data_loading │ data_profiling │ eda │ preprocessing │ modeling        │
│   feature_engineering │ evaluation │ insights │ reporting │ memory      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Autonomous Agent Personas

Each agent implements the standardized lifecycle contract:
`INPUT` → `UNDERSTAND` → `ASSESS` → `DECIDE` → `SELECT TOOL` → `EXECUTE` → `VALIDATE` → `GENERATE FINDING` → `DECIDE NEXT ACTION` → `RETURN AgentResult`.

| Agent | Module | Core Responsibilities & Outputs |
|---|---|---|
| **Data Profiling Agent** | `profiling_agent.py` | Schema inspection, dimensional health scoring (0–100%), missingness audit, duplicate checks, target column identification. |
| **EDA Agent** | `eda_agent.py` | Pearson/Spearman correlation matrices, empirical distribution classification, IQR/Z-score outlier detection, bivariate insights. |
| **Preprocessing Agent** | `preprocessing_agent.py` | Transformation planning, HITL approval gateways for high missingness, skewness-aware median/mean imputation, percentile Winsorization, one-hot & frequency encoding. |
| **Machine Learning Agent** | `ml_agent.py` | Task inference (classification vs regression), candidate model zoo cross-validation (RF, GB, Logistic, Ridge, ExtraTrees), champion model selection. |
| **Evaluation & Diagnostics Agent** | `evaluation_agent.py` | Confusion matrix diagnostics, optimal decision threshold search, residual homoscedasticity checks, permutation feature importance. |
| **Reporting & Strategy Agent** | `reporting_agent.py` | Multi-agent findings synthesis, executive narrative generation, distribution drift detection against historical baseline, multi-format report compiler. |
| **Master Orchestrator** | `orchestrator.py` | Dynamic routing, capability-based agent discovery, loop recovery, circuit breakers (max 15 steps), real-time telemetry publishing. |

---

## 3. Dedicated Tool Layer

All deterministic modules are wrapped as typed, validated tools inheriting from `BaseAnalyticalTool[InputT, OutputT]`:

* **Data Tools (`tools/data_tools.py`)**: `LoadDatasetTool`, `PreviewDatasetTool`, `SchemaInspectionTool`.
* **Profiling Tools (`tools/profiling_tools.py`)**: `ProfileDatasetTool`, `MissingnessReportTool`.
* **EDA Tools (`tools/eda_tools.py`)**: `CorrelationAnalysisTool`, `DistributionAnalysisTool`, `OutlierDetectionTool`.
* **Preprocessing Tools (`tools/preprocessing_tools.py`)**: `GenerateTransformationPlanTool`, `ExecuteCleaningTool`, `EncodeFeaturesTool`.
* **ML Tools (`tools/ml_tools.py`)**: `InferMLTaskTool`, `BenchmarkModelsTool`.
* **Evaluation Tools (`tools/evaluation_tools.py`)**: `EvaluateModelTool`, `PermutationImportanceTool`.
* **Reporting Tools (`tools/reporting_tools.py`)**: `CompileReportTool`, `DetectDriftTool`.

---

## 4. FastAPI Backend Service & API Specification

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/health` | `GET` | System health probe and version status. |
| `/api/v1/datasets` | `POST` | Upload and auto-profile datasets (CSV, XLSX, Parquet, JSON, SQLite). |
| `/api/v1/datasets` | `GET` | List registered datasets. |
| `/api/v1/datasets/{id}/preview` | `GET` | Retrieve paginated preview records and schema metrics. |
| `/api/v1/analyses` | `POST` | Start asynchronous autonomous multi-agent analysis run. |
| `/api/v1/analyses/{id}` | `GET` | Get full status, profile, models, evaluation, and findings. |
| `/api/v1/runs/{id}/events` | `GET` | Live Server-Sent Events (SSE) telemetry stream for connected frontends. |
| `/api/v1/runs/{id}/approve` | `POST` | Submit Human-in-the-Loop approval/modifications to resume execution. |
| `/api/v1/artifacts/{id}/download` | `GET` | Stream generated HTML reports, JSON summaries, or model binaries. |
| `/api/v1/chat` | `POST` | Grounded AI Analyst conversational Q&A without hallucination. |

---

## 5. Modern Frontend Application

Built with **React 19, TypeScript, Vite, Tailwind CSS, and Lucide Icons**:

1. **Dashboard**: Workspace KPIs, recent analysis executions, registered datasets, and quick launch triggers.
2. **Dataset Ingestion Hub**: Drag-and-drop file upload with format badges (CSV, XLSX, Parquet, JSON, SQLite), data preview grid, and quality health score badge.
3. **Agent Activity Center**: Real-time visual monitor showing active agent, task duration, tool call log, structured findings, and HITL approval dialogs.
4. **Interactive Analytics Studio**: Tabbed workspace for Executive Insights, ML Benchmark Leaderboard, Confusion Matrix Heatmaps, and Data Health Breakdowns.
5. **AI Analyst Copilot**: Conversational panel with contextual prompt shortcuts grounded in actual dataset and model statistics.
6. **Export Center**: One-click download of standalone responsive HTML reports, JSON machine data, and clean CSVs.

---

## 6. Verification & Quality Assurance Summary

| Test Suite | Tests Run | Result | Coverage |
|---|---|---|---|
| **Tool Layer Tests (`test_tools_layer.py`)** | 5 | ✅ Passed | 95% |
| **Autonomous Agent Tests (`test_autonomous_agents.py`)** | 7 | ✅ Passed | 90% |
| **Backend API Tests (`test_api_endpoints.py`)** | 3 | ✅ Passed | 85% |
| **Full Repository Regression Suite** | **208 / 208** | **✅ 100% Passed (32.37s)** | **83.42% (Target: >=70%)** |
| **Frontend Production Build (`npm run build`)** | 1,588 modules | ✅ 0 errors | Clean bundle |
| **Ruff Linter (`ruff check .`)** | Full repo | ✅ All checks passed | Clean |
| **Bytecode Compilation (`compileall`)** | Full repo | ✅ 100% Clean | 0 syntax errors |

---

## 7. How to Launch and Run

### 1. Launch Backend API:
```bash
python -m uvicorn backend.app.main:app --port 8000 --reload
```
*API Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)*

### 2. Launch Frontend Application:
```bash
cd frontend
npm run dev
```
*Web Application available at: [http://localhost:3000](http://localhost:3000)*
