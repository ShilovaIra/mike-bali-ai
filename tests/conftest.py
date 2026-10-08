from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
import pytest_asyncio

from db.store import SessionStore

pytest_plugins = ("pytest_asyncio",)


def database_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")


requires_db = pytest.mark.skipif(
    not database_url(),
    reason="Set TEST_DATABASE_URL or DATABASE_URL to run database tests",
)


TRUNCATE_SQL = """
TRUNCATE TABLE
    follow_up_jobs,
    webhook_events,
    leads,
    topic_events,
    messages,
    conversations,
    identities,
    users,
    partner_referral_clicks,
    partner_views,
    partner_access,
    partner_users,
    knowledge_base,
    partners,
    admin_users
RESTART IDENTITY CASCADE
"""


@pytest_asyncio.fixture
async def store() -> SessionStore:
    url = database_url()
    assert url is not None
    session_store = await SessionStore.create(url)
    async with session_store.pool.acquire() as conn:
        await conn.execute(TRUNCATE_SQL)
        await conn.execute(
            """
            DELETE FROM partner_types
            WHERE slug NOT IN (
                'esim',
                'money_exchange',
                'excursions',
                'visa_service',
                'beauty_service',
                'vehicle_rent'
            )
            """
        )
    yield session_store
    await session_store.close()
