from __future__ import annotations

from contextlib import asynccontextmanager

from httpx import ASGITransport, AsyncClient

from tests.conftest import requires_db

MONEY_TYPE = {
    "slug": "money_exchange",
    "is_menu_visible": True,
    "sort_order": 20,
    "button_label": "💰 \nОбмен",
    "topic_label": "💰 Обмен",
    "intro": "Вот партнёры для обмена:",
    "fallback": "Пока нет доступных партнёров по обмену. Напишите Майку — подскажу, что можно сделать.",
    "caption_emoji": "💰",
    "caption_cta": "⬇️ Обменять сейчас ⬇️",
    "button_template": "Обменять с {name}",
}


@asynccontextmanager
async def operator_client(store, *, partner_name: str = "Money Shop"):
    from admin_api.app import create_app

    await store.create_admin_user(email="admin@example.com", password="admin123")
    partner = await store.create_partner(
        name=partner_name,
        type="money_exchange",
        referral_url="https://example.com/money",
    )
    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin123"},
        )
        client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield client, partner


async def create_shop_user(client, partner_id, *, email: str = "shop@example.com") -> str:
    created = await client.post(
        "/api/partner-users",
        json={
            "email": email,
            "password": "shop-secret",
            "partner_ids": [str(partner_id)],
        },
    )
    assert created.status_code == 201
    login = await client.post(
        "/api/partner/auth/login",
        json={"email": email, "password": "shop-secret"},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


@requires_db
async def test_operator_creates_partner_user_who_sees_zero_stats_for_that_partner(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        created = await client.post(
            "/api/partner-users",
            json={
                "email": "shop@example.com",
                "password": "shop-secret",
                "partner_ids": [str(partner.id)],
            },
        )
        assert created.status_code == 201
        assert created.json()["email"] == "shop@example.com"

        partner_login = await client.post(
            "/api/partner/auth/login",
            json={"email": "shop@example.com", "password": "shop-secret"},
        )
        assert partner_login.status_code == 200
        stats = await client.get(
            f"/api/partner/stats?partner_id={partner.id}",
            headers={"Authorization": f"Bearer {partner_login.json()['access_token']}"},
        )

    assert stats.status_code == 200
    body = stats.json()
    assert body["partner_id"] == str(partner.id)
    zeros = {"views": 0, "referral_clicks": 0, "opened_views": 0}
    assert body["all_time"] == zeros
    assert body["last_30_days"] == zeros
    assert body["category_users"]["phrase"] == "💰 Обмен"


@requires_db
async def test_partner_user_login_with_wrong_password_returns_401(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        await create_shop_user(client, partner.id)
        response = await client.post(
            "/api/partner/auth/login",
            json={"email": "shop@example.com", "password": "wrong"},
        )

    assert response.status_code == 401


@requires_db
async def test_operator_token_cannot_read_partner_stats(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        response = await client.get(f"/api/partner/stats?partner_id={partner.id}")

    assert response.status_code == 401


@requires_db
async def test_partner_user_token_cannot_read_operator_stats(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        token = await create_shop_user(client, partner.id)
        stats = await client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {token}"},
        )
        partners = await client.get(
            "/api/partners",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert stats.status_code == 401
    assert partners.status_code == 401


@requires_db
async def test_create_partner_user_with_operator_email_is_rejected(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        response = await client.post(
            "/api/partner-users",
            json={
                "email": "admin@example.com",
                "password": "shop-secret",
                "partner_ids": [str(partner.id)],
            },
        )

    assert response.status_code == 409


@requires_db
async def test_partner_user_me_lists_partners_they_can_access(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, first):
        other = await store.create_partner(
            name="Ex24",
            type="money_exchange",
            referral_url="https://example.com/ex24",
        )
        created = await client.post(
            "/api/partner-users",
            json={
                "email": "shop@example.com",
                "password": "shop-secret",
                "partner_ids": [str(first.id), str(other.id)],
            },
        )
        assert created.status_code == 201
        login = await client.post(
            "/api/partner/auth/login",
            json={"email": "shop@example.com", "password": "shop-secret"},
        )
        me = await client.get(
            "/api/partner/me",
            headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        )

    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "shop@example.com"
    names = {p["name"]: p["id"] for p in body["partners"]}
    assert names["Money Shop"] == str(first.id)
    assert names["Ex24"] == str(other.id)


@requires_db
async def test_partner_user_cannot_read_stats_for_partner_without_access(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, first):
        other = await store.create_partner(
            name="Ex24",
            type="money_exchange",
            referral_url="https://example.com/ex24",
        )
        token = await create_shop_user(client, first.id)
        response = await client.get(
            f"/api/partner/stats?partner_id={other.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 404


@requires_db
async def test_deleted_partner_user_cannot_sign_in(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        created = await client.post(
            "/api/partner-users",
            json={
                "email": "shop@example.com",
                "password": "shop-secret",
                "partner_ids": [str(partner.id)],
            },
        )
        user_id = created.json()["id"]
        deleted = await client.delete(f"/api/partner-users/{user_id}")
        assert deleted.status_code == 204
        login = await client.post(
            "/api/partner/auth/login",
            json={"email": "shop@example.com", "password": "shop-secret"},
        )

    assert login.status_code == 401


@requires_db
async def test_wrapped_offer_redirects_to_partner_referral_url(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    from partner_dashboard.offers import wrap_offer_for_user

    async with operator_client(store) as (client, partner):
        ctx = await store.start_conversation("telegram", "9001")
        path = await wrap_offer_for_user(
            store.pool, partner=partner, user_id=ctx.user_id
        )
        assert path.startswith("/r/")
        response = await client.get(path, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == partner.referral_url


@requires_db
async def test_wrap_click_counts_as_view_click_and_opened_view(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    from partner_dashboard.offers import wrap_offer_for_user

    async with operator_client(store) as (client, partner):
        ctx = await store.start_conversation("telegram", "9002")
        path = await wrap_offer_for_user(
            store.pool, partner=partner, user_id=ctx.user_id
        )
        await client.get(path, follow_redirects=False)
        token = await create_shop_user(client, partner.id)
        stats = await client.get(
            f"/api/partner/stats?partner_id={partner.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert stats.status_code == 200
    body = stats.json()
    assert body["all_time"] == {"views": 1, "referral_clicks": 1, "opened_views": 1}
    assert body["last_30_days"] == {"views": 1, "referral_clicks": 1, "opened_views": 1}


@requires_db
async def test_second_tap_on_same_showing_counts_click_not_opened_view(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    from partner_dashboard.offers import wrap_offer_for_user

    async with operator_client(store) as (client, partner):
        ctx = await store.start_conversation("telegram", "9003")
        path = await wrap_offer_for_user(
            store.pool, partner=partner, user_id=ctx.user_id
        )
        await client.get(path, follow_redirects=False)
        await client.get(path, follow_redirects=False)
        token = await create_shop_user(client, partner.id)
        stats = await client.get(
            f"/api/partner/stats?partner_id={partner.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert stats.json()["all_time"] == {
        "views": 1,
        "referral_clicks": 2,
        "opened_views": 1,
    }


@requires_db
async def test_partner_stats_count_distinct_users_who_chose_that_category(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        await store.start_conversation("telegram", "9101", source="unknown")
        await store.record_topic_event("telegram", "9101", topic="money_exchange")
        async with store.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE topic_events
                SET created_at = now() - interval '40 days'
                WHERE topic = 'money_exchange'
                """
            )
        await store.start_conversation("telegram", "9102", source="unknown")
        await store.record_topic_event("telegram", "9102", topic="money_exchange")
        await store.record_topic_event("telegram", "9102", topic="money_exchange")
        await store.start_conversation("telegram", "9103", source="unknown")
        await store.record_topic_event("telegram", "9103", topic="visa_service")

        token = await create_shop_user(client, partner.id)
        stats = await client.get(
            f"/api/partner/stats?partner_id={partner.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert stats.status_code == 200
    assert stats.json()["category_users"] == {
        "phrase": "💰 Обмен",
        "all_time": 2,
        "last_30_days": 1,
    }


@requires_db
async def test_updated_topic_label_shows_on_partner_stats(store, monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")
    async with operator_client(store) as (client, partner):
        updated = await client.patch(
            "/api/partner-types/money_exchange",
            json={**MONEY_TYPE, "topic_label": "обмен валюты"},
        )
        assert updated.status_code == 200
        token = await create_shop_user(client, partner.id)
        stats = await client.get(
            f"/api/partner/stats?partner_id={partner.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert stats.status_code == 200
    assert stats.json()["category_users"]["phrase"] == "обмен валюты"
