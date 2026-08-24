"""Master Dynamic Orchestrator for AutoAnalyst AI."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

import pandas as pd

from autoanalyst.agents.base import AgentResult
from autoanalyst.agents.eda_agent import EDAAgent
from autoanalyst.agents.evaluation_agent import EvaluationAgent
from autoanalyst.agents.ml_agent import MachineLearningAgent
from autoanalyst.agents.preprocessing_agent import PreprocessingAgent
from autoanalyst.agents.profiling_agent import DataProfilingAgent
from autoanalyst.agents.registry import GLOBAL_AGENT_REGISTRY, AgentRegistry
from autoanalyst.agents.reporting_agent import ReportingAgent
from autoanalyst.data_loading.loader import load_dataset

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorEvent:
    """Event emitted during multi-agent execution for real-time telemetry."""

    event_type: str  # "RUN_STARTED", "AGENT_STARTED", "TOOL_EXECUTED", "AGENT_COMPLETED", "HITL_PAUSED", "RUN_COMPLETED", "RUN_FAILED"
    run_id: str
    agent_name: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AnalysisPlan:
    """Dynamic plan determined by the Orchestrator."""

    run_id: str
    steps_planned: list[str]
    current_step_index: int = 0
    is_complete: bool = False
    hitl_paused_step: str | None = None
    approval_prompt: str | None = None


class MasterOrchestrator:
    """Intelligent Master Orchestrator coordinating dynamic multi-agent workflows."""

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        max_steps: int = 15,
        event_callback: Callable[[OrchestratorEvent], None] | None = None,
        llm_service: Any | None = None,
    ) -> None:
        self.registry = registry or GLOBAL_AGENT_REGISTRY
        self.max_steps = max_steps
        self.event_callback = event_callback
        if llm_service is not None:
            self.llm = llm_service
        else:
            from autoanalyst.llm.service import GLOBAL_LLM_SERVICE
            self.llm = GLOBAL_LLM_SERVICE
        self._ensure_default_agents()

    def _ensure_default_agents(self) -> None:
        """Register the default specialized agents if not already present."""
        if not self.registry.get("profiling_agent"):
            self.registry.register(DataProfilingAgent(llm_service=self.llm))
        if not self.registry.get("eda_agent"):
            self.registry.register(EDAAgent(llm_service=self.llm))
        if not self.registry.get("preprocessing_agent"):
            self.registry.register(PreprocessingAgent(llm_service=self.llm))
        if not self.registry.get("ml_agent"):
            self.registry.register(MachineLearningAgent(llm_service=self.llm))
        if not self.registry.get("evaluation_agent"):
            self.registry.register(EvaluationAgent(llm_service=self.llm))
        if not self.registry.get("reporting_agent"):
            self.registry.register(ReportingAgent(llm_service=self.llm))

    def _emit(
        self, event_type: str, run_id: str, agent_name: str | None = None, data: dict[str, Any] | None = None
    ) -> None:
        event = OrchestratorEvent(
            event_type=event_type,
            run_id=run_id,
            agent_name=agent_name,
            data=data or {},
        )
        logger.info("Orchestrator Event: [%s] run=%s agent=%s", event_type, run_id, agent_name)
        if self.event_callback:
            try:
                self.event_callback(event)
            except Exception as exc:
                logger.warning("Event callback error: %s", exc)

    def run_analysis(
        self,
        dataset: str | pd.DataFrame,
        target_column: str | None = None,
        model_task: str = "auto",
        missing_strategy: str = "median",
        require_approval: bool = False,
        approvals: dict[str, bool] | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute autonomous multi-agent analysis with dynamic planning and recovery."""
        run_id = run_id or f"run_{uuid.uuid4().hex[:10]}"
        start_time = time.perf_counter()

        self._emit("RUN_STARTED", run_id, data={"target_column": target_column, "model_task": model_task})

        # Initialize State
        raw_df = load_dataset(dataset) if isinstance(dataset, str) else dataset.copy()
        state: dict[str, Any] = {
            "run_id": run_id,
            "raw_df": raw_df,
            "target_column": target_column,
            "model_task": model_task,
            "missing_strategy": missing_strategy,
            "require_approval": require_approval,
            "approvals": approvals or {},
            "all_findings": [],
            "agent_history": [],
            "warnings": [],
        }

        current_agent_name = "profiling_agent"
        step_count = 0

        while current_agent_name and step_count < self.max_steps:
            step_count += 1
            agent = self.registry.get(current_agent_name)
            if not agent:
                logger.warning("Agent '%s' not registered in registry. Terminating workflow.", current_agent_name)
                break

            self._emit("AGENT_STARTED", run_id, agent_name=current_agent_name)

            result: AgentResult = agent.run(state)
            state["agent_history"].append(result)

            # Accumulate findings & merge artifacts
            if result.findings:
                state["all_findings"].extend(result.findings)
            for k, v in result.artifacts.items():
                state[k] = v

            actions_data = [
                a.model_dump() if hasattr(a, "model_dump") else (a.dict() if hasattr(a, "dict") else dict(a))
                for a in result.actions_taken
            ]
            findings_data = [
                f.model_dump() if hasattr(f, "model_dump") else (f.dict() if hasattr(f, "dict") else dict(f))
                for f in result.findings
            ]
            self._emit(
                "AGENT_COMPLETED",
                run_id,
                agent_name=current_agent_name,
                data={
                    "status": result.status,
                    "findings_count": len(result.findings),
                    "tools_used": result.tools_used,
                    "duration_ms": result.duration_ms,
                    "actions_taken": actions_data,
                    "findings": findings_data,
                    "recommendations": result.recommendations,
                },
            )

            # Check if paused for human approval
            if result.status == "paused_for_approval":
                self._emit(
                    "HITL_PAUSED",
                    run_id,
                    agent_name=current_agent_name,
                    data={"prompt": result.human_prompt, "step": current_agent_name},
                )
                return {
                    "run_id": run_id,
                    "status": "paused_for_approval",
                    "paused_step": current_agent_name,
                    "human_prompt": result.human_prompt,
                    "state": state,
                    "agent_history": state["agent_history"],
                }

            # Decide Next Step
            if result.next_action:
                decision = result.next_action.decision
                if decision == "WORKFLOW_COMPLETE":
                    current_agent_name = None
                elif decision == "TRIGGER_EDA":
                    current_agent_name = "eda_agent"
                elif decision == "TRIGGER_PREPROCESSING" or decision == "TRIGGER_PREPROCESSING_OR_ML":
                    current_agent_name = "preprocessing_agent"
                elif decision == "TRIGGER_MODELING":
                    current_agent_name = "ml_agent"
                elif decision == "TRIGGER_EVALUATION":
                    current_agent_name = "evaluation_agent"
                elif decision == "TRIGGER_REPORTING" or decision == "COMPLETE_EXPLORATION":
                    current_agent_name = "reporting_agent"
                else:
                    current_agent_name = result.next_action.recommended_agent
            else:
                current_agent_name = None

        duration_total = round((time.perf_counter() - start_time) * 1000.0, 2)
        self._emit("RUN_COMPLETED", run_id, data={"duration_total_ms": duration_total, "steps_executed": step_count})

        return {
            "run_id": run_id,
            "status": "completed",
            "duration_ms": duration_total,
            "state": state,
            "profile": state.get("profile"),
            "eda_results": {
                "correlation_matrix": state.get("correlation_matrix"),
                "distributions": state.get("distributions"),
                "outliers_summary": state.get("outliers_summary"),
            },
            "cleaned_df": state.get("cleaned_df"),
            "model_results": state.get("model_results"),
            "evaluation_results": state.get("evaluation_results"),
            "all_findings": state.get("all_findings"),
            "insights": state.get("insights", []),
            "executive_summary": state.get("executive_summary"),
            "report_path": state.get("report_path"),
            "agent_history": state["agent_history"],
        }
