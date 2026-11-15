"""Repository for managing shared candidate news articles."""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.utils.time import utc_now


class ArticleModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    source_name: str
    source_url: str
    published_at: datetime
    fetched_at: datetime = Field(default_factory=utc_now)
    category: str  # "Finance" or "Technology"
    region: str = "Global"  # "India" or "Global"
    topic_ids: List[str] = Field(default_factory=list)
    content_excerpt: str = ""
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    impact_analysis: Optional[str] = None
    importance_score: float = 0.0
    content_hash: str = ""
    processing_status: str = "processed"  # 'pending', 'processed', 'failed'


class ArticlesRepository:
    """In-memory article storage with query and filtering helpers."""

    def __init__(self):
        # Key: article_id, Value: ArticleModel
        self._articles_by_id: Dict[str, ArticleModel] = {}
        # Key: source_url, Value: article_id
        self._url_to_id: Dict[str, str] = {}

    def save_article(self, article: ArticleModel) -> ArticleModel:
        """Save or update an article."""
        self._articles_by_id[article.id] = article
        self._url_to_id[article.source_url] = article.id
        return article

    def get_by_id(self, article_id: str) -> Optional[ArticleModel]:
        """Find article by ID."""
        return self._articles_by_id.get(article_id)

    def get_by_url(self, url: str) -> Optional[ArticleModel]:
        """Find article by canonical URL."""
        art_id = self._url_to_id.get(url)
        if art_id:
            return self._articles_by_id.get(art_id)
        return None

    def list_candidates(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 50,
    ) -> List[ArticleModel]:
        """Query candidate articles with optional filtering and descending score order."""
        results = [
            a for a in self._articles_by_id.values()
            if a.processing_status == "processed"
            and a.importance_score >= min_importance
        ]

        if category:
            results = [a for a in results if a.category.lower() == category.lower()]
        if region:
            results = [a for a in results if a.region.lower() == region.lower()]

        # Sort by importance score descending, then publication time descending
        results.sort(key=lambda x: (x.importance_score, x.published_at), reverse=True)
        return results[:limit]

    def clear(self):
        """Clear memory."""
        self._articles_by_id.clear()
        self._url_to_id.clear()


# Singleton instance
articles_repo = ArticlesRepository()
