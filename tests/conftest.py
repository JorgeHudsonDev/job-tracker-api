import os

# Deben definirse ANTES de importar la app: config.py lee el entorno al importarse.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def make_user(client):
    """Registra un usuario, hace login y devuelve las cabeceras con su token."""

    def _make_user(username: str = "ana", password: str = "password123"):
        client.post(
            "/auth/register", json={"username": username, "password": password}
        )
        response = client.post(
            "/auth/login", data={"username": username, "password": password}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make_user