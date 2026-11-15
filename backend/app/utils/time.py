"""Time utilities for UTC and Asia/Kolkata."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# The confirmed project timezone
IST = ZoneInfo("Asia/Kolkata")


def utc_now() -> datetime:
    """Return the current timestamp in UTC."""
    return datetime.now(timezone.utc)


def ist_now() -> datetime:
    """Return current timestamp in Asia/Kolkata."""
    return datetime.now(IST)


def today_ist_date_string() -> str:
    """Return today's date in Asia/Kolkata formatted as YYYY-MM-DD."""
    return ist_now().strftime("%Y-%m-%d")


def to_utc(dt: datetime) -> datetime:
    """Convert an aware or naive datetime to UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
