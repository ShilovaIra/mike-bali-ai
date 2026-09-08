from tests.conftest import requires_db


@requires_db
async def test_record_topic_event_counts_unique_users_and_taps_all_time(store):
    await store.start_conversation("telegram", "800", source="unknown")
    await store.record_topic_event("telegram", "800", topic="rent")
    await store.record_topic_event("telegram", "800", topic="rent")

    await store.start_conversation("telegram", "801", source="unknown")
    await store.record_topic_event("telegram", "801", topic="rent")

    stats = await store.get_bot_stats()

    rent = stats.topics_all_time["rent"]
    assert rent.unique_users == 2
    assert rent.taps == 3


@requires_db
async def test_get_bot_stats_excludes_topic_events_older_than_7_days(store):
    await store.start_conversation("telegram", "802", source="unknown")
    await store.record_topic_event("telegram", "802", topic="rent")

    async with store.pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE topic_events
            SET created_at = now() - interval '10 days'
            WHERE topic = 'rent'
            """
        )

    await store.start_conversation("telegram", "803", source="unknown")
    await store.record_topic_event("telegram", "803", topic="esim")

    stats = await store.get_bot_stats()

    assert "rent" not in stats.topics_7d
    assert stats.topics_7d["esim"].unique_users == 1
    assert stats.topics_all_time["rent"].unique_users == 1
    assert stats.topics_all_time["esim"].unique_users == 1


@requires_db
async def test_get_bot_stats_counts_new_users_today_and_last_7_days(store):
    await store.start_conversation("telegram", "804", source="unknown")
    await store.start_conversation("telegram", "805", source="unknown")

    stats = await store.get_bot_stats()

    assert stats.new_users_today == 2
    assert stats.new_users_7d == 2
    assert stats.total_users == 2


@requires_db
async def test_get_bot_stats_counts_leads_all_time_and_last_7_days(store):
    await store.start_conversation("telegram", "806", source="unknown")
    await store.create_lead("telegram", "806", snapshot={"name": "Anna"})

    stats = await store.get_bot_stats()

    assert stats.leads_all_time == 1
    assert stats.leads_7d == 1


@requires_db
async def test_get_bot_stats_groups_users_by_first_source(store):
    await store.start_conversation("telegram", "807", source="instagram")
    await store.start_conversation("telegram", "808", source="instagram")
    await store.start_conversation("telegram", "809", source="unknown")

    stats = await store.get_bot_stats()

    assert stats.users_by_first_source == {"instagram": 2, "unknown": 1}


@requires_db
async def test_inbound_stamp_counts_as_active_today(store):
    before = (await store.get_bot_stats()).active_today
    await store.start_conversation("telegram", "8001")
    await store.record_inbound("telegram", "8001")
    after = (await store.get_bot_stats()).active_today
    assert after == before + 1


@requires_db
async def test_topic_tap_counts_as_active_today(store):
    before = (await store.get_bot_stats()).active_today
    await store.record_topic_event("telegram", "8002", topic="rent")
    after = (await store.get_bot_stats()).active_today
    assert after == before + 1


@requires_db
async def test_user_message_counts_as_active_today(store):
    before = (await store.get_bot_stats()).active_today
    await store.append_message("telegram", "8003", role="user", content="привет")
    after = (await store.get_bot_stats()).active_today
    assert after == before + 1


@requires_db
async def test_same_user_inbound_and_message_count_once_as_active_today(store):
    before = (await store.get_bot_stats()).active_today
    await store.start_conversation("telegram", "8004")
    await store.record_inbound("telegram", "8004")
    await store.append_message("telegram", "8004", role="user", content="привет")
    after = (await store.get_bot_stats()).active_today
    assert after == before + 1
