from __future__ import annotations

import os
from contextlib import asynccontextmanager

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "test-key"

import pytest
from httpx import ASGITransport, AsyncClient

import bot
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
async def test_operator_adds_an_active_partner_and_sees_them_in_chat(store):
    async with authed_client(store) as client:
        created_partner = await client.post(
            "/api/partners",
            json={
                "name": "Ex24.pro",
                "type": "money_exchange",
                "referral_url": "https://ex24qr.com/wtakeox",
                "blurb": "Лицензированный обмен валюты.",
                "is_active": True,
                "sort_order": 1,
            },
        )
        assert created_partner.status_code == 201
        partner_id = created_partner.json()["id"]

        added = await client.post("/api/knowledge-base", json={"partner_id": partner_id})
        assert added.status_code == 201

        listed = await client.get("/api/knowledge-base")

    assert listed.status_code == 200
    match = next(row for row in listed.json() if row["partner_id"] == partner_id)
    assert match["name"] == "Ex24.pro"
    assert match["kind"] == "💰 Обмен"
    assert match["blurb"] == "Лицензированный обмен валюты."
    assert match["referral_url"] == "https://ex24qr.com/wtakeox"
    assert match["in_chat"] is True


@requires_db
async def test_adding_the_same_partner_again_is_rejected(store):
    async with authed_client(store) as client:
        created_partner = await client.post(
            "/api/partners",
            json={
                "name": "Ex24.pro",
                "type": "money_exchange",
                "referral_url": "https://ex24qr.com/wtakeox",
                "blurb": "",
                "is_active": True,
                "sort_order": 1,
            },
        )
        partner_id = created_partner.json()["id"]
        first = await client.post("/api/knowledge-base", json={"partner_id": partner_id})
        assert first.status_code == 201

        second = await client.post("/api/knowledge-base", json={"partner_id": partner_id})
        assert second.status_code == 409

        listed = await client.get("/api/knowledge-base")

    rows = [row for row in listed.json() if row["partner_id"] == partner_id]
    assert len(rows) == 1


@requires_db
async def test_removing_a_knowledge_base_row_keeps_the_partner(store):
    async with authed_client(store) as client:
        created_partner = await client.post(
            "/api/partners",
            json={
                "name": "Ex24.pro",
                "type": "money_exchange",
                "referral_url": "https://ex24qr.com/wtakeox",
                "blurb": "Лицензированный обмен валюты.",
                "is_active": True,
                "sort_order": 1,
            },
        )
        partner_id = created_partner.json()["id"]
        added = await client.post("/api/knowledge-base", json={"partner_id": partner_id})
        assert added.status_code == 201
        row_id = added.json()["id"]

        deleted = await client.delete(f"/api/knowledge-base/{row_id}")
        assert deleted.status_code == 204

        listed = await client.get("/api/knowledge-base")
        partners = await client.get("/api/partners")

    assert listed.json() == []
    assert any(partner["id"] == partner_id for partner in partners.json())


@requires_db
async def test_inactive_partner_stays_listed_but_not_in_chat(store):
    async with authed_client(store) as client:
        created_partner = await client.post(
            "/api/partners",
            json={
                "name": "Ex24.pro",
                "type": "money_exchange",
                "referral_url": "https://ex24qr.com/wtakeox",
                "blurb": "Лицензированный обмен валюты.",
                "is_active": False,
                "sort_order": 1,
            },
        )
        partner_id = created_partner.json()["id"]
        added = await client.post("/api/knowledge-base", json={"partner_id": partner_id})
        assert added.status_code == 201

        listed = await client.get("/api/knowledge-base")

    match = next(row for row in listed.json() if row["partner_id"] == partner_id)
    assert match["name"] == "Ex24.pro"
    assert match["in_chat"] is False


@requires_db
async def test_model_prompt_quotes_active_partners_and_skips_inactive_ones(store, monkeypatch):
    monkeypatch.setattr(bot, "store", store)
    monkeypatch.setattr(bot, "places", None)

    empty = await bot.current_system_prompt()
    assert empty == bot.system_prompt()
    assert "База знаний" not in empty

    active = await store.create_partner(
        name="Ex24.pro",
        type="money_exchange",
        referral_url="https://ex24qr.com/wtakeox",
        blurb="Лицензированный обмен валюты.",
        is_active=True,
    )
    inactive = await store.create_partner(
        name="Hidden Exchange",
        type="money_exchange",
        referral_url="https://example.com/hidden",
        blurb="Не показывать",
        is_active=False,
    )
    await store.add_knowledge_base_partner(active.id)
    await store.add_knowledge_base_partner(inactive.id)

    told = await bot.current_system_prompt()
    assert "https://ex24qr.com/wtakeox" in told
    assert "https://example.com/hidden" not in told
    assert "Не ищи в Google и не добавляй другие места." in told
