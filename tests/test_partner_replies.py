from __future__ import annotations

from partners import PartnerType, build_partner_cards


def _partner_type(**overrides) -> PartnerType:
    base = dict(
        slug="vehicle_rent",
        is_menu_visible=True,
        sort_order=60,
        button_label="🛵 \nАренда транспорта",
        topic_label="🛵 Аренда транспорта",
        intro="Вот партнёры по аренде транспорта:",
        fallback=(
            "Пока нет доступных партнёров по аренде транспорта. "
            "Напишите Майку — подскажу, что можно сделать."
        ),
        caption_emoji="🛵",
        caption_cta="⬇️ Арендовать сейчас ⬇️",
        button_template="Арендовать у {name}",
    )
    base.update(overrides)
    return PartnerType(**base)


def test_empty_partners_returns_type_fallback_and_no_cards():
    partner_type = _partner_type()

    text, cards = build_partner_cards([], partner_type)

    assert text == partner_type.fallback
    assert cards == []
