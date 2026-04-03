from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    # For PostgreSQL: use connection pooling defaults
    pool_pre_ping=True,       # test connections before use
    pool_recycle=300,         # recycle connections every 5 minutes
    echo=settings.DEBUG,      # log SQL in debug mode
)

# ── Session factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Declarative base (shared by all models) ───────────────────────────────────
Base = declarative_base()


# ── Dependency (FastAPI) ──────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a DB session and closes it on exit.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
