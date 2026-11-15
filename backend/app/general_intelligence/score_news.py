"""Transparent quality, significance, and freshness scoring for articles."""

from datetime import datetime
from app.utils.time import utc_now


# High credibility publishers get a source boost
REPUTABLE_SOURCES = {
    "reuters", "bloomberg", "financial times", "wall street journal",
    "economic times", "livemint", "techcrunch", "the verge", "wired",
    "cnbc", "bbc", "moneycontrol",
}


def score_source_quality(source_name: str) -> float:
    """Return quality score between 1.0 and 10.0 for source."""
    clean_name = source_name.lower()
    for reputable in REPUTABLE_SOURCES:
        if reputable in clean_name:
            return 9.0
    return 6.5  # Standard baseline for other configured feeds


def score_freshness(published_at: datetime, max_lookback_hours: int = 36) -> float:
    """Score freshness from 1.0 (oldest within lookback) to 10.0 (just published)."""
    age_seconds = (utc_now() - published_at).total_seconds()
    age_hours = max(0.0, age_seconds / 3600.0)

    if age_hours > max_lookback_hours:
        return 1.0

    # Linear decay from 10.0 down to 2.0 at max_lookback_hours
    fraction = age_hours / max_lookback_hours
    return round(10.0 - (fraction * 8.0), 2)


def score_article(
    title: str,
    source_name: str,
    published_at: datetime,
    matched_topic_ids: list,
    max_lookback_hours: int = 36,
) -> float:
    """
    Calculate shared importance score for the General Intelligence pool.
    Combines source quality (35%), freshness (35%), and topical richness (30%).
    """
    source_score = score_source_quality(source_name)
    freshness = score_freshness(published_at, max_lookback_hours)
    topic_richness = min(10.0, len(matched_topic_ids) * 3.5)

    total = (0.35 * source_score) + (0.35 * freshness) + (0.30 * topic_richness)
    return round(total, 2)
