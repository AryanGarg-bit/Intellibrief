"""News exploration and article detail routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.repositories.articles_repository import articles_repo, ArticleModel

router = APIRouter(prefix="/api/news", tags=["News Explorer"])


@router.get("", response_model=List[ArticleModel])
def list_news(
    category: Optional[str] = Query(None, description="Filter by Finance or Technology"),
    region: Optional[str] = Query(None, description="Filter by India or Global"),
    query: Optional[str] = Query(None, description="Keyword search in title"),
    limit: int = Query(50, ge=1, le=100),
) -> List[ArticleModel]:
    """Search and filter candidate news articles."""
    articles = articles_repo.list_candidates(category=category, region=region, limit=limit)

    if query:
        q_lower = query.lower()
        articles = [a for a in articles if q_lower in a.title.lower()]

    return articles


@router.get("/{article_id}", response_model=ArticleModel)
def get_article(article_id: str) -> ArticleModel:
    """Retrieve details for a single article."""
    article = articles_repo.get_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    return article
