from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import requires_db


@pytest.fixture(autouse=True)
def _admin_jwt_secret(monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")


@requires_db
async def test_login_with_valid_admin_returns_token_and_me_returns_email(store):
    from admin_api.app import create_app

    await store.create_admin_user(email="admin@example.com", password="admin123")

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin123"},
        )
        assert login.status_code == 200
        body = login.json()
        assert body["token_type"] == "bearer"
        token = body["access_token"]
        assert isinstance(token, str)
        assert len(token) > 10

        me = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert me.status_code == 200
    assert me.json() == {"email": "admin@example.com"}


@requires_db
async def test_wrong_password_and_anonymous_stats_are_rejected(store):
    from admin_api.app import create_app

    await store.create_admin_user(email="admin@example.com", password="admin123")

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "wrong"},
        )
        stats = await client.get("/api/stats")

    assert login.status_code == 401
    assert stats.status_code == 401
