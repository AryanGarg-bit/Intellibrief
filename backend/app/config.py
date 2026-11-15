"""Application configuration and settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App environment
    app_env: str = "local"
    app_base_url: str = "http://localhost:3000"
    backend_base_url: str = "http://localhost:8000"

    # Timezone & Schedule
    timezone: str = "Asia/Kolkata"
    daily_send_hour: int = 7
    daily_send_minute: int = 0

    # AI Provider
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Supabase (Database)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Transactional Email (Resend)
    resend_api_key: str = ""
    email_from: str = "Daily Intelligence <briefing@example.com>"

    # Pipeline Settings
    internal_job_secret: str = "local_dev_secret"
    news_lookback_hours: int = 36
    max_source_articles: int = 60
    min_source_quality: float = 5.0
    retry_max_attempts: int = 3


# Global settings instance
settings = Settings()
