from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode

from httpx import ASGITransport, AsyncClient

from tests.conftest import requires_db

ROOT = Path(__file__).resolve().parents[1]

BOT_TOKEN = "123456:test-token"


def sign_init_data(user: dict, bot_token: str = BOT_TOKEN) -> str:
    fields = {
        "auth_date": "1700000000",
        "query_id": "AAE",
        "user": json.dumps(user, ensure_ascii=False, separators=(",", ":")),
    }
    data_check = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


@requires_db
async def test_unsigned_visitor_sees_active_partners_in_sort_order_with_plain_links(store):
    hidden = await store.create_partner(
        name="Hidden FX",
        type="money_exchange",
        referral_url="https://example.com/hidden",
        blurb="Скрыт",
        is_active=False,
        sort_order=0,
    )
    await store.create_partner(
        name="Late FX",
        type="money_exchange",
        referral_url="https://example.com/late",
        blurb="Позже",
        sort_order=20,
    )
    await store.create_partner(
        name="Early FX",
        type="money_exchange",
        referral_url="https://example.com/early",
        blurb="Раньше",
        sort_order=5,
    )

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/tma/partners")

    assert response.status_code == 200
    body = response.json()
    assert [item["name"] for item in body] == ["Early FX", "Late FX"]
    assert [item["referral_url"] for item in body] == [
        "https://example.com/early",
        "https://example.com/late",
    ]
    assert all(item["id"] != str(hidden.id) for item in body)


@requires_db
async def test_partner_card_uses_the_type_chip_button_blurb_and_logo(store):
    partner = await store.create_partner(
        name="Early FX",
        type="money_exchange",
        referral_url="https://example.com/early",
        blurb="Обмен на Бали",
        logo_path="media/partners/ex24pro_logo.jpeg",
        sort_order=1,
    )

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        listed = await client.get("/api/tma/partners")
        logo = await client.get(f"/api/tma/partners/{partner.id}/logo")

    card = listed.json()[0]
    assert card["type_label"] == "Обмен"
    assert card["action"] == "Обменять с Early FX"
    assert card["blurb"] == "Обмен на Бали"
    assert card["logo_url"] == f"/api/tma/partners/{partner.id}/logo"
    assert logo.status_code == 200
    assert logo.headers["content-type"].startswith("image/")
    assert logo.content == (ROOT / "media/partners/ex24pro_logo.jpeg").read_bytes()


@requires_db
async def test_bad_signature_cannot_read_thread_save_or_open_partner(store):
    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma bad-signature"
        partner_id = "00000000-0000-4000-8000-000000000099"
        messages = await client.get("/api/tma/messages")
        saved = await client.put(f"/api/tma/favorites/{partner_id}")
        opened = await client.post(f"/api/tma/partners/{partner_id}/open")

    assert messages.status_code == 401
    assert saved.status_code == 401
    assert opened.status_code == 401


@requires_db
async def test_signed_person_sees_the_whole_thread_and_an_empty_thread_is_empty(
    store, monkeypatch
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    for index in range(21):
        await store.append_message(
            "telegram",
            "42",
            role="user" if index % 2 == 0 else "assistant",
            content=f"m{index}",
        )

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 42, "first_name": "Анна"})
        full = await client.get("/api/tma/messages")
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 99, "first_name": "Борис"})
        empty = await client.get("/api/tma/messages")

    assert full.status_code == 200
    assert [item["content"] for item in full.json()] == [f"m{index}" for index in range(21)]
    assert [item["role"] for item in full.json()] == [
        "user" if index % 2 == 0 else "assistant" for index in range(21)
    ]
    assert empty.status_code == 200
    assert empty.json() == []


