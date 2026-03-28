"""Maps Service — Find nearest emergency facilities."""

import logging
from typing import Optional

import httpx

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class MapsService:
    """Finds nearest hospitals and emergency facilities using Google Maps."""

    async def geocode_location(self, location: str) -> Optional[dict]:
        """
        Convert a location string to lat/lon coordinates.

        Args:
            location: Human-readable location string

        Returns:
            Dict with lat, lng, formatted_address or None
        """
        if not settings.google_maps_api_key:
            logger.warning("Maps API key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "address": location,
                    "key": settings.google_maps_api_key,
                }
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params=params,
                )

                data = response.json()

                if data["status"] != "OK" or not data.get("results"):
                    logger.warning(f"Geocoding failed for '{location}': {data['status']}")
                    return None

                result = data["results"][0]
                geo = result["geometry"]["location"]

                return {
                    "lat": geo["lat"],
                    "lng": geo["lng"],
                    "formatted_address": result["formatted_address"],
                }

        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None

    async def find_nearest_hospitals(
        self,
        lat: float,
        lng: float,
        radius_meters: int = 10000,
        max_results: int = 3,
    ) -> list[dict]:
        """
        Find nearest hospitals to given coordinates.

        Args:
            lat: Latitude
            lng: Longitude
            radius_meters: Search radius in meters
            max_results: Maximum results to return

        Returns:
            List of hospital dicts with name, address, distance info
        """
        if not settings.google_maps_api_key:
            return []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": radius_meters,
                    "type": "hospital",
                    "key": settings.google_maps_api_key,
                }
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                    params=params,
                )

                data = response.json()

                if data["status"] != "OK":
                    logger.warning(f"Places API error: {data['status']}")
                    return []

                hospitals = []
                for place in data.get("results", [])[:max_results]:
                    hospitals.append({
                        "name": place.get("name", "Unknown Hospital"),
                        "address": place.get("vicinity", "Unknown address"),
                        "rating": place.get("rating"),
                        "open_now": place.get("opening_hours", {}).get("open_now"),
                        "lat": place["geometry"]["location"]["lat"],
                        "lng": place["geometry"]["location"]["lng"],
                    })

                logger.info(f"Found {len(hospitals)} hospitals near ({lat}, {lng})")
                return hospitals

        except Exception as e:
            logger.error(f"Places API error: {e}")
            return []


# Singleton instance
maps_service = MapsService()
