# backend/app/services/places_service.py
from __future__ import annotations

from typing import Any, Optional
import re
import asyncio
import random
import httpx
from .tag_map import TAG_MAP

# Rotate endpoints because public Overpass instances often time out.
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
]

# Miami bounding box (south, west, north, east)
MIAMI_BBOX = (25.70, -80.30, 25.85, -80.10)


def _build_address(tags: dict[str, Any]) -> Optional[str]:
    # OSM addresses can be fragmented. Build a reasonable display string.
    parts = []
    hn = tags.get("addr:housenumber")
    street = tags.get("addr:street")
    city = tags.get("addr:city")
    state = tags.get("addr:state")
    postcode = tags.get("addr:postcode")

    line1 = " ".join([p for p in [hn, street] if p])
    if line1:
        parts.append(line1)
    line2 = ", ".join([p for p in [city, state, postcode] if p])
    if line2:
        parts.append(line2)

    return ", ".join(parts) if parts else tags.get("addr:full")


def _interest_to_filter(interest: str) -> str:
    for pattern, osm_filter in TAG_MAP:
        if pattern.search(interest):
            return osm_filter

    # Fallback: try name match for the interest, case-insensitive
    # Escape quotes/backslashes for Overpass regex string
    safe = re.sub(r'["\\]', "", interest).strip()
    if safe:
        return f'["name"~"{safe}",i]'
    # Last resort: anything with a name
    return '["name"]'


def _overpass_query(osm_filter: str) -> str:
    s, w, n, e = MIAMI_BBOX
    # nwr = nodes + ways + relations
    # We request center for ways/relations so we always have coordinates.
    return f"""
    [out:json][timeout:25];
    (
      nwr{osm_filter}({s},{w},{n},{e});
    );
    out center 50;
    """


class PlacesService:
    """
    Drop-in replacement for Google Places.
    Returns up to 3 examples in Miami based on the interest.
    """

    def __init__(self, cache: dict[str, list[dict[str, Any]]]) -> None:
        self.cache = cache

    async def _fetch_overpass(self, query: str) -> dict[str, Any]:
        """
        Resilient Overpass call:
        - rotates endpoints
        - retries w/ exponential backoff + jitter
        - uses correct request encoding for /api/interpreter
        """
        attempts = 4
        base_delay = 0.6

        timeout = httpx.Timeout(30.0, connect=10.0)

        last_err: Exception | None = None

        async with httpx.AsyncClient(timeout=timeout) as client:
            for i in range(attempts):
                endpoint = OVERPASS_ENDPOINTS[i % len(OVERPASS_ENDPOINTS)]
                try:
                    # Most compatible format for Overpass interpreter
                    r = await client.post(endpoint, data={"data": query})
                    r.raise_for_status()
                    return r.json()
                except (
                    httpx.HTTPStatusError,
                    httpx.TimeoutException,
                    httpx.RequestError,
                ) as e:
                    last_err = e
                    delay = base_delay * (2**i) + random.uniform(0, 0.3)
                    await asyncio.sleep(delay)

        raise last_err or RuntimeError("Overpass request failed")

    async def get_examples(self, interest: str, cache_key: str) -> list[dict[str, Any]]:
        if cache_key in self.cache:
            return self.cache[cache_key]

        osm_filter = _interest_to_filter(interest)
        query = _overpass_query(osm_filter)

        # IMPORTANT: never crash /api/chat if Overpass is down.
        try:
            data = await self._fetch_overpass(query)
        except Exception:
            self.cache[cache_key] = []
            return []

        elements = data.get("elements", []) or []

        # Build cards, de-dupe by name
        cards: list[dict[str, Any]] = []
        seen_names: set[str] = set()

        for el in elements:
            tags = el.get("tags") or {}
            name = tags.get("name")
            if not name or name in seen_names:
                continue

            # lat/lon: nodes have lat/lon, ways/relations use "center"
            lat = el.get("lat")
            lon = el.get("lon")
            center = el.get("center") or {}
            lat = lat if lat is not None else center.get("lat")
            lon = lon if lon is not None else center.get("lon")

            if lat is None or lon is None:
                continue

            address = _build_address(tags)

            cards.append(
                {
                    "name": name,
                    "address": address,
                    "rating": None,
                    "user_ratings_total": None,
                    "maps_url": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}",
                }
            )

            seen_names.add(name)
            if len(cards) >= 3:
                break

        self.cache[cache_key] = cards
        return cards
