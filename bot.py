from __future__ import annotations

import os

import requests
from dotenv import load_dotenv
from openai import OpenAI
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from admin_ids import parse_admin_ids, sender_is_admin
from buttons import BUTTON_TO_TOPIC, build_reply_keyboard_rows
from db.store import SessionStore
from db.url import resolve_database_url
from partners import PartnerType, build_partner_cards, resolve_logo_path
from stats_report import format_bot_stats

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = resolve_database_url()

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

CHANNEL = "telegram"
client = OpenAI(api_key=OPENAI_API_KEY)
store: SessionStore | None = None

ADMIN_IDS = parse_admin_ids(os.getenv("ADMIN_CHAT_ID"))


def require_store() -> SessionStore:
    if store is None:
        raise RuntimeError("SessionStore is not initialized")
    return store


async def build_reply_markup() -> ReplyKeyboardMarkup:
    partner_types = await require_store().list_partner_types()
    keyboard = [
        [KeyboardButton(label) for label in row]
        for row in build_reply_keyboard_rows(partner_types)
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
    source = context.args[0] if context.args else "unknown"
    tid = telegram_id(update)
    await require_store().start_conversation(CHANNEL, tid, source=source)
    await require_store().record_inbound(CHANNEL, tid)

    await update.message.reply_text(
        "Привет! Я Майк - AI-гид по Бали.\n\n"
        "Могу помочь с покупкой eSIM, обменом валюты, оформлением визы, арендой транспорта, поиском бьюти-услуг и интересных экскурсий, а также с арендой и покупкой недвижимости. Просто отправь вопрос в чат или воспользуйся кнопками из моего меню ⬇️",
        reply_markup=await build_reply_markup(),
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID:\n{update.effective_chat.id}")


def is_admin(update: Update) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    return sender_is_admin(
        user_id=str(user.id) if user else "",
        chat_id=str(chat.id) if chat else "",
        admin_ids=ADMIN_IDS,
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    session = require_store()
    bot_stats = await session.get_bot_stats()
    partner_types = await session.list_partner_types()
    await update.message.reply_text(
        format_bot_stats(bot_stats, partner_types=partner_types)
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tid = telegram_id(update)
    await require_store().reset_conversation(CHANNEL, tid)
    await require_store().record_inbound(CHANNEL, tid)
    await update.message.reply_text(
        "Память диалога очищена. Начинаем заново 👌",
        reply_markup=await build_reply_markup(),
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location

    if not location:
        await update.message.reply_text(
            "Не получил геопозицию. Отправь локацию ещё раз.",
            reply_markup=await build_reply_markup(),
        )
        return

    tid = telegram_id(update)
    await require_store().record_inbound(CHANNEL, tid)

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
    metadata = {
        "message_type": "location",
        "lat": lat,
        "lon": lon,
        "area": area,
        "full_address": full_address,
    }
    await ask_openai(update, context, user_text, metadata=metadata)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    session = require_store()
    partner_types = await session.list_partner_types()
    partner_by_label = {t.button_label: t for t in partner_types}
    tid = telegram_id(update)

    topic = BUTTON_TO_TOPIC.get(user_text)
    partner_type = partner_by_label.get(user_text)
    if partner_type is not None:
        topic = partner_type.slug
    await session.record_inbound(CHANNEL, tid)
    if topic:
        await session.record_topic_event(CHANNEL, tid, topic=topic)
    if partner_type is not None:
        await handle_partner_topic(update, partner_type)
        return
    await ask_openai(update, context, user_text)


async def handle_partner_topic(update: Update, partner_type: PartnerType):
    session = require_store()
    partners = await session.list_active_partners(partner_type.slug)
    intro_or_fallback, cards = build_partner_cards(partners, partner_type)

    await update.message.reply_text(
        intro_or_fallback,
        reply_markup=await build_reply_markup(),
    )
    if not cards:
        return

    for card in cards:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(card.button_text, url=card.referral_url)]]
        )
        logo = resolve_logo_path(card.logo_path)
        if logo is not None:
            with logo.open("rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=card.caption_html,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
        else:
            await update.message.reply_text(
                card.caption_html,
                parse_mode="HTML",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )


async def ask_openai(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_text: str,
    *,
    metadata: dict | None = None,
):
    tid = telegram_id(update)
    session = require_store()
    await session.append_message(
        CHANNEL,
        tid,
        role="user",
        content=user_text,
        metadata=metadata,
    )

    history = await session.get_ai_context(CHANNEL, tid)

    await update.message.reply_text("Думаю как местный 😎")

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{"role": "system", "content": MIKE_PROMPT}] + history,
        )
        answer = response.output_text

        lead_ready = "ЗАЯВКА_ГОТОВА" in answer
        answer = answer.replace("ЗАЯВКА_ГОТОВА", "").strip()
        await session.append_message(CHANNEL, tid, role="assistant", content=answer)

        if lead_ready:
            lead = await session.create_lead(
                CHANNEL,
                tid,
                snapshot=await build_lead_snapshot(update),
            )
            if lead and lead.created:
                await send_lead_to_admin(update, context, lead.source)

    except Exception as e:
        answer = f"Ошибка OpenAI:\n{e}"

    await update.message.reply_text(answer, reply_markup=await build_reply_markup())


async def build_lead_snapshot(update: Update) -> dict:
    tid = telegram_id(update)
    user = update.effective_user
    history = await require_store().get_ai_context(CHANNEL, tid, limit=16)
    username = f"@{user.username}" if user.username else None

    return {
        "telegram_id": tid,
        "telegram_username": username,
        "telegram_first_name": user.first_name,
        "dialogue": history,
    }


async def send_lead_to_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    source: str,
):
    if not ADMIN_IDS:
        return

    user = update.effective_user
    tid = telegram_id(update)
    history = await require_store().get_ai_context(CHANNEL, tid, limit=16)

    dialogue = ""
    for message in history:
        role = "Клиент" if message["role"] == "user" else "Майк"
        dialogue += f"{role}: {message['content']}\n\n"

    username = f"@{user.username}" if user.username else "не указан"

    lead_text = (
        "🏠 Новая заявка на недвижимость\n\n"
        f"Источник: {source}\n\n"
        f"Имя в Telegram: {user.first_name or 'не указано'}\n"
        f"Username: {username}\n"
        f"Telegram ID: {tid}\n\n"
        "Диалог:\n"
        f"{dialogue}"
    )

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin_id, text=lead_text)


async def post_init(application: Application) -> None:
    global store
    store = await SessionStore.create(DATABASE_URL)


async def post_shutdown(application: Application) -> None:
    global store
    if store is not None:
        await store.close()
        store = None


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Ошибка: не найден TELEGRAM_BOT_TOKEN в файле .env")
        return

    if not OPENAI_API_KEY:
        print("Ошибка: не найден OPENAI_API_KEY в файле .env")
        return

    if not DATABASE_URL:
        print("Ошибка: не найден DATABASE_URL в файле .env")
        return

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Mike Bali AI запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
