from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import asyncpg

from db.passwords import verify_password


def _counts(views: int, clicks: int, opened: int) -> dict:
    return {"views": views, "referral_clicks": clicks, "opened_views": opened}


@dataclass(frozen=True)
class PartnerUser:
    id: UUID
    email: str
    password_hash: str


async def get_partner_user_by_email(pool: asyncpg.Pool, email: str) -> PartnerUser | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, email, password_hash
            FROM partner_users
            WHERE email = $1
            """,
            email.lower().strip(),
        )
    if row is None:
        return None
    return PartnerUser(id=row["id"], email=row["email"], password_hash=row["password_hash"])


async def has_partner_access(
    pool: asyncpg.Pool, *, partner_user_id: UUID, partner_id: UUID
) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchval(
            """
            SELECT 1
            FROM partner_access
            WHERE partner_user_id = $1 AND partner_id = $2
            """,
            partner_user_id,
            partner_id,
        )
    return row is not None


def authenticate_partner_user(user: PartnerUser | None, password: str) -> PartnerUser | None:
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


async def get_partner_stats(pool: asyncpg.Pool, partner_id: UUID) -> dict:
    async with pool.acquire() as conn:
        all_time = await conn.fetchrow(
            """
            SELECT
                (SELECT COUNT(*) FROM partner_views WHERE partner_id = $1) AS views,
                (
                    SELECT COUNT(*)
                    FROM partner_referral_clicks c
                    JOIN partner_views v ON v.id = c.view_id
                    WHERE v.partner_id = $1
                ) AS clicks,
                (
                    SELECT COUNT(*)
                    FROM partner_views v
                    WHERE v.partner_id = $1
                      AND EXISTS (
                          SELECT 1 FROM partner_referral_clicks c WHERE c.view_id = v.id
                      )
                ) AS opened
            """,
            partner_id,
        )
        last_30 = await conn.fetchrow(
            """
            SELECT
                (
                    SELECT COUNT(*) FROM partner_views
                    WHERE partner_id = $1 AND created_at >= now() - interval '30 days'
                ) AS views,
                (
                    SELECT COUNT(*)
                    FROM partner_referral_clicks c
                    JOIN partner_views v ON v.id = c.view_id
                    WHERE v.partner_id = $1
                      AND c.created_at >= now() - interval '30 days'
                ) AS clicks,
                (
                    SELECT COUNT(*)
                    FROM partner_views v
                    WHERE v.partner_id = $1
                      AND v.created_at >= now() - interval '30 days'
                      AND EXISTS (
                          SELECT 1 FROM partner_referral_clicks c WHERE c.view_id = v.id
                      )
                ) AS opened
            """,
            partner_id,
        )
        category = await conn.fetchrow(
            """
            SELECT
                partner_type.topic_label AS phrase,
                (
                    SELECT COUNT(DISTINCT topic_event.user_id)::int
                    FROM topic_events AS topic_event
                    WHERE topic_event.topic = partner_type.slug
                ) AS all_time,
                (
                    SELECT COUNT(DISTINCT topic_event.user_id)::int
                    FROM topic_events AS topic_event
                    WHERE topic_event.topic = partner_type.slug
                      AND topic_event.created_at >= now() - interval '30 days'
                ) AS last_30_days
            FROM partners AS partner
            JOIN partner_types AS partner_type
                ON partner_type.slug = partner.type
            WHERE partner.id = $1
            """,
            partner_id,
        )
        favorites = await conn.fetchval(
            """
            SELECT COUNT(*)::int
            FROM saved_partners
            WHERE partner_id = $1
            """,
            partner_id,
        )
    if category is None:
        category_users = {"phrase": "", "all_time": 0, "last_30_days": 0}
    else:
        category_users = {
            "phrase": category["phrase"],
            "all_time": category["all_time"],
            "last_30_days": category["last_30_days"],
        }
    return {
        "partner_id": str(partner_id),
        "all_time": _counts(all_time["views"], all_time["clicks"], all_time["opened"]),
        "last_30_days": _counts(last_30["views"], last_30["clicks"], last_30["opened"]),
        "category_users": category_users,
        "favorites": favorites,
    }


async def list_accessible_partners(pool: asyncpg.Pool, partner_user_id: UUID) -> list[dict]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT p.id, p.name
            FROM partner_access a
            JOIN partners p ON p.id = a.partner_id
            WHERE a.partner_user_id = $1
            ORDER BY p.name ASC
            """,
            partner_user_id,
        )
    return [{"id": str(row["id"]), "name": row["name"]} for row in rows]
