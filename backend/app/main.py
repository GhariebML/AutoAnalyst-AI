"""FastAPI application main entrypoint for AutoAnalyst AI."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure src/ is in python path
src_dir = Path(__file__).resolve().parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from backend.app.api.v1.analyses import router as analyses_router  # noqa: E402
from backend.app.api.v1.artifacts import router as artifacts_router  # noqa: E402
from backend.app.api.v1.chat import router as chat_router  # noqa: E402
from backend.app.api.v1.dashboard import router as dashboard_router  # noqa: E402
from backend.app.api.v1.datasets import router as datasets_router  # noqa: E402
from backend.app.api.v1.health import router as health_router  # noqa: E402
from backend.app.api.v1.predictions import router as predictions_router  # noqa: E402
from backend.app.api.v1.runs import router as runs_router  # noqa: E402
from backend.app.api.v1.system import router as system_router  # noqa: E402
from backend.app.core.config import settings  # noqa: E402
from backend.app.core.telemetry import GLOBAL_METRICS, PrometheusMiddleware  # noqa: E402
from backend.app.models.database import init_db  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown routines."""
    logger.info("Initializing AutoAnalyst AI backend database...")
    init_db()
    logger.info("AutoAnalyst AI backend started successfully on version %s", settings.APP_VERSION)
    yield
    logger.info("Shutting down AutoAnalyst AI backend...")


# Initialize database tables
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade production API for AutoAnalyst AI autonomous multi-agent data analytics.",
    lifespan=lifespan,
)

# Prometheus Telemetry Middleware
app.add_middleware(PrometheusMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 routes
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(system_router, prefix=settings.API_V1_PREFIX)
app.include_router(datasets_router, prefix=settings.API_V1_PREFIX)
app.include_router(analyses_router, prefix=settings.API_V1_PREFIX)
app.include_router(runs_router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions_router, prefix=settings.API_V1_PREFIX)
app.include_router(artifacts_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)


@app.get(f"{settings.API_V1_PREFIX}/metrics", tags=["telemetry"])
def prometheus_metrics() -> Response:
    """Standard Prometheus plaintext metrics exposition for enterprise APM."""
    content = GLOBAL_METRICS.generate_prometheus_text()
    return Response(content=content, media_type="text/plain; version=0.0.4")


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "metrics_url": f"{settings.API_V1_PREFIX}/metrics",
    }
