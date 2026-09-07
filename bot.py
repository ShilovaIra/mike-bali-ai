from __future__ import annotations

import os
from collections import defaultdict

import requests
from dotenv import load_dotenv
from openai import OpenAI
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from buttons import build_reply_keyboard_rows

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MIKE_PROMPT = """
Ты Майк — дружелюбный AI-гид по Бали и помощник Bali ProMax.

Говори на русском языке коротко, понятно и живо.

Помогай туристам с пляжами, ресторанами, маршрутами, экскурсиями, транспортом и недвижимостью.

Если человек интересуется недвижимостью, мягко выясняй:
1. Покупка или аренда?
2. Район
3. Бюджет
4. Количество спален
5. Когда планирует покупку или аренду
6. Имя
7. WhatsApp или Telegram для связи

Не задавай всё сразу. Задавай по одному-два вопроса.
Если пользователь уже что-то сказал раньше — учитывай это и не спрашивай повторно.

Когда собрал достаточно данных для заявки, напиши в ответе фразу:
ЗАЯВКА_ГОТОВА

Если получаешь геолокацию, не выдумывай район сам. Используй только район и адрес, которые переданы в сообщении.
"""

sessions: dict[str, list[dict]] = defaultdict(list)
client = OpenAI(api_key=OPENAI_API_KEY)


def parse_admin_ids(raw: str | None) -> frozenset[str]:
    """Comma-separated Telegram user/chat ids, e.g. '111,222'."""
    if not raw:
        return frozenset()
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


ADMIN_IDS = parse_admin_ids(os.getenv("ADMIN_CHAT_ID"))


def reply_markup() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(label) for label in row]
        for row in build_reply_keyboard_rows()
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=False)


def telegram_id(update: Update) -> str:
    return str(update.effective_user.id)


def get_location_name(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "accept-language": "ru",
        }
        headers = {"User-Agent": "MikeBaliAI/1.0"}

        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        address = data.get("address", {})

        area = (
            address.get("suburb")
            or address.get("village")
            or address.get("town")
            or address.get("city")
            or address.get("municipality")
            or address.get("county")
            or "район не определён"
        )

        full_address = data.get("display_name", "адрес не определён")
        return area, full_address

    except Exception as e:
        return "район не определён", f"Ошибка определения адреса: {e}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tid = telegram_id(update)
    sessions[tid] = []

    await update.message.reply_text(
        "Привет! Я Майк — AI-гид по Бали.\n\n"
        "Могу помочь с пляжами, ресторанами, маршрутами, районами и недвижимостью.",
        reply_markup=reply_markup(),
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID:\n{update.effective_chat.id}")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessions[telegram_id(update)] = []
    await update.message.reply_text(
        "Память диалога очищена. Начинаем заново 👌",
        reply_markup=reply_markup(),
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location

    if not location:
        await update.message.reply_text(
            "Не получил геопозицию. Нажми «Что рядом» и разреши отправку локации.",
            reply_markup=reply_markup(),
        )
        return

    lat = location.latitude
    lon = location.longitude
    area, full_address = get_location_name(lat, lon)

    user_text = f"""
Пользователь отправил геолокацию.

Координаты:
Широта: {lat}
Долгота: {lon}

Определённый район:
{area}

Адрес по карте:
{full_address}

Подскажи, что находится рядом.
Не угадывай район сам.
Используй только определённый район и адрес.
Дай короткий ответ: где человек находится, что рядом посмотреть, где поесть и куда съездить.
"""
    await ask_openai(update, context, user_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ask_openai(update, context, update.message.text)


async def ask_openai(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_text: str,
):
    tid = telegram_id(update)
    history = sessions[tid]
    history.append({"role": "user", "content": user_text})

    await update.message.reply_text("Думаю как местный 😎")

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{"role": "system", "content": MIKE_PROMPT}] + history,
        )
        answer = response.output_text

        lead_ready = "ЗАЯВКА_ГОТОВА" in answer
        answer = answer.replace("ЗАЯВКА_ГОТОВА", "").strip()
        history.append({"role": "assistant", "content": answer})

        if lead_ready:
            await send_lead_to_admin(update, context)

    except Exception as e:
        answer = f"Ошибка OpenAI:\n{e}"

    await update.message.reply_text(answer, reply_markup=reply_markup())


async def send_lead_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_IDS:
        return

    user = update.effective_user
    tid = telegram_id(update)
    username = f"@{user.username}" if user.username else "не указан"

    dialogue = ""
    for message in sessions[tid]:
        role = "Клиент" if message["role"] == "user" else "Майк"
        dialogue += f"{role}: {message['content']}\n\n"

    lead_text = (
        "🏠 Новая заявка на недвижимость\n\n"
        f"Имя в Telegram: {user.first_name or 'не указано'}\n"
        f"Username: {username}\n"
        f"Telegram ID: {tid}\n\n"
        "Диалог:\n"
        f"{dialogue}"
    )

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin_id, text=lead_text)


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Ошибка: не найден TELEGRAM_BOT_TOKEN в файле .env")
        return

    if not OPENAI_API_KEY:
        print("Ошибка: не найден OPENAI_API_KEY в файле .env")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Mike Bali AI запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
