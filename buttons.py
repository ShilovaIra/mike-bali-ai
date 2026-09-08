"""Reply keyboard button labels for the Telegram bot.

Emoji and caption are separated by \\n so many Telegram clients stack them.
This is still plain text, not real icon layout.
"""

from __future__ import annotations

from collections.abc import Sequence

from partners import PartnerType
from topics import TOPIC_ASK_MIKE, TOPIC_BUY, TOPIC_RENT

RENT_BUTTON = "🏡 \nАренда недвижимости"
BUY_BUTTON = "🏡 \nПокупка недвижимости"
ASK_MIKE_BUTTON = "💬 \nСпросить Майка"

BUTTON_TO_TOPIC = {
    RENT_BUTTON: TOPIC_RENT,
    BUY_BUTTON: TOPIC_BUY,
    ASK_MIKE_BUTTON: TOPIC_ASK_MIKE,
}


def build_reply_keyboard_rows(
    partner_types: Sequence[PartnerType],
) -> list[list[str]]:
    """Pack partner types 2-up, then real estate; Ask Mike always alone last."""
    ordered_partners = sorted(
        (t for t in partner_types if t.is_menu_visible),
        key=lambda t: (t.sort_order, t.slug),
    )
    before_ask_mike = [
        *[t.button_label for t in ordered_partners],
        RENT_BUTTON,
        BUY_BUTTON,
    ]
    rows: list[list[str]] = [
        before_ask_mike[i : i + 2] for i in range(0, len(before_ask_mike), 2)
    ]
    rows.append([ASK_MIKE_BUTTON])
    return rows
