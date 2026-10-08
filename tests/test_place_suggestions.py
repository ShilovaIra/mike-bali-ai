"""An empty partner button suggests real places instead of the stored fallback."""

from __future__ import annotations

import pytest

from partners import PartnerType
from places import Place
from place_suggestions import (
    PlaceSuggestions,
    SuggestedPlace,
    active_suggestion_slug,
    build_place_reply,
    compose_reply,
    intro_request,
    model_search_request,
    requested_area,
    suggest_places,
)


def _partner_type(**overrides) -> PartnerType:
    base = dict(
        slug="beauty_service",
        is_menu_visible=True,
        sort_order=50,
        button_label="💇‍♀️ \nБьюти услуги",
        topic_label="💇‍♀️ Бьюти услуги",
        intro="Вот партнёры по бьюти-услугам:",
        fallback=(
            "Пока нет доступных партнёров по бьюти-услугам. "
            "Напишите Майку — подскажу, что можно сделать."
        ),
        caption_emoji="💇‍♀️",
        caption_cta="⬇️ Записаться ⬇️",
        button_template="Записаться к {name}",
    )
    base.update(overrides)
    return PartnerType(**base)


def _place(area: str, *, rating: float = 4.8) -> Place:
    return Place(
        name=f"Salon in {area}",
        address="Pecatu",
        maps_url=f"https://maps.google.com/?cid={area}",
        place_id=area,
        rating=rating,
    )


async def test_empty_beauty_button_suggests_top_place_in_each_default_area():
    async def search(query: str):
        area = query.removeprefix("beauty salon ")
        return [_place(area), _place("ignored", rating=3.0)]

    result = await suggest_places(_partner_type(), search)

    assert [(place.area, place.name, place.maps_url, place.rating) for place in result.places] == [
        ("Canggu", "Salon in Canggu", "https://maps.google.com/?cid=Canggu", 4.8),
        ("Ubud", "Salon in Ubud", "https://maps.google.com/?cid=Ubud", 4.8),
        ("Uluwatu", "Salon in Uluwatu", "https://maps.google.com/?cid=Uluwatu", 4.8),
    ]


async def test_missing_area_is_left_out_of_the_suggestions():
    async def search(query: str):
        area = query.removeprefix("beauty salon ")
        if area == "Ubud":
            return []
        return [_place(area)]

    result = await suggest_places(_partner_type(), search)

    assert [place.area for place in result.places] == ["Canggu", "Uluwatu"]


async def test_no_places_returns_the_stored_fallback_without_an_intro():
    async def search(query: str):
        return []

    result = await suggest_places(_partner_type(), search)

    assert result.places == ()
    assert result.text == _partner_type().fallback


async def test_named_area_suggests_one_place_there():
    seen = []

    async def search(query: str):
        seen.append(query)
        return [_place("Seminyak")]

    result = await suggest_places(_partner_type(), search, area="Seminyak")

    assert seen == ["beauty salon Seminyak"]
    assert [(place.area, place.maps_url) for place in result.places] == [
        ("Seminyak", "https://maps.google.com/?cid=Seminyak")
    ]
    assert result.text is None


async def test_named_area_with_no_place_says_nothing_was_found():
    async def search(query: str):
        return []

    result = await suggest_places(_partner_type(), search, area="Seminyak")

    assert result.places == ()
    assert result.text == "В Seminyak ничего не нашлось."


def test_short_area_reply_names_that_area():
    assert requested_area("а в Семиньяке?") == "Seminyak"


def test_longer_message_is_not_an_area_request():
    assert requested_area("расскажи про храмы в Семиньяке") is None


def test_two_areas_in_a_short_reply_use_the_first():
    assert requested_area("Семиньяк или Санур") == "Seminyak"


@pytest.mark.parametrize(
    ("text", "area"),
    [
        ("Canggu", "Canggu"),
        ("в Чангу", "Canggu"),
        ("Ubud", "Ubud"),
        ("в Убуде", "Ubud"),
        ("Uluwatu", "Uluwatu"),
        ("в Улувату", "Uluwatu"),
        ("Sanur", "Sanur"),
        ("в Сануре", "Sanur"),
        ("Kuta", "Kuta"),
        ("в Куте", "Kuta"),
        ("Nusa Dua", "Nusa Dua"),
        ("в Нуса Дуа", "Nusa Dua"),
        ("Jimbaran", "Jimbaran"),
        ("в Джимбаране", "Jimbaran"),
        ("Pererenan", "Pererenan"),
        ("в Переренане", "Pererenan"),
        ("Berawa", "Berawa"),
        ("в Бераве", "Berawa"),
        ("Amed", "Amed"),
        ("в Амеде", "Amed"),
        ("Lovina", "Lovina"),
        ("в Ловине", "Lovina"),
    ],
)
def test_short_reply_recognizes_the_agreed_areas(text, area):
    assert requested_area(text) == area


async def test_unmapped_partner_type_is_searched_by_its_slug():
    seen = []

    async def search(query: str):
        seen.append(query)
        return [_place("Canggu")]

    await suggest_places(_partner_type(slug="night_market"), search, area="Canggu")

    assert seen == ["night market Canggu"]


