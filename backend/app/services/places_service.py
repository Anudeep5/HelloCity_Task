# backend/app/services/places_service.py
from __future__ import annotations

from typing import Any
import urllib.parse
import httpx

from app.core.config import settings


class PlacesService:
    """
    Google Places Text Search implementation.
    Returns up to 3 real Miami places for a given interest.
    """

    def __init__(self, cache: dict[str, list[dict[str, Any]]]) -> None:
        self.cache = cache

    async def get_examples(self, interest: str, cache_key: str) -> list[dict[str, Any]]:
        if cache_key in self.cache:
            return self.cache[cache_key]

        query = f"{interest} in Miami"

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": settings.GOOGLE_PLACES_API_KEY,
        }

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(url, params=params)
                r.raise_for_status()
                data = r.json()
        except Exception:
            self.cache[cache_key] = []
            return []

        results = (data.get("results") or [])[:3]
        cards: list[dict[str, Any]] = []

        for place in results:
            name = place.get("name")
            if not name:
                continue

            address = place.get("formatted_address") or place.get("vicinity")
            rating = place.get("rating")
            user_ratings_total = place.get("user_ratings_total")
            place_id = place.get("place_id")

            # FIX: build a Maps URL that actually targets the place
            # This reliably opens the venue details.
            if place_id:
                q = urllib.parse.quote(name)
                maps_url = (
                    "https://www.google.com/maps/search/?api=1"
                    f"&query={q}"
                    f"&query_place_id={place_id}"
                )
            else:
                maps_url = (
                    "https://www.google.com/maps/search/?api=1&"
                    + urllib.parse.urlencode({"query": f"{name} Miami"})
                )

            cards.append(
                {
                    "name": name,
                    "address": address,
                    "rating": rating,
                    "user_ratings_total": user_ratings_total,
                    "maps_url": maps_url,
                }
            )

            if len(cards) >= 3:
                break

        self.cache[cache_key] = cards
        return cards
