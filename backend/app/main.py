import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import auth
from app.config import settings
from app.routers import hint, patterns, profile, run, submit, users


logger = logging.getLogger(__name__)


def sync_curated_content() -> None:
    if not settings.AUTO_SEED_CURATED_CONTENT:
        return

    try:
        from seed_data import seed

        seed()
        logger.info("Curated practice content is synchronized.")
    except Exception:
        logger.exception(
            "Content synchronization failed. Run 'alembic upgrade head' and restart the backend."
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Alembic owns the schema. Startup only synchronizes versioned content.
    sync_curated_content()
    yield


app = FastAPI(
    title="DebugMentor API",
    description="DSA practice API with visible-case runs, official submissions, and personalized hints.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials="*" not in settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(patterns.router, tags=["Practice catalog"])
app.include_router(run.router, prefix="/api", tags=["Practice"])
app.include_router(submit.router, prefix="/api", tags=["Practice"])
app.include_router(hint.router, prefix="/api", tags=["Hints"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok", "service": "DebugMentor API", "version": "2.0.0"}