@pytest.mark.parametrize(
    ("slug", "phrase"),
    [
        ("vehicle_rent", "scooter rental"),
        ("excursions", "tour agency"),
        ("money_exchange", "currency exchange"),
        ("visa_service", "visa agent"),
        ("esim", "eSIM shop"),
    ],
)
async def test_known_partner_types_use_their_fixed_query(slug, phrase):
    seen = []

    async def search(query: str):
        seen.append(query)
        return [_place("Canggu")]

    await suggest_places(_partner_type(slug=slug), search, area="Canggu")

    assert seen == [f"{phrase} Canggu"]


def test_reply_appends_each_place_and_its_google_link_after_the_intro():
    suggestions = PlaceSuggestions(
        places=(
            SuggestedPlace(
                name="Salon in Canggu",
                area="Canggu",
                maps_url="https://maps.google.com/?cid=Canggu",
                rating=4.8,
            ),
        )
    )

    text = compose_reply("Вот салоны, которые стоит посмотреть.", suggestions)

    assert text == (
        "Вот салоны, которые стоит посмотреть.\n\n"
        "Salon in Canggu\n"
        "Canggu · 4.8\n"
        "https://maps.google.com/?cid=Canggu"
    )


def test_reply_omits_a_missing_rating():
    suggestions = PlaceSuggestions(
        places=(
            SuggestedPlace(
                name="Salon in Ubud",
                area="Ubud",
                maps_url="https://maps.google.com/?cid=Ubud",
            ),
        )
    )

    text = compose_reply("Intro.", suggestions)

    assert text == (
        "Intro.\n\n"
        "Salon in Ubud\n"
        "Ubud\n"
        "https://maps.google.com/?cid=Ubud"
    )


def test_finished_text_is_the_whole_reply():
    suggestions = PlaceSuggestions(places=(), text="В Seminyak ничего не нашлось.")

    assert compose_reply("Intro the model should not write.", suggestions) == (
        "В Seminyak ничего не нашлось."
    )


def test_area_follow_up_keeps_the_empty_partner_button():
    beauty = "💇‍♀️ \nБьюти услуги"
    messages = [
        {
            "role": "user",
            "content": beauty,
            "metadata": {"place_suggestion_slug": "beauty_service"},
        },
        {
            "role": "assistant",
            "content": "Salon in Canggu",
            "metadata": {"place_suggestion_slug": "beauty_service"},
        },
        {"role": "user", "content": "спасибо", "metadata": {}},
    ]

    assert active_suggestion_slug(messages, {beauty, "📱 \neSIM"}) == "beauty_service"


def test_another_menu_button_clears_the_place_suggestion():
    beauty = "💇‍♀️ \nБьюти услуги"
    esim = "📱 \neSIM"
    messages = [
        {
            "role": "user",
            "content": beauty,
            "metadata": {"place_suggestion_slug": "beauty_service"},
        },
        {"role": "user", "content": esim, "metadata": {}},
    ]

    assert active_suggestion_slug(messages, {beauty, esim}) is None


def test_intro_request_names_the_button_and_areas_without_links():
    suggestions = PlaceSuggestions(
        places=(
            SuggestedPlace(
                name="Salon in Canggu",
                area="Canggu",
                maps_url="https://maps.google.com/?cid=Canggu",
                rating=4.8,
            ),
        )
    )

    text = intro_request(_partner_type(), suggestions)

    assert "Бьюти" in text
    assert "Canggu" in text
    assert "https://" not in text
    assert "Salon in Canggu" not in text


async def test_place_reply_keeps_mikes_intro_and_only_googles_link():
    async def search(query: str):
        assert query == "beauty salon Canggu"
        return [_place("Canggu")]

    async def write_intro(prompt: str):
        assert "https://" not in prompt
        return "Вот подборка.\nhttps://goo.gl/fake"

    text = await build_place_reply(
        _partner_type(), search, write_intro, area="Canggu"
    )

    assert text == (
        "Вот подборка.\n\n"
        "Salon in Canggu\n"
        "Canggu · 4.8\n"
        "https://maps.google.com/?cid=Canggu"
    )


async def test_place_reply_does_not_ask_mike_when_no_places_are_found():
    async def search(query: str):
        return []

    async def write_intro(prompt: str):
        raise AssertionError(prompt)

    text = await build_place_reply(_partner_type(), search, write_intro)

    assert text == _partner_type().fallback


def test_without_a_places_key_the_button_asks_for_maps_search_links():
    text = model_search_request(_partner_type())

    assert "Canggu" in text
    assert "Ubud" in text
    assert "Uluwatu" in text
    assert "beauty salon" in text
    assert "https://www.google.com/maps/search/?api=1&query=" in text
    assert "Напишите Майку" not in text


def test_named_area_asks_for_that_area_only():
    text = model_search_request(_partner_type(), area="Seminyak")

    assert "Seminyak" in text
    assert "Canggu" not in text