@requires_db
async def test_exchange_question_is_stored_as_the_partner_list_with_tracked_links(
    store, monkeypatch
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    monkeypatch.setenv("PARTNER_OFFER_BASE_URL", "https://offers.example")
    types = await store.list_partner_types()
    intro = next(item.intro for item in types if item.slug == "money_exchange")
    await store.create_partner(
        name="Hidden FX",
        type="money_exchange",
        referral_url="https://example.com/hidden",
        is_active=False,
        sort_order=0,
    )
    await store.create_partner(
        name="Late FX",
        type="money_exchange",
        referral_url="https://example.com/late",
        sort_order=20,
    )
    await store.create_partner(
        name="Early FX",
        type="money_exchange",
        referral_url="https://example.com/early",
        sort_order=5,
    )
    await store.create_partner(
        name="Visa Desk",
        type="visa_service",
        referral_url="https://example.com/visa",
        sort_order=1,
    )

    async def choose(_text: str, _slugs: list[str]) -> str:
        return "money_exchange"

    from admin_api.app import create_app

    app = create_app(store=store, choose_partner_type=choose)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 42, "first_name": "Анна"})
        posted = await client.post("/api/tma/messages", json={"text": "Где обмен?"})
        assert posted.status_code == 200
        reply = posted.json()["reply"]
        followed = await client.get(
            reply.split("https://offers.example")[1].split()[0],
            follow_redirects=False,
        )
        thread = await client.get("/api/tma/messages")

    assert reply.startswith(intro)
    assert reply.index("Early FX") < reply.index("Late FX")
    assert "Hidden FX" not in reply
    assert "Visa Desk" not in reply
    assert "https://example.com/early" not in reply
    assert reply.count("https://offers.example/r/") == 2
    assert followed.status_code == 302
    assert followed.headers["location"] in {
        "https://example.com/early",
        "https://example.com/late",
    }
    assert [item["content"] for item in thread.json()] == ["Где обмен?", reply]
    assert [item["role"] for item in thread.json()] == ["user", "assistant"]


@requires_db
async def test_typed_exchange_question_in_the_bot_receives_the_same_partner_list(
    store, monkeypatch
):
    monkeypatch.setenv("PARTNER_OFFER_BASE_URL", "https://offers.example")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    types = await store.list_partner_types()
    intro = next(item.intro for item in types if item.slug == "money_exchange")
    await store.create_partner(
        name="Early FX",
        type="money_exchange",
        referral_url="https://example.com/early",
        sort_order=5,
    )

    import bot

    previous_store = bot.store
    bot.store = store

    async def choose(_text: str, _slugs: list[str]) -> str:
        return "money_exchange"

    monkeypatch.setattr(bot, "choose_partner_type", choose)
    sent: list[str] = []

    class Message:
        text = "Где обмен?"

        async def reply_text(self, text, **kwargs):
            sent.append(text)

        async def reply_photo(self, **kwargs):
            raise AssertionError("a typed question does not send a partner card")

    update = SimpleNamespace(
        message=Message(),
        effective_user=SimpleNamespace(id=42, first_name="Анна", username=None),
    )
    try:
        await bot.handle_message(update, SimpleNamespace())
    finally:
        bot.store = previous_store

    assert len(sent) == 1
    assert sent[0].startswith(intro)
    assert "Early FX" in sent[0]
    assert "https://example.com/early" not in sent[0]
    assert "https://offers.example/r/" in sent[0]
    thread = await store.list_thread_messages("telegram", "42")
    assert [item["content"] for item in thread] == ["Где обмен?", sent[0]]


@requires_db
async def test_normal_question_is_stored_as_mikes_written_answer(store, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)

    async def choose(_text: str, _slugs: list[str]) -> None:
        return None

    async def write_answer(_text: str) -> str:
        return "Пляж Баланган. Вот ссылка на карту."

    from admin_api.app import create_app

    app = create_app(store=store, choose_partner_type=choose, write_answer=write_answer)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 42, "first_name": "Анна"})
        posted = await client.post("/api/tma/messages", json={"text": "Где пляж?"})
        thread = await client.get("/api/tma/messages")

    assert posted.status_code == 200
    assert posted.json()["reply"] == "Пляж Баланган. Вот ссылка на карту."
    assert [item["content"] for item in thread.json()] == [
        "Где пляж?",
        "Пляж Баланган. Вот ссылка на карту.",
    ]
    assert [item["role"] for item in thread.json()] == ["user", "assistant"]


