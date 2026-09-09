"""Places lookups must return real places with links Mike can quote verbatim."""

from __future__ import annotations

import json

import httpx
import pytest

from places import (
    BALI_CENTER,
    FIELD_MASK,
    SEARCH_RADIUS_M,
    SEARCH_TEXT_URL,
    PlacesClient,
)

SAMPLE_PLACE = {
    "id": "ChIJ_seniman",
    "displayName": {"text": "Seniman Coffee Studio", "languageCode": "en"},
    "formattedAddress": "Jalan Sriwedari, Ubud, Bali 80571, Indonesia",
    "googleMapsUri": "https://maps.google.com/?cid=1234567890",
    "rating": 4.6,
    "userRatingCount": 4120,
    "primaryTypeDisplayName": {"text": "Кофейня"},
    "currentOpeningHours": {"openNow": True},
}


def client_returning(payload, status=200, recorder=None):
    def handler(request: httpx.Request) -> httpx.Response:
        if recorder is not None:
            recorder.append(request)
        return httpx.Response(status, json=payload)

    transport = httpx.MockTransport(handler)
    return PlacesClient("test-key", client=httpx.AsyncClient(transport=transport))


@pytest.mark.asyncio
async def test_search_returns_place_with_googles_own_link():
    places = client_returning({"places": [SAMPLE_PLACE]})

    results = await places.search("coffee Ubud")

    assert len(results) == 1
    place = results[0]
    assert place.name == "Seniman Coffee Studio"
    assert place.maps_url == "https://maps.google.com/?cid=1234567890"
    assert place.rating == 4.6
    assert place.open_now is True


@pytest.mark.asyncio
async def test_missing_google_uri_falls_back_to_a_place_pinned_search_url():
    raw = {key: value for key, value in SAMPLE_PLACE.items() if key != "googleMapsUri"}
    places = client_returning({"places": [raw]})

    (place,) = await places.search("coffee Ubud")

    assert place.maps_url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "query_place_id=ChIJ_seniman" in place.maps_url


@pytest.mark.asyncio
async def test_request_is_biased_to_bali_and_asks_for_the_fields_we_use():
    requests: list[httpx.Request] = []
    places = client_returning({"places": []}, recorder=requests)

    await places.search("cafe Canggu", limit=3, open_now=True)

    (request,) = requests
    assert str(request.url) == SEARCH_TEXT_URL
    assert request.headers["X-Goog-Api-Key"] == "test-key"
    assert request.headers["X-Goog-FieldMask"] == FIELD_MASK

    body = json.loads(request.content)
    assert body["textQuery"] == "cafe Canggu"
    assert body["pageSize"] == 3
    assert body["openNow"] is True
    assert body["regionCode"] == "ID"
    circle = body["locationBias"]["circle"]
    assert (circle["center"]["latitude"], circle["center"]["longitude"]) == BALI_CENTER
    assert circle["radius"] == SEARCH_RADIUS_M


@pytest.mark.asyncio
async def test_limit_is_honoured_even_if_google_returns_more():
    payload = {"places": [dict(SAMPLE_PLACE, id=f"place-{i}") for i in range(10)]}
    places = client_returning(payload)

    assert len(await places.search("restaurants Canggu", limit=4)) == 4


@pytest.mark.asyncio
async def test_places_without_an_id_or_name_are_dropped():
    payload = {
        "places": [
            {"displayName": {"text": "No id here"}},
            {"id": "no-name"},
            SAMPLE_PLACE,
        ]
    }
    places = client_returning(payload)

    results = await places.search("restaurants Canggu")

    assert [place.name for place in results] == ["Seniman Coffee Studio"]


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [403, 429, 500])
async def test_api_failure_returns_no_places_instead_of_raising(status):
    places = client_returning({"error": {"message": "nope"}}, status=status)

    assert await places.search("restaurants Canggu") == []


@pytest.mark.asyncio
async def test_network_failure_returns_no_places():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route", request=request)

    places = PlacesClient(
        "test-key", client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    )

    assert await places.search("restaurants Canggu") == []


@pytest.mark.asyncio
async def test_blank_query_skips_the_api_entirely():
    requests: list[httpx.Request] = []
    places = client_returning({"places": [SAMPLE_PLACE]}, recorder=requests)

    assert await places.search("   ") == []
    assert requests == []


def test_for_model_omits_unknown_fields():
    from places import Place

    payload = Place(
        name="Seniman Coffee Studio",
        address="Ubud, Bali",
        maps_url="https://maps.google.com/?cid=1",
        place_id="abc",
    ).for_model()

    assert payload == {
        "name": "Seniman Coffee Studio",
        "address": "Ubud, Bali",
        "maps_url": "https://maps.google.com/?cid=1",
    }
