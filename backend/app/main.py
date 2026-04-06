from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import submit, users, run
from app import auth
from app.database import Base, engine

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
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA (optional)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(submit.router, prefix="/api", tags=["Submissions"])
app.include_router(run.router,    prefix="/api", tags=["Execution"])
app.include_router(users.router,  prefix="/api", tags=["Users"])
app.include_router(auth.router,   prefix="/api", tags=["Auth"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "DebugMentor API", "version": "1.0.0"}
