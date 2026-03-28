"""Weather Service — Real-time weather data for disaster context."""

import logging
from typing import Optional

import httpx

from backend.config.settings import settings

logger = logging.getLogger(__name__)

# OpenWeatherMap API base URL
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherService:
    """Fetches real-time weather data to enrich triage context."""

    async def get_weather_for_location(
        self, location: str
    ) -> Optional[dict]:
        """
        Get current weather conditions for a location.

        Args:
            location: City name or "lat,lon" coordinates

        Returns:
            Structured weather data dict or None if unavailable
        """
        if not settings.openweather_api_key:
            logger.warning("OpenWeather API key not configured, skipping weather data")
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Current weather
                params = {
                    "q": location,
                    "appid": settings.openweather_api_key,
                    "units": "metric",
                }

                response = await client.get(
                    f"{OWM_BASE_URL}/weather", params=params
                )

                if response.status_code != 200:
                    logger.warning(
                        f"Weather API returned {response.status_code} for '{location}'"
                    )
                    return None

                data = response.json()

                weather_info = {
                    "location": data.get("name", location),
                    "temperature_c": data["main"]["temp"],
                    "feels_like_c": data["main"]["feels_like"],
                    "humidity_percent": data["main"]["humidity"],
                    "conditions": data["weather"][0]["description"] if data.get("weather") else "unknown",
                    "wind_speed_mps": data["wind"]["speed"],
                    "wind_direction_deg": data["wind"].get("deg", 0),
                    "visibility_m": data.get("visibility", "unknown"),
                    "pressure_hpa": data["main"]["pressure"],
                }

                # Check for severe weather alerts
                alerts = []
                wind_speed = data["wind"]["speed"]
                temp = data["main"]["temp"]

                if wind_speed > 20:
                    alerts.append(f"High winds: {wind_speed} m/s — may impede rescue operations")
                if temp > 40:
                    alerts.append(f"Extreme heat: {temp}°C — heat stroke risk for responders")
                if temp < -10:
                    alerts.append(f"Extreme cold: {temp}°C — hypothermia risk")
                if data["main"]["humidity"] > 90:
                    alerts.append("Very high humidity — reduced visibility possible")

                weather_info["alerts"] = alerts

                logger.info(f"Weather data fetched for '{location}': {weather_info['conditions']}")
                return weather_info

        except httpx.TimeoutException:
            logger.warning(f"Weather API timeout for '{location}'")
            return None
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None


# Singleton instance
weather_service = WeatherService()
