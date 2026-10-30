from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import requires_db

ROOT = Path(__file__).resolve().parents[1]


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
async def test_saving_a_partner_keeps_an_existing_logo(store):
    partner = await store.create_partner(
        name="Spa Bali",
        type="beauty_service",
        referral_url="https://example.com/spa",
        blurb="Массаж",
        logo_path="media/partners/esim-logo.png",
        is_active=True,
        sort_order=3,
    )
    async with authed_client(store) as client:
        updated = await client.patch(
            f"/api/partners/{partner.id}",
            json={
                "name": "Spa Bali",
                "type": "beauty_service",
                "referral_url": "https://example.com/spa",
                "blurb": "Массаж",
                "logo_path": "media/partners/spa-new.jpeg",
                "is_active": False,
                "sort_order": 4,
            },
        )
        listed = await client.get("/api/partners")

    assert updated.status_code == 200
    assert updated.json()["logo_path"] == "media/partners/esim-logo.png"
    assert updated.json()["logo_url"] == ""
    row = next(item for item in listed.json() if item["id"] == str(partner.id))
    assert row["logo_path"] == "media/partners/esim-logo.png"
    assert row["is_active"] is False


@requires_db
async def test_logged_in_admin_receives_the_bytes_of_a_bundled_partner_logo(store):
    logo_rel = "media/partners/esim-logo.png"
    partner = await store.create_partner(
        name="eSIM",
        type="esim",
        referral_url="https://example.com/esim",
        blurb="Связь",
        logo_path=logo_rel,
        is_active=True,
        sort_order=1,
    )
    async with authed_client(store) as client:
        logo = await client.get(f"/api/partners/{partner.id}/logo")

    assert logo.status_code == 200
    assert logo.headers["content-type"].startswith("image/")
    assert logo.content == (ROOT / logo_rel).read_bytes()


@requires_db
async def test_partner_logo_is_not_served_when_missing_or_outside_media_partners(store):
    async with authed_client(store) as client:
        for logo_path in ("", "media/partners/missing-logo.jpeg", "media/partners/../../pytest.ini"):
            partner = await store.create_partner(
                name="Spa Bali",
                type="beauty_service",
                referral_url="https://example.com/spa",
                blurb="Массаж",
                logo_path=logo_path,
                is_active=True,
                sort_order=2,
            )
            logo = await client.get(f"/api/partners/{partner.id}/logo")
            assert logo.status_code == 404


@requires_db
async def test_partner_logo_without_a_token_is_rejected(store):
    partner = await store.create_partner(
        name="eSIM",
        type="esim",
        referral_url="https://example.com/esim",
        blurb="Связь",
        logo_path="media/partners/esim-logo.png",
        is_active=True,
        sort_order=1,
    )
    async with authed_client(store) as client:
        client.headers.pop("Authorization", None)
        logo = await client.get(f"/api/partners/{partner.id}/logo")

    assert logo.status_code == 401
