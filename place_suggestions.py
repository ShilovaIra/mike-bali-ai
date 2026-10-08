"""Places to offer when a partner button has nobody to show."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass

from partners import PartnerType
from places import Place

DEFAULT_AREAS = ("Canggu", "Ubud", "Uluwatu")

_QUERIES = {
    "beauty_service": "beauty salon",
    "vehicle_rent": "scooter rental",
    "excursions": "tour agency",
    "money_exchange": "currency exchange",
    "visa_service": "visa agent",
    "esim": "eSIM shop",
}

_AREA_ALIASES = {
    "canggu": "Canggu",
    "чангу": "Canggu",
    "ubud": "Ubud",
    "убуд": "Ubud",
    "убуде": "Ubud",
    "убуда": "Ubud",
    "uluwatu": "Uluwatu",
    "улувату": "Uluwatu",
    "seminyak": "Seminyak",
    "семиньяк": "Seminyak",
    "семиньяке": "Seminyak",
    "семиньяка": "Seminyak",
    "семиньяку": "Seminyak",
    "sanur": "Sanur",
    "санур": "Sanur",
    "сануре": "Sanur",
    "санура": "Sanur",
    "kuta": "Kuta",
    "кута": "Kuta",
    "куте": "Kuta",
    "куту": "Kuta",
    "nusa dua": "Nusa Dua",
    "нуса дуа": "Nusa Dua",
    "нуса-дуа": "Nusa Dua",
    "jimbaran": "Jimbaran",
    "джимбаран": "Jimbaran",
    "джимбаране": "Jimbaran",
    "джимбарана": "Jimbaran",
    "pererenan": "Pererenan",
    "переренан": "Pererenan",
    "переренане": "Pererenan",
    "переренана": "Pererenan",
    "berawa": "Berawa",
    "берава": "Berawa",
    "бераве": "Berawa",
    "беравы": "Berawa",
    "amed": "Amed",
    "амед": "Amed",
    "амеде": "Amed",
    "амеда": "Amed",
    "lovina": "Lovina",
    "ловина": "Lovina",
    "ловине": "Lovina",
    "ловины": "Lovina",
}

_FILLERS = frozenset(
    {"а", "в", "во", "на", "по", "пожалуйста", "давай", "покажи", "или"}
)


def requested_area(text: str) -> str | None:
    """The area a short reply is asking for, in the English name we search.

    A longer message that merely mentions an area is not a request. Two areas
    and nothing else use the first one named.
    """
    cleaned = re.sub(r"[^\w\s-]", " ", text.casefold())
    tokens = [token for token in cleaned.split() if token not in _FILLERS]
    found: list[str] = []
    index = 0
    while index < len(tokens):
        bigram = " ".join(tokens[index : index + 2])
        if bigram in _AREA_ALIASES:
            found.append(_AREA_ALIASES[bigram])
            index += 2
            continue
        area = _AREA_ALIASES.get(tokens[index])
        if area is None:
            return None
        found.append(area)
        index += 1
    return found[0] if found else None


@dataclass(frozen=True)
class SuggestedPlace:
    name: str
    area: str
    maps_url: str
    rating: float | None = None


@dataclass(frozen=True)
class PlaceSuggestions:
    places: tuple[SuggestedPlace, ...]
    text: str | None = None


Search = Callable[[str], Awaitable[Sequence[Place]]]
WriteIntro = Callable[[str], Awaitable[str]]
_LINK = re.compile(r"https?://\S+")


def _plain_intro(text: str) -> str:
    return _LINK.sub("", text).strip()


async def build_place_reply(
    partner_type: PartnerType,
    search: Search,
    write_intro: WriteIntro,
    *,
    area: str | None = None,
) -> str:
    """Intro from Mike plus Places links, or a finished line when there is nothing to introduce."""
    suggestions = await suggest_places(partner_type, search, area=area)
    if suggestions.text is not None:
        return suggestions.text
    intro = _plain_intro(await write_intro(intro_request(partner_type, suggestions)))
    return compose_reply(intro, suggestions)


def intro_request(partner_type: PartnerType, suggestions: PlaceSuggestions) -> str:
    """What Mike may say. Place names and links stay out of the model prompt."""
    areas = ", ".join(place.area for place in suggestions.places)
    return (
        f"Пользователь нажал «{partner_type.topic_label}». "
        f"Подборка готова по районам: {areas}. "
        "Напиши одно-два живых предложения на русском. "
        "Не перечисляй заведения, не давай ссылки и не придумывай места."
    )


def compose_reply(intro: str, suggestions: PlaceSuggestions) -> str:
    """Mike's intro, then each place with the area we searched and Google's link.

    A finished line (fallback or nothing found) is the whole reply.
    """
    if suggestions.text is not None:
        return suggestions.text
    blocks = [intro.strip()]
    for place in suggestions.places:
        details = place.area if place.rating is None else f"{place.area} · {place.rating}"
        blocks.append(f"{place.name}\n{details}\n{place.maps_url}")
    return "\n\n".join(blocks)


def active_suggestion_slug(
    messages: Sequence[Mapping],
    menu_labels: set[str],
) -> str | None:
    """Empty-partner button still in effect, until another menu button."""
    for message in reversed(messages):
        metadata = message.get("metadata") or {}
        slug = metadata.get("place_suggestion_slug")
        if message.get("role") == "user" and message.get("content") in menu_labels:
            return slug
        if slug:
            return slug
    return None


def _phrase(partner_type: PartnerType) -> str:
    return _QUERIES.get(partner_type.slug) or partner_type.slug.replace("_", " ")


def model_search_request(partner_type: PartnerType, *, area: str | None = None) -> str:
    """Ask Mike the way chat does when there is no Places API key.

    The link is a Google Maps search URL, which resolves without a Places subscription.
    """
    phrase = _phrase(partner_type)
    if area:
        where = f"одно хорошее место в районе {area}"
    else:
        where = "по одному хорошему месту в районах Canggu, Ubud и Uluwatu"
    return (
        f"Пользователь нажал «{partner_type.topic_label}». "
        f"Подбери {where} по запросу «{phrase}» на Бали. "
        "Для каждого места напиши название и ссылку Google Карт строго по шаблону "
        "https://www.google.com/maps/search/?api=1&query=НАЗВАНИЕ+РАЙОН+Bali. "
        "Название латиницей, пробелы замени на +. "
        "Не пиши, что партнёров нет, и не проси написать тебе."
    )


async def suggest_places(
    partner_type: PartnerType,
    search: Search,
    *,
    area: str | None = None,
) -> PlaceSuggestions:
    areas = (area,) if area else DEFAULT_AREAS
    phrase = _phrase(partner_type)
    places: list[SuggestedPlace] = []
    for area_name in areas:
        found = await search(f"{phrase} {area_name}")
        if not found:
            continue
        top = found[0]
        places.append(
            SuggestedPlace(
                name=top.name,
                area=area_name,
                maps_url=top.maps_url,
                rating=top.rating,
            )
        )
    if not places:
        if area:
            return PlaceSuggestions(places=(), text=f"В {area} ничего не нашлось.")
        return PlaceSuggestions(places=(), text=partner_type.fallback)
    return PlaceSuggestions(places=tuple(places))
