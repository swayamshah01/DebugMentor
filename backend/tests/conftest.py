import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, get_db
from app.auth import get_current_user
from app.engines import llm_layer


llm_layer.gemini_model = None
llm_layer.redis_client = None


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def api_client(db_session):
    def set_current_user(user):
        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    try:
        yield client, set_current_user
    finally:
        app.dependency_overrides.clear()
