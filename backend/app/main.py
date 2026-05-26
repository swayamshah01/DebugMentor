import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import submit, users, run, hint, testcases, profile, patterns
from app import auth
from app.database import Base, engine

logger = logging.getLogger(__name__)

# Create tables on startup (remove once Alembic handles all migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DebugMentor API",
    description=(
        "AI-powered code debugging assistant backend. "
        "Phase 1: real Python execution + pattern analysis. "
        "Phase 2: LLM + sandboxed Docker execution."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(submit.router, prefix="/api", tags=["Submissions"])
app.include_router(run.router,    prefix="/api", tags=["Execution"])
app.include_router(users.router,  prefix="/api", tags=["Users"])
app.include_router(auth.router,   prefix="/api", tags=["Auth"])
app.include_router(hint.router,   prefix="/api", tags=["Hints"])
app.include_router(testcases.router, prefix="/api", tags=["Test Cases"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(patterns.router, prefix="", tags=["Patterns"])


@app.on_event("startup")
def seed_curated_content_on_startup():
    """Keep the local curated problem bank in sync after old dummy seeds."""
    if os.getenv("AUTO_SEED_CURATED_CONTENT", "true").lower() not in {"1", "true", "yes"}:
        return

    try:
        backend_root = Path(__file__).resolve().parents[2]
        if str(backend_root) not in sys.path:
            sys.path.insert(0, str(backend_root))

        from seed_data import seed

        seed()
        logger.info("Curated DSA content is synced.")
    except Exception as exc:
        logger.warning("Curated DSA content sync failed: %s", exc, exc_info=True)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "DebugMentor API", "version": "1.0.0"}
