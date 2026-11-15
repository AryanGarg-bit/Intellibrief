"""Score story relevance for an individual subscriber."""

from typing import List
from app.schemas import PreferenceItem
from app.repositories.articles_repository import ArticleModel


def score_for_user(article: ArticleModel, preferences: List[PreferenceItem]) -> float:
    """
    Calculate personalization match score (0.0 to 10.0) between an article
    and a subscriber's structured preferences.
    """
    if not preferences:
        return article.importance_score

    match_score = 0.0
    pref_map = {p.topic_id: p.interest_score for p in preferences}

    # 1. Match on tagged topic IDs
    for topic_id in article.topic_ids:
        if topic_id in pref_map:
            # Interest score is 1-10
            match_score += pref_map[topic_id]

    # 2. Check keyword overlaps in title and excerpt
    combined_text = f"{article.title} {article.content_excerpt}".lower()
    for pref in preferences:
        for kw in pref.keywords:
            if kw.lower() in combined_text:
                match_score += (pref.interest_score * 0.5)
                break

    # Blend baseline importance (30%) with user preference match (70%)
    final_score = (0.30 * article.importance_score) + (0.70 * min(10.0, match_score))
    return round(final_score, 2)
