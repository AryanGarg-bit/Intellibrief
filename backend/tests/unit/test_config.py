"""Unit tests for configuration."""

from app.config import Settings


def test_default_settings():
    """Verify that default settings load with expected defaults."""
    cfg = Settings(
        app_env="test",
        gemini_api_key="test_key",
        supabase_url="https://example.supabase.co",
    )
    assert cfg.app_env == "test"
    assert cfg.timezone == "Asia/Kolkata"
    assert cfg.daily_send_hour == 7
    assert cfg.daily_send_minute == 0
    assert cfg.gemini_model == "gemini-2.5-flash"
    assert cfg.gemini_api_key == "test_key"
