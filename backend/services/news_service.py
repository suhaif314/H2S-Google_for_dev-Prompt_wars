"""News Service — Recent news for situational awareness."""

import logging
from typing import Optional

import httpx

from backend.config.settings import settings

logger = logging.getLogger(__name__)

NEWSAPI_BASE_URL = "https://newsapi.org/v2"


class NewsService:
    """Fetches recent news articles for emergency context enrichment."""

    async def get_relevant_news(
        self,
        location: Optional[str] = None,
        incident_keywords: Optional[str] = None,
        max_articles: int = 5,
    ) -> Optional[list[str]]:
        """
        Fetch recent news relevant to the emergency.

        Args:
            location: Location to search news for
            incident_keywords: Keywords related to the incident type
            max_articles: Maximum number of articles to return

        Returns:
            List of news headline strings or None
        """
        if not settings.news_api_key:
            logger.warning("News API key not configured, skipping news data")
            return None

        # Build search query combining location and incident type
        query_parts = []
        if location:
            query_parts.append(location)
        if incident_keywords:
            query_parts.append(incident_keywords)

        if not query_parts:
            query_parts = ["emergency", "disaster", "accident"]

        query = " OR ".join(query_parts)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "q": query,
                    "apiKey": settings.news_api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": max_articles,
                }

                response = await client.get(
                    f"{NEWSAPI_BASE_URL}/everything", params=params
                )

                if response.status_code != 200:
                    logger.warning(f"News API returned {response.status_code}")
                    return None

                data = response.json()
                articles = data.get("articles", [])

                headlines = []
                for article in articles[:max_articles]:
                    title = article.get("title", "")
                    description = article.get("description", "")
                    source = article.get("source", {}).get("name", "Unknown")
                    published = article.get("publishedAt", "")[:10]

                    headline = f"[{source}, {published}] {title}"
                    if description:
                        headline += f" — {description[:150]}"

                    headlines.append(headline)

                logger.info(f"Fetched {len(headlines)} news articles for query: '{query}'")
                return headlines if headlines else None

        except httpx.TimeoutException:
            logger.warning("News API timeout")
            return None
        except Exception as e:
            logger.error(f"News API error: {e}")
            return None


# Singleton instance
news_service = NewsService()
