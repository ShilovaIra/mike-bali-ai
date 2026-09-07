"""Reply keyboard button labels for the Telegram bot.

Emoji and caption are separated by \\n so many Telegram clients stack them.
This is still plain text, not real icon layout.
"""

from __future__ import annotations

ESIM_BUTTON = "📱 \neSIM"
EXCHANGE_BUTTON = "💰 \nОбмен"
TOURS_BUTTON = "🇮🇩 \nЭкскурсии"
VISA_BUTTON = "🪪 \nПомощь с Визой"
BEAUTY_BUTTON = "💇‍♀️ \nБьюти услуги"
RENT_BUTTON = "🏡 \nАренда недвижимости"
BUY_BUTTON = "🏡 \nПокупка недвижимости"
ASK_MIKE_BUTTON = "💬 \nСпросить Майка"

MENU_BUTTONS = (
    ESIM_BUTTON,
    EXCHANGE_BUTTON,
    TOURS_BUTTON,
    VISA_BUTTON,
    BEAUTY_BUTTON,
    RENT_BUTTON,
    BUY_BUTTON,
)

BUTTON_TO_TOPIC = {
    ESIM_BUTTON: "esim",
    EXCHANGE_BUTTON: "exchange",
    TOURS_BUTTON: "tours",
    VISA_BUTTON: "visa",
    BEAUTY_BUTTON: "beauty",
    RENT_BUTTON: "rent",
    BUY_BUTTON: "buy",
    ASK_MIKE_BUTTON: "ask_mike",
}


def build_reply_keyboard_rows() -> list[list[str]]:
    """Pack the main menu two buttons per row; Ask Mike always alone last."""
    rows = [list(MENU_BUTTONS[i : i + 2]) for i in range(0, len(MENU_BUTTONS), 2)]
    rows.append([ASK_MIKE_BUTTON])
    return rows
