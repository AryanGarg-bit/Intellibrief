"""Unit tests for Layer A: General Intelligence modules."""

from datetime import datetime, timezone
from app.general_intelligence.rss_client import parse_rss_xml, RawFeedItem
from app.general_intelligence.normalize_article import clean_url, strip_html_tags, normalize_feed_item
from app.general_intelligence.deduplicate import Deduplicator
from app.general_intelligence.classify_news import classify_category_and_topics, detect_region
from app.general_intelligence.score_news import score_article, score_freshness
from app.general_intelligence.build_news_pool import process_and_store_raw_items
from app.repositories.articles_repository import articles_repo


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Tech &amp; Markets Daily</title>
    <link>https://example.com</link>
    <item>
      <title>NVIDIA announces new Blackwell AI chips</title>
      <link>https://example.com/nvidia-blackwell?utm_source=twitter&amp;utm_campaign=daily</link>
      <pubDate>Mon, 14 Nov 2026 12:00:00 GMT</pubDate>
      <description>&lt;p&gt;NVIDIA unveiled its latest GPU architecture for AI datacenters.&lt;/p&gt;</description>
    </item>
    <item>
      <title>RBI leaves repo rate unchanged at 6.5%</title>
      <link>https://example.com/rbi-rate-decision</link>
      <pubDate>Mon, 14 Nov 2026 10:30:00 GMT</pubDate>
      <description>Reserve Bank of India maintained status quo on interest rates.</description>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_xml():
    """Verify parsing of standard RSS XML feed."""
    items = parse_rss_xml(SAMPLE_RSS, default_source_name="Sample Feed")
    assert len(items) == 2
    assert items[0].title == "NVIDIA announces new Blackwell AI chips"
    assert "nvidia-blackwell" in items[0].link
    assert items[1].title == "RBI leaves repo rate unchanged at 6.5%"


def test_clean_url_removes_utm():
    """Verify UTM parameters and trailing slashes are removed."""
    raw = "https://example.com/nvidia-blackwell/?utm_source=twitter&utm_campaign=daily#section1"
    cleaned = clean_url(raw)
    assert cleaned == "https://example.com/nvidia-blackwell"


def test_strip_html_tags():
    """Verify HTML stripping."""
    html = "<p>Hello <b>World</b> &amp; &quot;Friends&quot;</p>"
    clean = strip_html_tags(html)
    assert clean == 'Hello World & "Friends"'


def test_deduplicator():
    """Verify deduplication detects identical URLs and hashes."""
    dedup = Deduplicator()
    item1 = normalize_feed_item(
        raw_title="AI Breakthrough",
        raw_url="https://example.com/article1",
        raw_published=None,
        raw_summary="Summary",
        source_name="TechDaily",
    )
    item2 = normalize_feed_item(
        raw_title="AI Breakthrough",
        raw_url="https://example.com/article1?utm_medium=rss",  # Same canonical URL
        raw_published=None,
        raw_summary="Summary",
        source_name="TechDaily",
    )

    assert dedup.is_duplicate(item1) is False
    assert dedup.is_duplicate(item2) is True


def test_classification():
    """Verify category, region, and topic classification."""
    cat_tech, topics_tech = classify_category_and_topics(
        title="NVIDIA announces new Blackwell AI chips",
        excerpt="Semiconductor GPU hardware and AI data center acceleration.",
    )
    assert cat_tech == "Technology"
    assert "semiconductors" in topics_tech or "ai_products" in topics_tech

    cat_fin, topics_fin = classify_category_and_topics(
        title="RBI leaves repo rate unchanged at 6.5%",
        excerpt="The central bank held rates steady amidst inflation concerns.",
    )
    assert cat_fin == "Finance"
    assert detect_region("RBI leaves repo rate unchanged in Mumbai, India") == "India"
    assert detect_region("Fed cuts rates in New York") == "Global"


def test_build_news_pool():
    """Verify end-to-end processing and storage in candidate pool."""
    articles_repo.clear()
    raw_items = [
        RawFeedItem(
            title="Tech Giants expand Cloud data center investments",
            link="https://tech.example.com/cloud-expansion",
            published=None,
            summary="Cloud computing infrastructure and AI demand surge.",
            source_name="TechCrunch",
        ),
        RawFeedItem(
            title="Sensex surges 400 points as Indian equities rally",
            link="https://fin.example.com/sensex-rally",
            published=None,
            summary="Dalal Street witnessed strong buying in banking stocks.",
            source_name="Economic Times",
        ),
    ]

    dedup = Deduplicator()
    summary = process_and_store_raw_items(raw_items, dedup)

    assert summary["total_added"] == 2
    assert summary["finance_candidates"] == 1
    assert summary["technology_candidates"] == 1

    candidates = articles_repo.list_candidates()
    assert len(candidates) == 2
