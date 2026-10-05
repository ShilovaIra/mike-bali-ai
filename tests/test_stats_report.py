from db.store import BotStats, TopicCount
from partners import PartnerType
from stats_report import format_bot_stats


def _stats(**overrides) -> BotStats:
    defaults = dict(
        total_users=10,
        new_users_today=1,
        active_today=2,
        new_users_7d=3,
        topics_all_time={},
        topics_7d={},
        leads_all_time=0,
        leads_7d=0,
        users_by_first_source={},
    )
    defaults.update(overrides)
    return BotStats(**defaults)


def test_format_bot_stats_lists_rent_and_buy_as_separate_topics():
    stats = _stats(
        topics_all_time={
            "rent": TopicCount(unique_users=8, taps=9),
            "buy": TopicCount(unique_users=3, taps=4),
        },
        topics_7d={
            "rent": TopicCount(unique_users=5, taps=6),
            "buy": TopicCount(unique_users=2, taps=3),
        },
    )

    text = format_bot_stats(stats)

    assert "🏡 Аренда недвижимости: 5 users (6 taps)" in text
    assert "🏡 Покупка недвижимости: 2 users (3 taps)" in text
    assert "🏡 Аренда недвижимости: 8 users (9 taps)" in text
    assert "🏡 Покупка недвижимости: 3 users (4 taps)" in text


def test_format_bot_stats_shows_leads_only_under_real_estate():
    stats = _stats(
        topics_7d={"rent": TopicCount(unique_users=5, taps=6)},
        leads_all_time=8,
        leads_7d=2,
    )

    text = format_bot_stats(stats)
    real_estate = text.split("Недвижимость:")[1]

    assert "За 7 дней: 2 заявки" in real_estate
    assert "Всё время: 8 заявок" in real_estate
    assert "taps" not in real_estate
    assert "→" not in real_estate


def test_format_bot_stats_places_labeled_sources_between_users_and_7d():
    stats = _stats(
        total_users=100,
        new_users_today=5,
        active_today=12,
        new_users_7d=20,
        users_by_first_source={"instagram": 3, "unknown": 97},
    )

    text = format_bot_stats(stats)
    users_idx = text.index("Активны сегодня:")
    sources_idx = text.index("Источники:")
    week_idx = text.index("За 7 дней:")

    assert users_idx < sources_idx < week_idx
    assert "Instagram: 3" in text
    assert "Неизвестно: 97" in text
    assert "Новые сегодня: 5" in text
    assert "Новые пользователи: 20" in text


def test_format_bot_stats_uses_partner_type_topic_labels():
    stats = _stats(
        topics_all_time={
            "vehicle_rent": TopicCount(unique_users=4, taps=7),
        },
        topics_7d={
            "vehicle_rent": TopicCount(unique_users=2, taps=3),
        },
    )
    partner_types = [
        PartnerType(
            slug="vehicle_rent",
            is_menu_visible=True,
            sort_order=60,
            button_label="🛵 \nАренда транспорта",
            topic_label="🛵 Аренда транспорта",
            intro="i",
            fallback="f",
            caption_emoji="🛵",
            caption_cta="c",
            button_template="{name}",
        )
    ]

    text = format_bot_stats(stats, partner_types=partner_types)

    assert "🛵 Аренда транспорта: 2 users (3 taps)" in text
    assert "🛵 Аренда транспорта: 4 users (7 taps)" in text


def test_format_bot_stats_fits_telegram_limit_when_first_sources_are_unique_click_ids():
    sources = {
        "instagram": 22,
        "unknown": 22,
        "instagram_stories": 7,
        "telegram_channel": 6,
        "tiktok": 5,
        "restaurant_qr": 2,
    }
    for i in range(200):
        sources[f"TgTrack-PJ{i:016x}"] = 1

    text = format_bot_stats(_stats(users_by_first_source=sources))

    assert len(text) <= 4096
    assert "Instagram: 22" in text
    assert "Неизвестно: 22" in text
    assert "TgTrack: 200" in text
    assert "TgTrack-PJ" not in text
    assert "Недвижимость:" in text


def test_format_bot_stats_fits_telegram_limit_when_many_distinct_campaign_sources():
    sources = {f"campaign_{i:04d}": 1 for i in range(80)}

    text = format_bot_stats(_stats(users_by_first_source=sources))

    assert len(text) <= 4096
    assert "Другие:" in text
    assert text.count("\n  Campaign_") <= 20
