from __future__ import annotations

import os

from partner_dashboard.offers import wrap_partners_for_channel_user
from partners import PartnerType, build_partner_list_text

CHANNEL = "telegram"


async def complete(messages: list[dict]) -> str:
    from bot import run_model

    return await run_model(messages)


async def choose_partner_type(text: str, slugs: list[str]) -> str | None:
    if not slugs:
        return None
    listed = ", ".join(slugs)
    raw = await complete(
        [
            {
                "role": "system",
                "content": (
                    "Ответь одним словом: slug типа партнёра из списка, "
                    "если вопрос про этот тип. Иначе ответь none. "
                    f"Список: {listed}"
                ),
            },
            {"role": "user", "content": text},
        ]
    )
    slug = raw.strip().split()[0].strip(".").lower() if raw.strip() else ""
    return slug if slug in slugs else None


async def write_tourist_answer(session, telegram_id: str) -> str:
    from bot import system_prompt
    from knowledge_base import format_for_prompt

    knowledge = format_for_prompt(await session.list_knowledge_base())
    history = await session.get_ai_context(CHANNEL, telegram_id)
    messages = [{"role": "system", "content": system_prompt(knowledge)}] + history
    return await complete(messages)


async def answer_with_partner_list(
    session,
    telegram_id: str,
    text: str,
    partner_type: PartnerType,
) -> str:
    await session.append_message(CHANNEL, telegram_id, role="user", content=text)
    active = await session.list_active_partners(partner_type.slug)
    wrapped = await wrap_partners_for_channel_user(
        session,
        active,
        CHANNEL,
        telegram_id,
        public_base=os.environ.get("PARTNER_OFFER_BASE_URL", ""),
    )
    reply = build_partner_list_text(partner_type, wrapped)
    await session.append_message(CHANNEL, telegram_id, role="assistant", content=reply)
    return reply
