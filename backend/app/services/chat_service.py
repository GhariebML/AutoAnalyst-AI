"""Service layer for AI conversational data intelligence assistant with OpenRouter LLM support."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from autoanalyst.llm.context import ContextBuilder
from autoanalyst.llm.prompts.agents import CHAT_SYSTEM_PROMPT
from autoanalyst.llm.service import GLOBAL_LLM_SERVICE
from autoanalyst.llm.types import TaskCategory
from backend.app.models.database import AnalysisRunModel, ChatMessageModel
from backend.app.schemas.chat import ChatResponse

logger = logging.getLogger(__name__)


class ChatLLMOutput(BaseModel):
    """Structured LLM output schema for AI Analyst chat responses."""

    response: str = Field(description="Comprehensive, markdown-formatted grounded response")
    suggested_followups: list[str] = Field(default_factory=list, description="3 relevant follow-up questions")


class ChatService:
    """Handles grounded Q&A responses grounded in analysis state without hallucinations."""

    @staticmethod
    def answer_query(analysis_id: str, query: str, db: Session) -> ChatResponse:
        run = db.query(AnalysisRunModel).filter(AnalysisRunModel.id == analysis_id).first()
        if not run:
            return ChatResponse(
                analysis_id=analysis_id,
                query=query,
                response="Analysis not found. Please verify the analysis run ID.",
            )

        profile = json.loads(run.profile_json) if run.profile_json else {}
        insights = json.loads(run.insights_json) if run.insights_json else []
        findings = json.loads(run.findings_json) if getattr(run, "findings_json", None) else []
        model_results = json.loads(run.model_results_json) if getattr(run, "model_results_json", None) else {}
        evaluation = json.loads(run.evaluation_json) if run.evaluation_json else {}

        resp_text: str | None = None
        followups: list[str] = [
            "What were the most important features driving predictions?",
            "How does the champion model compare against other candidates?",
            "What data quality risks should I address?",
        ]
        source = "deterministic"

        # 1. Attempt OpenRouter LLM Grounded Response
        if GLOBAL_LLM_SERVICE.is_available:
            try:
                state_summary: dict[str, Any] = {
                    "dataset_id": run.dataset_id,
                    "target_column": run.target_column,
                    "model_task": run.model_task,
                    "champion_model_name": run.champion_model_name,
                    "champion_score": run.champion_score,
                    "status": run.status,
                    "rows": profile.get("rows"),
                    "columns": profile.get("columns"),
                    "health_score": profile.get("health_score"),
                }
                tool_results: dict[str, Any] = {
                    "data_profile": profile,
                    "model_zoo": model_results,
                    "holdout_evaluation": evaluation,
                    "executive_summary": run.executive_summary or "",
                }
                messages = ContextBuilder.build_agent_context(
                    system_instruction=CHAT_SYSTEM_PROMPT,
                    task_objective="Answer the user's specific dataset or modeling query using the factual analysis state.",
                    state_summary=state_summary,
                    tool_results=tool_results,
                    recent_findings=findings or insights,
                    user_prompt=query,
                )

                llm_res = GLOBAL_LLM_SERVICE.generate(
                    task=TaskCategory.CHAT,
                    messages=messages,
                    response_model=ChatLLMOutput,
                    run_id=analysis_id,
                    agent_name="ai_analyst_copilot",
                )
                if llm_res.parsed and isinstance(llm_res.parsed, ChatLLMOutput):
                    resp_text = llm_res.parsed.response
                    if llm_res.parsed.suggested_followups:
                        followups = llm_res.parsed.suggested_followups[:3]
                    source = f"openrouter ({llm_res.model})"
                else:
                    resp_text = llm_res.content
                    source = f"openrouter ({llm_res.model})"
            except Exception as exc:
                logger.warning("LLM chat formulation failed, falling back to deterministic: %s", exc)

        # 2. Deterministic Rule-Based Fallback
        if not resp_text:
            q_lower = query.lower()
            if "model" in q_lower or "champion" in q_lower:
                if run.champion_model_name:
                    resp_text = (
                        f"The champion model selected during cross-validation benchmark is **{run.champion_model_name}**. "
                    )
                    if "accuracy" in evaluation:
                        resp_text += f"It achieved **{evaluation['accuracy'] * 100:.1f}% accuracy** and **Macro F1 of {evaluation.get('f1_macro', 0):.3f}** on holdout validation data."
                    elif "rmse" in evaluation:
                        resp_text += f"It achieved **RMSE of {evaluation['rmse']:.3f}** and **R² explanatory power of {evaluation.get('r2', 0):.3f}**."
                    else:
                        resp_text += f"Cross-validation score: {run.champion_score}."
                else:
                    resp_text = "No predictive model was trained for this analysis run (either no target column was set or modeling was skipped)."

            elif "health" in q_lower or "quality" in q_lower or "missing" in q_lower:
                health = profile.get("health_score", 100.0)
                missing = profile.get("missing_cells_total", 0)
                dups = profile.get("duplicate_rows", 0)
                resp_text = (
                    f"Dataset Data Quality Health Score is **{health:.1f}%**. "
                    f"The dataset contained {missing:,} missing values and {dups:,} duplicate rows before preprocessing."
                )

            elif "summary" in q_lower or "executive" in q_lower or "overview" in q_lower:
                resp_text = run.executive_summary or "Analysis complete. Review the workspace tab for strategic findings."

            else:
                if insights:
                    resp_text = "**Key Analytical Insights:**\n\n" + "\n".join(f"• {ins}" for ins in insights[:4])
                else:
                    resp_text = f"Analysis status: **{run.status}** with duration {run.duration_ms:.0f}ms."

        msg_record = ChatMessageModel(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            analysis_id=analysis_id,
            user_query=query,
            agent_response=resp_text,
            source=source,
        )
        db.add(msg_record)
        db.commit()

        return ChatResponse(
            analysis_id=analysis_id,
            query=query,
            response=resp_text,
            source=source,
            suggested_followups=followups,
        )
