"""Article normalization, URL cleaning, and content hashing."""

import re
import hashlib
from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from dateutil import parser as date_parser
from app.utils.time import utc_now


TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term",
    "utm_content", "ref", "fbclid", "gclid", "guccounter",
}


def clean_url(raw_url: str) -> str:
    """
    Canonicalize URL by removing tracking parameters, fragments,
    and trailing slashes.
    """
    if not raw_url:
        return ""

    parsed = urlparse(raw_url.strip())
    # Filter out tracking query params
    filtered_query = [
        (k, v) for k, v in parse_qsl(parsed.query)
        if k.lower() not in TRACKING_PARAMS
    ]
    new_query = urlencode(filtered_query)
    clean_path = parsed.path.rstrip("/")

    canonical = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        clean_path,
        parsed.params,
        new_query,
        "",  # Strip fragment
    ))
    return canonical


def strip_html_tags(text: Optional[str]) -> str:
    """Remove HTML tags and normalize extra whitespace."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Decode basic entities
    clean = clean.replace("&amp;", "&").replace("&quot;", '"').replace("&apos;", "'").replace("&lt;", "<").replace("&gt;", ">")
    # Collapse multiple whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def parse_date(date_str: Optional[str]) -> datetime:
    """Parse various RSS date formats into a UTC datetime."""
    if not date_str:
        return utc_now()

    # Try RFC 2822 (common in RSS)
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    # Try dateutil parser (handles ISO 8601, Atom, and many variants)
    try:
        dt = date_parser.parse(date_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return utc_now()


def compute_content_hash(title: str, source_name: str) -> str:
    """Create a deterministic hash from article title and source."""
    normalized_key = f"{source_name.strip().lower()}:{title.strip().lower()}"
    return hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()[:16]


class NormalizedArticle:
    """Standardized article data representation."""

    def __init__(
        self,
        title: str,
        source_name: str,
        source_url: str,
        published_at: datetime,
        content_excerpt: str = "",
        content_hash: str = "",
    ):
        self.title = title
        self.source_name = source_name
        self.source_url = source_url
        self.published_at = published_at
        self.content_excerpt = content_excerpt
        self.content_hash = content_hash or compute_content_hash(title, source_name)


def normalize_feed_item(raw_title: str, raw_url: str, raw_published: Optional[str], raw_summary: Optional[str], source_name: str) -> Optional[NormalizedArticle]:
    """Validate and normalize raw feed item into a NormalizedArticle."""
    clean_title = strip_html_tags(raw_title)
    canonical_url = clean_url(raw_url)
    clean_summary = strip_html_tags(raw_summary)

    # Validate essential fields
    if not clean_title or not canonical_url or not canonical_url.startswith("http"):
        return None

    pub_date = parse_date(raw_published)
    content_hash = compute_content_hash(clean_title, source_name)

    return NormalizedArticle(
        title=clean_title,
        source_name=source_name,
        source_url=canonical_url,
        published_at=pub_date,
        content_excerpt=clean_summary,
        content_hash=content_hash,
    )
