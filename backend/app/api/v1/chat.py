"""AI Analyst chat API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def ask_ai_analyst(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Submit a contextual natural language question regarding an analysis run."""
    return ChatService.answer_query(
        analysis_id=payload.analysis_id,
        query=payload.query,
        db=db,
    )
