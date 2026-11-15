"""Build candidate news pool for Layer A (General Intelligence)."""

from typing import List, Dict, Any
from app.general_intelligence.rss_client import RawFeedItem
from app.general_intelligence.normalize_article import normalize_feed_item
from app.general_intelligence.deduplicate import Deduplicator
from app.general_intelligence.classify_news import classify_category_and_topics, detect_region
from app.general_intelligence.score_news import score_article
from app.repositories.articles_repository import ArticleModel, articles_repo
from app.utils.logging import logger


def process_and_store_raw_items(
    raw_items: List[RawFeedItem],
    deduplicator: Deduplicator,
) -> Dict[str, Any]:
    """
    Process raw feed items, deduplicate, classify, score, and store in shared pool.
    Returns summary statistics.
    """
    finance_count = 0
    tech_count = 0
    duplicates_count = 0

    for raw in raw_items:
        # 1. Normalize
        normalized = normalize_feed_item(
            raw_title=raw.title,
            raw_url=raw.link,
            raw_published=raw.published,
            raw_summary=raw.summary,
            source_name=raw.source_name,
        )

        if not normalized:
            continue

        # 2. Deduplicate
        if deduplicator.is_duplicate(normalized):
            duplicates_count += 1
            continue

        # 3. Classify Category, Region & Topics
        category, topic_ids = classify_category_and_topics(
            title=normalized.title,
            excerpt=normalized.content_excerpt,
        )
        region = detect_region(f"{normalized.title} {normalized.content_excerpt}")

        # 4. Score importance
        importance = score_article(
            title=normalized.title,
            source_name=normalized.source_name,
            published_at=normalized.published_at,
            matched_topic_ids=topic_ids,
        )

        # 5. Persist to shared pool
        article = ArticleModel(
            title=normalized.title,
            source_name=normalized.source_name,
            source_url=normalized.source_url,
            published_at=normalized.published_at,
            category=category,
            region=region,
            topic_ids=topic_ids,
            content_excerpt=normalized.content_excerpt,
            summary=normalized.content_excerpt or normalized.title,
            why_it_matters=f"Significant {category} development impacting {', '.join(topic_ids) if topic_ids else 'the market'}.",
            importance_score=importance,
            content_hash=normalized.content_hash,
            processing_status="processed",
        )
        articles_repo.save_article(article)

        if category == "Finance":
            finance_count += 1
        else:
            tech_count += 1

    logger.info(
        f"Layer A complete: {finance_count} Finance, {tech_count} Tech, {duplicates_count} duplicates skipped."
    )

    return {
        "finance_candidates": finance_count,
        "technology_candidates": tech_count,
        "duplicates_skipped": duplicates_count,
        "total_added": finance_count + tech_count,
    }
