"""Mike must never send a shortened map link: the id is guessed and goo.gl is dead."""

from __future__ import annotations

import pytest

from bot import MIKE_PROMPT
from maps_links import MAPS_SEARCH_BASE, is_shortened, maps_search_url, sanitize_map_links


def test_bare_shortlink_becomes_maps_search_for_the_named_place():
    answer = (
        "Вот ссылка на Seniman Coffee Studio на Google Картах:\n"
        "https://goo.gl/maps/KRKCNvvoD2K2\n\n"
        "Отличное место!"
    )

    result = sanitize_map_links(answer)

    assert "goo.gl" not in result
    assert (
        "https://www.google.com/maps/search/?api=1&query=Seniman+Coffee+Studio+Bali"
        in result
    )
    assert "Отличное место!" in result


def test_markdown_shortlink_is_flattened_and_rewritten():
    answer = "[Betelnut Cafe, Canggu - Google Maps](https://goo.gl/maps/yourlink)"

    result = sanitize_map_links(answer)

    assert "](" not in result
    assert "goo.gl" not in result
    assert MAPS_SEARCH_BASE in result


@pytest.mark.parametrize(
    "url",
    [
        "https://maps.app.goo.gl/abc123",
        "https://g.page/somewhere",
        "https://bit.ly/xyz",
    ],
)
def test_other_shorteners_are_rejected(url):
    assert is_shortened(url)
    assert url not in sanitize_map_links(f"Betelnut Cafe: {url}")


def test_real_links_are_left_alone():
    answer = (
        "Смотри тут: https://www.google.com/maps/search/?api=1&query=Betelnut+Cafe+Canggu+Bali\n"
        "и на сайте https://balipromax.com"
    )

    assert sanitize_map_links(answer) == answer


def test_markdown_link_to_real_url_is_flattened_for_plain_text_delivery():
    result = sanitize_map_links("[сайт](https://balipromax.com)")

    assert result == "сайт: https://balipromax.com"


def test_shortlink_without_any_place_name_is_dropped():
    result = sanitize_map_links("Держи: https://goo.gl/maps/abc123")

    assert "goo.gl" not in result
    assert "http" not in result


def test_maps_search_url_adds_region_once():
    assert maps_search_url("Betelnut Cafe Canggu") == (
        f"{MAPS_SEARCH_BASE}Betelnut+Cafe+Canggu+Bali"
    )
    assert maps_search_url("Seniman Coffee Studio Ubud Bali") == (
        f"{MAPS_SEARCH_BASE}Seniman+Coffee+Studio+Ubud+Bali"
    )


def test_prompt_forbids_shortened_links():
    assert "goo.gl" in MIKE_PROMPT
    assert MAPS_SEARCH_BASE.rstrip("=") in MIKE_PROMPT
