"""Deduplication and event clustering for news articles."""

from typing import Set, List
from app.general_intelligence.normalize_article import NormalizedArticle


class Deduplicator:
    """Tracks seen canonical URLs and content hashes to filter duplicate articles."""

    def __init__(self):
        self._seen_urls: Set[str] = set()
        self._seen_hashes: Set[str] = set()

    def is_duplicate(self, article: NormalizedArticle) -> bool:
        """
        Check if an article has already been seen by its canonical URL or content hash.
        If not seen, records it and returns False.
        """
        if not article or not article.source_url:
            return True

        if article.source_url in self._seen_urls:
            return True

        if article.content_hash in self._seen_hashes:
            return True

        # Register as seen
        self._seen_urls.add(article.source_url)
        self._seen_hashes.add(article.content_hash)
        return False

    def filter_unique(self, articles: List[NormalizedArticle]) -> List[NormalizedArticle]:
        """Filter a list of articles, returning only unique ones."""
        unique_articles = []
        for art in articles:
            if not self.is_duplicate(art):
                unique_articles.append(art)
        return unique_articles

    def reset(self):
        """Clear memory."""
        self._seen_urls.clear()
        self._seen_hashes.clear()
