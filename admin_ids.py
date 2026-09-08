"""Parse and check Telegram admin ids from ADMIN_CHAT_ID."""

from __future__ import annotations


def parse_admin_ids(raw: str | None) -> frozenset[str]:
    """Comma-separated Telegram user/chat ids, e.g. '111,222'."""
    if not raw:
        return frozenset()
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


def sender_is_admin(
    *,
    user_id: str,
    chat_id: str,
    admin_ids: frozenset[str],
) -> bool:
    if not admin_ids:
        return False
    return user_id in admin_ids or chat_id in admin_ids
