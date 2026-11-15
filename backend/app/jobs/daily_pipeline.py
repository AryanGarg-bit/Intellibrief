"""Daily pipeline orchestrating General Intelligence and Subscriber Delivery."""

from typing import Dict, Any, List, Optional
from app.repositories.users_repository import users_repo
from app.repositories.articles_repository import articles_repo, ArticleModel
from app.general_intelligence.rss_client import RawFeedItem, fetch_feed_sync
from app.general_intelligence.deduplicate import Deduplicator
from app.general_intelligence.build_news_pool import process_and_store_raw_items
from app.delivery.delivery_service import deliver_report_for_user
from app.utils.time import today_ist_date_string
from app.utils.logging import logger


# Curated starter list of top public RSS feeds for Finance and Technology
DEFAULT_FEEDS = [
    {"url": "https://feeds.feedburner.com/TechCrunch/", "source": "TechCrunch", "category": "Technology"},
    {"url": "https://www.theverge.com/rss/index.xml", "source": "The Verge", "category": "Technology"},
    {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "source": "Economic Times", "category": "Finance"},
    {"url": "https://www.livemint.com/rss/markets", "source": "Livemint", "category": "Finance"},
]


def run_daily_pipeline(
    report_date: Optional[str] = None,
    custom_feed_items: Optional[List[RawFeedItem]] = None,
) -> Dict[str, Any]:
    """
    Execute full daily pipeline:
    1. Layer A: Ingest and process candidate news pool.
    2. Layer B: For each eligible subscriber, personalize and deliver report.
    """
    date_str = report_date or today_ist_date_string()
    logger.info(f"Starting IntelliBrief Daily Pipeline for {date_str} (Asia/Kolkata)")

    # --------------------------------------------------------------------------
    # 1. Layer A: General Intelligence
    # --------------------------------------------------------------------------
    deduplicator = Deduplicator()
    raw_items: List[RawFeedItem] = []

    if custom_feed_items is not None:
        raw_items = custom_feed_items
    else:
        # Fetch from configured RSS feeds
        for feed in DEFAULT_FEEDS:
            feed_items = fetch_feed_sync(feed["url"], source_name=feed["source"])
            raw_items.extend(feed_items)

    layer_a_stats = process_and_store_raw_items(raw_items, deduplicator)
    candidates = articles_repo.list_candidates(limit=100)

    # --------------------------------------------------------------------------
    # 2. Layer B: Personalization & Delivery
    # --------------------------------------------------------------------------
    eligible_subscribers = users_repo.get_active_subscribers()
    sent_count = 0
    skipped_count = 0
    failed_count = 0

    for user in eligible_subscribers:
        delivery_res = deliver_report_for_user(user, date_str, candidates)
        if delivery_res.get("status") == "sent":
            sent_count += 1
        elif delivery_res.get("status") == "skipped":
            skipped_count += 1
        else:
            failed_count += 1

    summary = {
        "report_date": date_str,
        "layer_a": layer_a_stats,
        "layer_b": {
            "eligible_subscribers": len(eligible_subscribers),
            "sent": sent_count,
            "skipped": skipped_count,
            "failed": failed_count,
        },
    }

    logger.info(f"Pipeline complete for {date_str}: {summary}")
    return summary
