"""Format bot analytics for the admin /stats command."""

from __future__ import annotations

from collections.abc import Sequence

from db.store import BotStats, TopicCount
from partners import PartnerType
from topics import TOPIC_LABELS, TOPIC_ORDER

_SOURCE_LABELS = {
    "unknown": "Неизвестно",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "tgtrack": "TgTrack",
}

_MAX_SOURCE_LINES = 20


def _source_label(source: str) -> str:
    if source in _SOURCE_LABELS:
        return _SOURCE_LABELS[source]
    return source[:1].upper() + source[1:] if source else source


def _canonical_source(source: str) -> str:
    if source.lower().startswith("tgtrack"):
        return "tgtrack"
    return source


def collapse_user_sources(users_by_first_source: dict[str, int]) -> dict[str, int]:
    collapsed: dict[str, int] = {}
    for source, count in users_by_first_source.items():
        key = _canonical_source(source)
        collapsed[key] = collapsed.get(key, 0) + count
    return collapsed


def _leads_label(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} заявка"
    if 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return f"{count} заявки"
    return f"{count} заявок"


def _format_topic_line(label: str, count: TopicCount) -> str:
    return f"  {label}: {count.unique_users} users ({count.taps} taps)"


def _topic_catalog(
    partner_types: Sequence[PartnerType],
) -> tuple[tuple[str, ...], dict[str, str]]:
    partner_labels = {t.slug: t.topic_label for t in partner_types}
    labels = {**TOPIC_LABELS, **partner_labels}
    partner_slugs = {t.slug for t in partner_types}
    order = tuple(t for t in TOPIC_ORDER if t not in partner_slugs) + tuple(
        t.slug for t in sorted(partner_types, key=lambda t: (t.sort_order, t.slug))
    )
    return order, labels


def labeled_topic_rows(
    topics: dict[str, TopicCount],
    partner_types: Sequence[PartnerType],
) -> list[dict[str, object]]:
    _order, labels = _topic_catalog(partner_types)
    return [
        {
            "slug": slug,
            "label": labels.get(slug, slug),
            "unique_users": count.unique_users,
            "taps": count.taps,
        }
        for slug, count in topics.items()
    ]


def _format_topic_section(
    title: str,
    topics: dict[str, TopicCount],
    *,
    topic_order: tuple[str, ...],
    topic_labels: dict[str, str],
) -> list[str]:
    lines = [title]
    known = set(topic_order)
    extra = tuple(sorted(t for t in topics if t not in known))
    ranked = sorted(
        topic_order + extra,
        key=lambda topic: (
            -topics.get(topic, TopicCount(0, 0)).unique_users,
            -topics.get(topic, TopicCount(0, 0)).taps,
            topic_labels.get(topic, topic),
        ),
    )
    for topic in ranked:
        count = topics.get(topic, TopicCount(0, 0))
        if count.taps == 0:
            continue
        lines.append(_format_topic_line(topic_labels.get(topic, topic), count))
    if len(lines) == 1:
        lines.append("  —")
    return lines


def _format_source_section(users_by_first_source: dict[str, int]) -> list[str]:
    lines = ["Источники:"]
    ranked = sorted(
        collapse_user_sources(users_by_first_source).items(),
        key=lambda item: (-item[1], item[0]),
    )
    shown = ranked[:_MAX_SOURCE_LINES]
    rest = ranked[_MAX_SOURCE_LINES:]
    for source, count in shown:
        lines.append(f"  {_source_label(source)}: {count}")
    if rest:
        lines.append(f"  Другие: {sum(count for _, count in rest)}")
    if len(lines) == 1:
        lines.append("  —")
    return lines


def format_bot_stats(
    stats: BotStats,
    *,
    partner_types: Sequence[PartnerType] = (),
) -> str:
    topic_order, topic_labels = _topic_catalog(partner_types)
    lines = [
        "📊 Статистика бота",
        "",
        "Пользователи:",
        f"  Всего: {stats.total_users}",
        f"  Новые сегодня: {stats.new_users_today}",
        f"  Активны сегодня: {stats.active_today}",
        "",
        *_format_source_section(stats.users_by_first_source),
        "",
        "За 7 дней:",
        f"  Новые пользователи: {stats.new_users_7d}",
        "",
        *_format_topic_section(
            "Темы (7 дней):",
            stats.topics_7d,
            topic_order=topic_order,
            topic_labels=topic_labels,
        ),
        "",
        *_format_topic_section(
            "Темы (всё время):",
            stats.topics_all_time,
            topic_order=topic_order,
            topic_labels=topic_labels,
        ),
        "",
        "Недвижимость:",
        f"  За 7 дней: {_leads_label(stats.leads_7d)}",
        f"  Всё время: {_leads_label(stats.leads_all_time)}",
    ]
    return "\n".join(lines)
