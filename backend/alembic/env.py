"""
Alembic environment configuration for DebugMentor.

This file:
- Loads DATABASE_URL from .env
- Points Alembic at the SQLAlchemy Base metadata
- Imports all models so autogenerate can detect them
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# ── Add project root to path so app.* imports work ────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

# ── Load alembic.ini config ───────────────────────────────────────────────────
alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# ── Override sqlalchemy.url from .env (never hardcode it) ─────────────────────
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set. Check your .env file.")
alembic_config.set_main_option("sqlalchemy.url", database_url)

# ── Import Base + all models so Alembic detects table changes ─────────────────
from app.database import Base          # noqa: E402
from app.models import user, submission  # noqa: E402, F401  ← must import both

target_metadata = Base.metadata


# ── Migration runners ─────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """
    Run migrations without a live DB connection (generates SQL script).
    Useful for dry-run / review before applying.
    """
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations against a live database connection.
    """
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
