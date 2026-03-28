"""Test weather and news API services."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from backend.services.weather_service import weather_service
from backend.services.news_service import news_service
from backend.config.settings import settings


async def test_apis():
    """Test weather and news APIs."""
    
    print("=" * 60)
    print("API Configuration Status")
    print("=" * 60)
    
    # Check configuration
    print(f"\n1. OpenWeather API Key: {('✓ Configured' if settings.openweather_api_key else '✗ NOT CONFIGURED (empty)')}")
    print(f"2. News API Key: {('✓ Configured' if settings.news_api_key else '✗ NOT CONFIGURED (empty)')}")
    print(f"3. Google Maps API Key: {('✓ Configured' if settings.google_maps_api_key else '✗ NOT CONFIGURED (empty)')}")
    
    print("\n" + "=" * 60)
    print("Testing Weather API")
    print("=" * 60)
    
    if not settings.openweather_api_key:
        print("⚠ Weather API key is empty. Please add OPENWEATHER_API_KEY to .env")
        print("  Get it from: https://openweathermap.org/api")
    else:
        print("Testing weather fetch for 'New York'...")
        try:
            weather = await weather_service.get_weather_for_location("New York")
            if weather:
                print("✓ Weather API working!")
                print(f"  Location: {weather['location']}")
                print(f"  Temperature: {weather['temperature_c']}°C")
                print(f"  Conditions: {weather['conditions']}")
                print(f"  Alerts: {weather['alerts'] if weather['alerts'] else 'None'}")
            else:
                print("✗ Weather API returned no data")
        except Exception as e:
            print(f"✗ Weather API error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing News API")
    print("=" * 60)
    
    if not settings.news_api_key:
        print("⚠ News API key is empty. Please add NEWS_API_KEY to .env")
        print("  Get it from: https://newsapi.org/")
    else:
        print("Testing news fetch for 'flood emergency'...")
        try:
            news = await news_service.get_relevant_news(
                incident_keywords="flood",
                max_articles=3
            )
            if news:
                print("✓ News API working!")
                for i, headline in enumerate(news, 1):
                    print(f"  {i}. {headline[:100]}...")
            else:
                print("✗ News API returned no articles")
        except Exception as e:
            print(f"✗ News API error: {e}")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("\nTo enable Weather API:")
    print("  1. Go to https://openweathermap.org/api")
    print("  2. Sign up and get your API key")
    print("  3. Add to .env: OPENWEATHER_API_KEY=your_key_here")
    print("\nTo enable News API:")
    print("  1. Go to https://newsapi.org/")
    print("  2. Sign up and get your API key")
    print("  3. Add to .env: NEWS_API_KEY=your_key_here")
    print("\nTo enable Google Maps API:")
    print("  1. Go to https://cloud.google.com/maps-platform")
    print("  2. Enable the Maps API and get your API key")
    print("  3. Add to .env: GOOGLE_MAPS_API_KEY=your_key_here")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_apis())
