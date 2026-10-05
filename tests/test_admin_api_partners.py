from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import requires_db


@pytest.fixture(autouse=True)
def _admin_jwt_secret(monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")


@asynccontextmanager
async def authed_client(store):
    from admin_api.app import create_app

    await store.create_admin_user(email="admin@example.com", password="admin123")
    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin123"},
        )
        client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield client


@requires_db
async def test_created_partner_logo_path_and_active_flag_are_what_the_list_returns(store):
    async with authed_client(store) as client:
        created = await client.post(
            "/api/partners",
            json={
                "name": "Spa Bali",
                "type": "beauty_service",
                "referral_url": "https://example.com/spa",
                "blurb": "Массаж",
                "logo_path": "media/partners/spa.jpeg",
                "is_active": True,
                "sort_order": 3,
            },
        )
        assert created.status_code == 201
        partner_id = created.json()["id"]

        updated = await client.patch(
            f"/api/partners/{partner_id}",
            json={
                "name": "Spa Bali",
                "type": "beauty_service",
                "referral_url": "https://example.com/spa",
                "blurb": "Массаж",
                "logo_path": "media/partners/spa-new.jpeg",
                "is_active": False,
                "sort_order": 3,
            },
        )
        assert updated.status_code == 200

        listed = await client.get("/api/partners")

    assert listed.status_code == 200
    row = next(item for item in listed.json() if item["id"] == partner_id)
    assert row["logo_path"] == "media/partners/spa-new.jpeg"
    assert row["is_active"] is False
    assert "logo_url" not in row
