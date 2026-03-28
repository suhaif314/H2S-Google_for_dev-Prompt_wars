"""TriageAI Configuration Settings."""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Cloud
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"

    # Gemini
    gemini_model: str = "gemini-2.5-flash"

    # Weather API
    openweather_api_key: str = ""

    # News API
    news_api_key: str = ""

    # Google Maps
    google_maps_api_key: str = ""

    # App Config
    app_env: str = "development"
    app_port: int = 8000
    max_file_size_mb: int = 10
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:5500,http://localhost:8000"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
