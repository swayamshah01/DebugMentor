from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import submit, users
from app.database import Base, engine

# ── Create tables on startup ──────────────────────────────────────────────────
# NOTE: Remove this once Alembic migrations are fully set up.
# Use `alembic upgrade head` instead for production.
Base.metadata.create_all(bind=engine)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="DebugMentor API",
    description=(
        "AI-powered code debugging assistant backend. "
        "Phase 1: skeleton with dummy analysis. "
        "Phase 2: real LLM + AST analysis."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA dev server (optional)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(submit.router, prefix="/api", tags=["Submissions"])
app.include_router(users.router,  prefix="/api", tags=["Users"])


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe — returns 200 OK if the server is running."""
    return {
        "status": "ok",
        "service": "DebugMentor API",
        "version": "1.0.0",
    }
