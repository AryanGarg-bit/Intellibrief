"""Story selection enforcing the exact 5 Finance + 5 Tech rule and transparent shortages."""

from typing import List, Dict, Tuple, Optional
from app.schemas import PreferenceItem
from app.repositories.articles_repository import ArticleModel
from app.personalization.score_relevance import score_for_user


class SelectionResult:
    """Represents the selected stories and any shortage reasons."""

    def __init__(
        self,
        finance_stories: List[ArticleModel],
        technology_stories: List[ArticleModel],
        finance_shortage_note: Optional[str] = None,
        tech_shortage_note: Optional[str] = None,
    ):
        self.finance_stories = finance_stories
        self.technology_stories = technology_stories
        self.finance_shortage_note = finance_shortage_note
        self.tech_shortage_note = tech_shortage_note

    @property
    def total_count(self) -> int:
        return len(self.finance_stories) + len(self.technology_stories)


def select_daily_stories(
    candidates: List[ArticleModel],
    preferences: List[PreferenceItem],
    target_per_category: int = 5,
) -> SelectionResult:
    """
    Select up to 5 Finance and 5 Technology stories tailored to user preferences.
    If fewer than 5 qualified stories exist, returns available ones with an explicit note.
    Never fabricates or re-labels stories.
    """
    # Separate candidates into categories
    finance_candidates = [c for c in candidates if c.category == "Finance"]
    tech_candidates = [c for c in candidates if c.category == "Technology"]

    # Score each candidate for this user
    scored_finance = [(c, score_for_user(c, preferences)) for c in finance_candidates]
    scored_tech = [(c, score_for_user(c, preferences)) for c in tech_candidates]

    # Sort descending by personalized score
    scored_finance.sort(key=lambda item: item[1], reverse=True)
    scored_tech.sort(key=lambda item: item[1], reverse=True)

    # Pick top items up to target (5)
    selected_fin = [item[0] for item in scored_finance[:target_per_category]]
    selected_tech = [item[0] for item in scored_tech[:target_per_category]]

    # Determine shortage notes if fewer than 5 available
    fin_shortage = None
    if len(selected_fin) < target_per_category:
        fin_shortage = f"{len(selected_fin)} of {target_per_category} qualifying Finance stories available today."

    tech_shortage = None
    if len(selected_tech) < target_per_category:
        tech_shortage = f"{len(selected_tech)} of {target_per_category} qualifying Technology stories available today."

    return SelectionResult(
        finance_stories=selected_fin,
        technology_stories=selected_tech,
        finance_shortage_note=fin_shortage,
        tech_shortage_note=tech_shortage,
    )
