"""Real Bali places from the Google Places API.

Mike used to name restaurants from model memory and guess their map links, so
Tourists got invented places behind dead goo.gl links. Every link handed to a
Tourist now comes from a place id Google returned. The request asks only for
that id, which is the free Text Search field. Name, address, and rating are
paid fields and are not requested.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from maps_links import maps_place_url

logger = logging.getLogger(__name__)

SEARCH_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"

# Island centroid near Gianyar. The API caps a circle bias at 50 km; that
# covers the main tourist belt (Canggu, Seminyak, Ubud, Sanur, Uluwatu).
# locationBias is a preference, not a hard fence, so Amed or Lovina can
# still return when the query names them.
BALI_CENTER = (-8.4095, 115.1889)
SEARCH_RADIUS_M = 50000.0
LANGUAGE_CODE = "ru"
REGION_CODE = "ID"
DEFAULT_LIMIT = 5
REQUEST_TIMEOUT_S = 10.0

# Ids only. Adding displayName, address, rating, or hours bills a paid SKU.
FIELD_MASK = "places.id"


@dataclass(frozen=True)
class Place:
    name: str
    address: str
    maps_url: str
    place_id: str
    rating: float | None = None
    rating_count: int | None = None
    category: str | None = None
    open_now: bool | None = None

    def for_model(self) -> dict:
        """Compact shape for the model; keys it can quote back verbatim."""
        payload = {"name": self.name, "address": self.address, "maps_url": self.maps_url}
        if self.category:
            payload["category"] = self.category
        if self.rating is not None:
            payload["rating"] = self.rating
        if self.rating_count is not None:
            payload["rating_count"] = self.rating_count
        if self.open_now is not None:
            payload["open_now"] = self.open_now
        return payload


def _parse_place(raw: dict, *, query: str) -> Place | None:
    place_id = raw.get("id") or ""
    if not place_id:
        return None

    return Place(
        name=query,
        address="",
        maps_url=maps_place_url(query, place_id),
        place_id=place_id,
    )


class PlacesClient:
    """Text Search over Google Places, biased to Bali."""

    def __init__(self, api_key: str, *, client: httpx.AsyncClient | None = None):
        self._api_key = api_key
        self._client = client
        self._owns_client = client is None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S)
        return self._client

    async def search(
        self, query: str, *, limit: int = DEFAULT_LIMIT, open_now: bool = False
    ) -> list[Place]:
        query = (query or "").strip()
        if not query:
            return []

        latitude, longitude = BALI_CENTER
        body = {
            "textQuery": query,
            "pageSize": max(1, min(limit, 20)),
            "languageCode": LANGUAGE_CODE,
            "regionCode": REGION_CODE,
            "locationBias": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": SEARCH_RADIUS_M,
                }
            },
        }
        if open_now:
            body["openNow"] = True

        http = await self._http()
        try:
            response = await http.post(
                SEARCH_TEXT_URL,
                json=body,
                headers={
                    "X-Goog-Api-Key": self._api_key,
                    "X-Goog-FieldMask": FIELD_MASK,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            # A lookup failure must not take the whole reply down.
            logger.warning("Places search failed for %r: %s", query, exc)
            return []

        places = (_parse_place(raw, query=query) for raw in payload.get("places") or ())
        return [place for place in places if place is not None][:limit]

    async def close(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None
