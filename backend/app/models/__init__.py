"""
models/__init__.py

Import all models here so Alembic can detect them
when it inspects Base.metadata.
"""
from app.models.user import User           # noqa: F401
from app.models.submission import Submission  # noqa: F401
from app.models.mistake import Mistake     # noqa: F401
from app.models.pattern import Pattern     # noqa: F401
from app.models.problem import Problem     # noqa: F401
from app.models.testcase import TestCase   # noqa: F401
