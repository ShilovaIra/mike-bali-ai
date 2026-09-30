from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import requires_db

DIVING = {
    "slug": "diving",
    "is_menu_visible": True,
    "sort_order": 70,
    "button_label": "🤿 \nДайвинг",
    "topic_label": "🤿 Дайвинг",
    "intro": "Вот партнёры по дайвингу:",
    "fallback": "Пока нет партнёров по дайвингу.",
    "caption_emoji": "🤿",
    "caption_cta": "⬇️ Забронировать ⬇️",
    "button_template": "Забронировать с {name}",
}


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
async def test_created_partner_type_button_label_is_what_the_list_returns(store):
    async with authed_client(store) as client:
        created = await client.post("/api/partner-types", json=DIVING)
        assert created.status_code == 201

        updated = await client.patch(
            "/api/partner-types/diving",
            json={**DIVING, "button_label": "🤿 \nДайвинг на Бали"},
        )
        assert updated.status_code == 200

        listed = await client.get("/api/partner-types")

    assert listed.status_code == 200
    row = next(item for item in listed.json() if item["slug"] == "diving")
    assert row["button_label"] == "🤿 \nДайвинг на Бали"
    assert row["topic_label"] == "🤿 Дайвинг"
    assert "follow_up_text" not in row
    assert "choice_phrase" not in row
