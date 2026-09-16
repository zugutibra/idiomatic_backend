import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base_all import Base
from app.main import app
from app.models.idiom import Idiom


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    db.add(
        Idiom(
            phrase="Break the ice",
            meaning="To make people feel comfortable.",
            example_sentence="He broke the ice with a joke.",
            topic="relationships",
            difficulty="easier",
        )
    )
    db.add(
        Idiom(
            phrase="Hit the books",
            meaning="To study hard.",
            example_sentence="She hit the books before finals.",
            topic="education",
            difficulty="easier",
        )
    )
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "secret123", "display_name": "Test User"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
