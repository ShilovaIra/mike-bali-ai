from __future__ import annotations

from buttons import (
    ASK_MIKE_BUTTON,
    BUTTON_TO_TOPIC,
    BUY_BUTTON,
    RENT_BUTTON,
    build_reply_keyboard_rows,
)
from partners import PartnerType


def _type(
    slug: str,
    sort_order: int,
    label: str,
    *,
    is_menu_visible: bool = True,
) -> PartnerType:
    return PartnerType(
        slug=slug,
        is_menu_visible=is_menu_visible,
        sort_order=sort_order,
        button_label=label,
        topic_label=label.replace("\n", ""),
        intro="intro",
        fallback="fallback",
        caption_emoji="•",
        caption_cta="cta",
        button_template="{name}",
    )


def test_reply_keyboard_packs_bali_menu_two_up_with_ask_mike_alone():
    types = [
        _type("vehicle_rent", 60, "🛵 \nАренда транспорта"),
        _type("esim", 10, "📱 \neSIM"),
        _type("money_exchange", 20, "💰 \nОбмен"),
        _type("excursions", 30, "🇮🇩 \nЭкскурсии"),
        _type("visa_service", 40, "🪪 \nПомощь с Визой"),
        _type("beauty_service", 50, "💇‍♀️ \nБьюти услуги"),
    ]

    rows = build_reply_keyboard_rows(types)

    assert rows == [
        ["📱 \neSIM", "💰 \nОбмен"],
        ["🇮🇩 \nЭкскурсии", "🪪 \nПомощь с Визой"],
        ["💇‍♀️ \nБьюти услуги", "🛵 \nАренда транспорта"],
        [RENT_BUTTON, BUY_BUTTON],
        [ASK_MIKE_BUTTON],
    ]


def test_reply_keyboard_omits_hidden_partner_types():
    types = [
        _type("esim", 10, "📱 \neSIM"),
        _type("vehicle_rent", 60, "🛵 \nАренда транспорта", is_menu_visible=False),
        _type("money_exchange", 20, "💰 \nОбмен"),
    ]

    rows = build_reply_keyboard_rows(types)

    assert rows == [
        ["📱 \neSIM", "💰 \nОбмен"],
        [RENT_BUTTON, BUY_BUTTON],
        [ASK_MIKE_BUTTON],
    ]


def test_reply_keyboard_with_no_partner_types_still_ends_with_ask_mike_alone():
    rows = build_reply_keyboard_rows([])

    assert rows == [
        [RENT_BUTTON, BUY_BUTTON],
        [ASK_MIKE_BUTTON],
    ]


def test_hardcoded_buttons_map_to_topic_slugs():
    assert BUTTON_TO_TOPIC[RENT_BUTTON] == "rent"
    assert BUTTON_TO_TOPIC[BUY_BUTTON] == "buy"
    assert BUTTON_TO_TOPIC[ASK_MIKE_BUTTON] == "ask_mike"
