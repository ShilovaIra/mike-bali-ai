from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import requires_db


@pytest.fixture(autouse=True)
def _admin_jwt_secret(monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")


@requires_db
async def test_authenticated_stats_includes_users_leads_topic_label_and_source(store):
    from admin_api.app import create_app

    await store.create_admin_user(email="admin@example.com", password="admin123")
    await store.start_conversation("telegram", "1001", source="instagram")
    await store.start_conversation("telegram", "1002", source="unknown")
    await store.start_conversation("telegram", "1003", source="TgTrack-PJabc")
    await store.start_conversation("telegram", "1004", source="tgtrack-PJdef")
    await store.record_topic_event("telegram", "1001", topic="esim")
    created = await store.create_lead("telegram", "1001", snapshot={"kind": "rent"})
    assert created is not None

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin123"},
        )
        response = await client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total_users"] == 4
    assert body["leads_all_time"] == 1
    assert body["users_by_first_source"]["instagram"] == 1
    assert body["users_by_first_source"]["unknown"] == 1
    assert body["users_by_first_source"]["tgtrack"] == 2
    assert "TgTrack-PJabc" not in body["users_by_first_source"]
    esim = next(row for row in body["topics_all_time"] if row["slug"] == "esim")
    assert esim["label"] == "📱 eSIM"
    assert esim["unique_users"] == 1
    assert esim["taps"] == 1
