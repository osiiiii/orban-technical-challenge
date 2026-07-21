"""Backend tests.

Each test runs against a fresh in-memory SQLite database so results are
isolated and don't touch the developer's real shortener.db file.
"""
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud, models
from app.config import get_settings
from app.database import Base, get_db
from app.main import app

API_KEY = "test-key"
AUTH = {"X-API-Key": API_KEY}


@pytest.fixture()
def client():
    # Shared in-memory DB across connections via StaticPool.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    # Force a known API key and wire the test DB into the app.
    get_settings.cache_clear()
    settings = get_settings()
    settings.api_key = API_KEY
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        c._engine = engine
        c._session = TestingSession
        yield c

    app.dependency_overrides.clear()


def _create(client, url="https://example.com/some/long/path", **extra):
    body = {"long_url": url, **extra}
    return client.post("/api/shorten", json=body, headers=AUTH)


# --- Auth -----------------------------------------------------------------

def test_create_requires_api_key(client):
    resp = client.post("/api/shorten", json={"long_url": "https://example.com"})
    assert resp.status_code == 401


def test_create_rejects_wrong_api_key(client):
    resp = client.post(
        "/api/shorten",
        json={"long_url": "https://example.com"},
        headers={"X-API-Key": "wrong"},
    )
    assert resp.status_code == 401


# --- Happy path -----------------------------------------------------------

def test_create_returns_short_code(client):
    resp = _create(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["short_code"]
    assert data["short_url"].endswith(data["short_code"])
    assert data["long_url"] == "https://example.com/some/long/path"
    assert data["click_count"] == 0


def test_redirect_resolves_and_counts_clicks(client):
    code = _create(client).json()["short_code"]

    # follow_redirects=False so we can inspect the 307 and Location header.
    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com/some/long/path"

    # Click twice, then confirm the stats reflect both hits.
    client.get(f"/{code}", follow_redirects=False)
    stats = client.get(f"/api/stats/{code}", headers=AUTH).json()
    assert stats["click_count"] == 2


def test_stats_endpoint_shape(client):
    code = _create(client).json()["short_code"]
    stats = client.get(f"/api/stats/{code}", headers=AUTH).json()
    assert stats["short_code"] == code
    assert stats["is_expired"] is False
    assert stats["click_count"] == 0


def test_list_urls(client):
    _create(client, url="https://a.example.com")
    _create(client, url="https://b.example.com")
    resp = client.get("/api/urls", headers=AUTH)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# --- Edge cases -----------------------------------------------------------

def test_invalid_url_rejected(client):
    resp = _create(client, url="not-a-real-url")
    assert resp.status_code == 422


def test_missing_code_returns_404(client):
    assert client.get("/doesnotexist", follow_redirects=False).status_code == 404
    assert client.get("/api/stats/nope", headers=AUTH).status_code == 404


def test_duplicate_url_returns_same_code(client):
    first = _create(client, url="https://dup.example.com").json()
    second = _create(client, url="https://dup.example.com").json()
    assert first["short_code"] == second["short_code"]


def test_expired_link_returns_410(client):
    # Create a link, then backdate its expiry directly in the DB.
    code = _create(client, url="https://expired.example.com").json()["short_code"]
    db = client._session()
    try:
        url = crud.get_by_code(db, code)
        url.expires_at = models._utcnow() - timedelta(days=1)
        db.add(url)
        db.commit()
    finally:
        db.close()

    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 410


def test_expiry_days_sets_future_expiry(client):
    resp = _create(client, url="https://future.example.com", expires_in_days=7)
    assert resp.status_code == 201
    assert resp.json()["expires_at"] is not None
