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
async def test_assigned_partner_user_is_listed_until_deleted(store):
    async with authed_client(store) as client:
        partner = await client.post(
            "/api/partners",
            json={
                "name": "Spa Bali",
                "type": "beauty_service",
                "referral_url": "https://example.com/spa",
                "blurb": "",
                "logo_path": "",
                "is_active": True,
                "sort_order": 1,
            },
        )
        assert partner.status_code == 201
        partner_id = partner.json()["id"]

        created = await client.post(
            "/api/partner-users",
            json={
                "email": "shop@example.com",
                "password": "shop-secret",
                "partner_ids": [partner_id],
            },
        )
        assert created.status_code == 201
        user_id = created.json()["id"]

        listed = await client.get("/api/partner-users")
        row = next(item for item in listed.json() if item["id"] == user_id)
        assert row["email"] == "shop@example.com"
        assert row["partners"] == [{"id": partner_id, "name": "Spa Bali"}]

        rejected = await client.post(
            "/api/partner-users",
            json={
                "email": "empty@example.com",
                "password": "shop-secret",
                "partner_ids": [],
            },
        )
        assert rejected.status_code == 422

        deleted = await client.delete(f"/api/partner-users/{user_id}")
        assert deleted.status_code == 204

        remaining = await client.get("/api/partner-users")
        assert all(item["id"] != user_id for item in remaining.json())