@requires_db
async def test_ready_property_answer_creates_a_lead_and_hides_the_marker(store, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)

    async def choose(_text: str, _slugs: list[str]) -> None:
        return None

    async def write_answer(_text: str) -> str:
        return "Вилла в Чангу на двоих.\nЗАЯВКА_ГОТОВА"

    from admin_api.app import create_app

    app = create_app(store=store, choose_partner_type=choose, write_answer=write_answer)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data(
            {"id": 42, "first_name": "Анна", "username": "anna"}
        )
        posted = await client.post("/api/tma/messages", json={"text": "Хочу виллу в Чангу"})
        thread = await client.get("/api/tma/messages")

    assert posted.status_code == 200
    assert posted.json()["reply"] == "Вилла в Чангу на двоих."
    assert thread.json()[1]["content"] == "Вилла в Чангу на двоих."
    assert await store.has_lead("telegram", "42")


@requires_db
async def test_saving_a_partner_twice_keeps_one_row_and_inactive_drops_out(
    store, monkeypatch
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    partner = await store.create_partner(
        name="Early FX",
        type="money_exchange",
        referral_url="https://example.com/early",
        sort_order=1,
    )

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 42, "first_name": "Анна"})
        first = await client.put(f"/api/tma/favorites/{partner.id}")
        second = await client.put(f"/api/tma/favorites/{partner.id}")
        listed = await client.get("/api/tma/favorites")
        await store.update_partner(
            partner.id,
            name=partner.name,
            type=partner.type,
            referral_url=partner.referral_url,
            is_active=False,
        )
        after = await client.get("/api/tma/favorites")

    assert first.status_code == 200
    assert second.status_code == 200
    assert [item["id"] for item in listed.json()] == [str(partner.id)]
    assert after.json() == []


@requires_db
async def test_opening_a_partner_returns_a_tracked_link(store, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    monkeypatch.setenv("PARTNER_OFFER_BASE_URL", "https://offers.example")
    partner = await store.create_partner(
        name="Early FX",
        type="money_exchange",
        referral_url="https://example.com/early",
        sort_order=1,
    )

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 42, "first_name": "Анна"})
        opened = await client.post(f"/api/tma/partners/{partner.id}/open")
        assert opened.status_code == 200
        url = opened.json()["url"]
        followed = await client.get(url.removeprefix("https://offers.example"), follow_redirects=False)

    assert url.startswith("https://offers.example/r/")
    assert followed.status_code == 302
    assert followed.headers["location"] == "https://example.com/early"


@requires_db
async def test_profile_returns_the_telegram_name(store, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data(
            {"id": 42, "first_name": "Анна", "last_name": "Иванова"}
        )
        named = await client.get("/api/tma/me")
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 7, "first_name": "Борис"})
        first_only = await client.get("/api/tma/me")

    assert named.status_code == 200
    assert named.json() == {"first_name": "Анна", "last_name": "Иванова"}
    assert first_only.json() == {"first_name": "Борис", "last_name": ""}


@requires_db
async def test_removing_a_saved_partner_drops_it_from_the_list(store, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    partner = await store.create_partner(
        name="Early FX",
        type="money_exchange",
        referral_url="https://example.com/early",
        sort_order=1,
    )

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 42, "first_name": "Анна"})
        await client.put(f"/api/tma/favorites/{partner.id}")
        removed = await client.delete(f"/api/tma/favorites/{partner.id}")
        listed = await client.get("/api/tma/favorites")

    assert removed.status_code == 204
    assert listed.json() == []


@requires_db
async def test_a_question_uses_the_model_when_no_writer_is_injected(store, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    calls: list[list[dict]] = []

    async def complete(messages):
        calls.append(messages)
        if len(calls) == 1:
            return "none"
        return "Пляж Баланган."

    monkeypatch.setattr("tourist_answers.complete", complete)

    from admin_api.app import create_app

    app = create_app(store=store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "tma " + sign_init_data({"id": 42, "first_name": "Анна"})
        posted = await client.post("/api/tma/messages", json={"text": "Где пляж?"})

    assert posted.status_code == 200
    assert posted.json()["reply"] == "Пляж Баланган."
    assert calls[1][-1]["content"] == "Где пляж?"
