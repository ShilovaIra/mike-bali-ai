"""How the bot sends a partner card: CDN logo, bundled logo, or text only."""

from __future__ import annotations

import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "test-key"

from telegram.error import BadRequest

import bot
from partners import PartnerCard
from storage import AssetStorage
from tests.conftest import S3_ENV, object_key

CDN = S3_ENV["S3_PUBLIC_BASE_URL"]


class FakeMessage:
    def __init__(self, *, photo_error: Exception | None = None):
        self.photo_error = photo_error
        self.photos: list[dict] = []
        self.texts: list[dict] = []

    async def reply_photo(self, **kwargs):
        if self.photo_error is not None:
            raise self.photo_error
        photo = kwargs["photo"]
        kwargs["photo"] = photo if isinstance(photo, str) else ("file", photo.name)
        self.photos.append(kwargs)

    async def reply_text(self, text, **kwargs):
        self.texts.append({"text": text, **kwargs})


def card(logo_path: str | None) -> PartnerCard:
    return PartnerCard(
        caption_html="<b>eSIM</b>",
        button_text="Купить",
        referral_url="https://example.com/go",
        logo_path=logo_path,
    )


async def test_uploaded_logo_is_sent_by_cdn_url(monkeypatch):
    monkeypatch.setattr(bot, "storage", AssetStorage.from_env(S3_ENV))
    message = FakeMessage()

    await bot.send_partner_card(message, card("partners/1/logo-abc.png"))

    assert message.photos[0]["photo"] == f"{CDN}/{object_key('partners/1/logo-abc.png')}"
    assert message.texts == []


async def test_card_falls_back_to_text_when_telegram_cannot_fetch_logo(monkeypatch):
    monkeypatch.setattr(bot, "storage", AssetStorage.from_env(S3_ENV))
    message = FakeMessage(photo_error=BadRequest("Wrong file identifier/http url specified"))

    await bot.send_partner_card(message, card("partners/1/logo-gone.png"))

    assert [item["text"] for item in message.texts] == ["<b>eSIM</b>"]


async def test_uploaded_logo_without_storage_config_sends_text_card(monkeypatch):
    monkeypatch.setattr(bot, "storage", None)
    message = FakeMessage()

    await bot.send_partner_card(message, card("partners/1/logo-abc.png"))

    assert message.photos == []
    assert [item["text"] for item in message.texts] == ["<b>eSIM</b>"]


async def test_bundled_logo_is_still_sent_as_file(monkeypatch):
    monkeypatch.setattr(bot, "storage", AssetStorage.from_env(S3_ENV))
    message = FakeMessage()

    await bot.send_partner_card(message, card("media/partners/esim-logo.png"))

    assert len(message.photos) == 1
    kind, name = message.photos[0]["photo"]
    assert kind == "file" and name.endswith("media/partners/esim-logo.png")
    assert message.texts == []
