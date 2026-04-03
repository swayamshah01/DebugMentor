"""
models/__init__.py

Import all models here so Alembic can detect them
when it inspects Base.metadata.
"""
from app.models.user import User           # noqa: F401
from app.models.submission import Submission  # noqa: F401
