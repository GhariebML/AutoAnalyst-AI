"""Relational database models and engine for AutoAnalyst AI backend."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from backend.app.core.config import settings

Base = declarative_base()
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatasetModel(Base):
    """Uploaded and versioned dataset record."""

    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_format = Column(String(32), nullable=False)
    rows = Column(Integer, nullable=True)
    columns = Column(Integer, nullable=True)
    health_score = Column(Float, nullable=True)
    schema_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    analyses = relationship("AnalysisRunModel", back_populates="dataset", cascade="all, delete-orphan")


class AnalysisRunModel(Base):
    """Analysis execution record."""

    __tablename__ = "analysis_runs"

    id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False)
    target_column = Column(String(128), nullable=True)
    model_task = Column(String(32), default="auto")
    status = Column(String(32), default="pending")  # pending, running, paused_for_approval, completed, failed
    champion_model_name = Column(String(128), nullable=True)
    champion_score = Column(Float, nullable=True)
    executive_summary = Column(Text, nullable=True)
    insights_json = Column(Text, nullable=True)
    findings_json = Column(Text, nullable=True)
    profile_json = Column(Text, nullable=True)
    eda_json = Column(Text, nullable=True)
    model_results_json = Column(Text, nullable=True)
    evaluation_json = Column(Text, nullable=True)
    report_path = Column(String(512), nullable=True)
    duration_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    dataset = relationship("DatasetModel", back_populates="analyses")
    artifacts = relationship("ArtifactModel", back_populates="analysis", cascade="all, delete-orphan")


class ArtifactModel(Base):
    """Generated report, chart, or model binary artifact."""

    __tablename__ = "artifacts"

    id = Column(String(64), primary_key=True, index=True)
    analysis_id = Column(String(64), ForeignKey("analysis_runs.id"), nullable=False)
    artifact_type = Column(
        String(32), nullable=False
    )  # html_report, markdown_report, json_report, cleaned_csv, model_pkl
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    analysis = relationship("AnalysisRunModel", back_populates="artifacts")


class ChatMessageModel(Base):
    """Persisted Q&A message exchange."""

    __tablename__ = "chat_messages"

    id = Column(String(64), primary_key=True, index=True)
    analysis_id = Column(String(64), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    source = Column(String(32), default="rules")  # rules | llm
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    """Initialize database tables and run automatic schema migration."""
    Base.metadata.create_all(bind=engine)
    # Check and add missing columns for SQLite
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(analysis_runs)"))
            existing_cols = {row[1] for row in result.fetchall()}
            if existing_cols:
                required_cols = {
                    "findings_json": "TEXT",
                    "eda_json": "TEXT",
                    "model_results_json": "TEXT",
                    "champion_score": "REAL",
                }
                for col_name, col_type in required_cols.items():
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE analysis_runs ADD COLUMN {col_name} {col_type}"))
                conn.commit()
        except Exception:
            pass


def get_db():
    """Database session dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
