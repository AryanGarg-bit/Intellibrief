"""RSS Client for fetching and parsing standard RSS / Atom feeds."""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime
import httpx
from app.utils.logging import logger


class RawFeedItem:
    """Represents a single raw entry parsed from an RSS feed."""

    def __init__(
        self,
        title: str,
        link: str,
        published: Optional[str] = None,
        summary: Optional[str] = None,
        source_name: str = "",
    ):
        self.title = title
        self.link = link
        self.published = published
        self.summary = summary
        self.source_name = source_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "published": self.published,
            "summary": self.summary,
            "source_name": self.source_name,
        }


def parse_rss_xml(xml_content: str, default_source_name: str = "RSS Feed") -> List[RawFeedItem]:
    """
    Parse an RSS 2.0 or Atom XML string into a list of RawFeedItem objects.
    Uses standard library ElementTree for simplicity and reliability.
    """
    items: List[RawFeedItem] = []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as err:
        logger.warning(f"XML parse error for {default_source_name}: {err}")
        return items

    # Check for standard RSS 2.0 (<channel><item>)
    channel = root.find("channel")
    if channel is not None:
        source_title_elem = channel.find("title")
        source_name = source_title_elem.text.strip() if source_title_elem is not None and source_title_elem.text else default_source_name

        for item_elem in channel.findall("item"):
            title_elem = item_elem.find("title")
            link_elem = item_elem.find("link")
            pub_elem = item_elem.find("pubDate")
            desc_elem = item_elem.find("description")

            title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else None
            summary = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else None

            if title and link:
                items.append(
                    RawFeedItem(
                        title=title,
                        link=link,
                        published=pub_date,
                        summary=summary,
                        source_name=source_name,
                    )
                )
        return items

    # Check for Atom feed (<feed><entry>)
    # Atom elements usually carry a namespace e.g. {http://www.w3.org/2005/Atom}entry
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    atom_entries = root.findall("atom:entry", ns) or root.findall("entry")
    source_title_elem = root.find("atom:title", ns) or root.find("title")
    source_name = source_title_elem.text.strip() if source_title_elem is not None and source_title_elem.text else default_source_name

    for entry in atom_entries:
        title_elem = entry.find("atom:title", ns) or entry.find("title")
        link_elem = entry.find("atom:link", ns) or entry.find("link")
        pub_elem = entry.find("atom:published", ns) or entry.find("published") or entry.find("atom:updated", ns) or entry.find("updated")
        summary_elem = entry.find("atom:summary", ns) or entry.find("summary") or entry.find("atom:content", ns) or entry.find("content")

        title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
        link = link_elem.attrib.get("href", "") if link_elem is not None else ""
        pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else None
        summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else None

        if title and link:
            items.append(
                RawFeedItem(
                    title=title,
                    link=link,
                    published=pub_date,
                    summary=summary,
                    source_name=source_name,
                )
            )

    return items


def fetch_feed_sync(feed_url: str, source_name: str = "News Feed", timeout_seconds: float = 10.0) -> List[RawFeedItem]:
    """
    Fetch an RSS feed synchronously over HTTP with timeout and error handling.
    Returns empty list if network or server error occurs.
    """
    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            resp = client.get(feed_url)
            resp.raise_for_status()
            return parse_rss_xml(resp.text, default_source_name=source_name)
    except Exception as e:
        logger.warning(f"Failed to fetch RSS feed from {feed_url}: {e}")
        return []
