"""Reports endpoints for today's briefing and history."""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from app.repositories.users_repository import users_repo
from app.repositories.preferences_repository import preferences_repo
from app.repositories.articles_repository import articles_repo
from app.repositories.deliveries_repository import deliveries_repo
from app.personalization.select_stories import select_daily_stories
from app.reporting.render_email import generate_executive_summary
from app.utils.time import today_ist_date_string

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/today/{user_id}")
def get_today_report(user_id: str) -> Dict[str, Any]:
    """Retrieve today's personalized briefing for a user."""
    user = users_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    preferences = preferences_repo.get_preferences(user_id)
    candidates = articles_repo.list_candidates(limit=100)
    selection = select_daily_stories(candidates, preferences, target_per_category=5)

    date_str = today_ist_date_string()
    exec_summary = generate_executive_summary(selection)

    return {
        "report_date": date_str,
        "executive_summary": exec_summary,
        "finance_stories": [s.model_dump() for s in selection.finance_stories],
        "technology_stories": [s.model_dump() for s in selection.technology_stories],
        "finance_shortage_note": selection.finance_shortage_note,
        "tech_shortage_note": selection.tech_shortage_note,
        "total_stories": selection.total_count,
    }


@router.get("/history/{user_id}")
def get_user_delivery_history(user_id: str) -> List[Dict[str, Any]]:
    """List past delivery records for a subscriber."""
    user = users_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    records = deliveries_repo.list_by_user(user_id)
    return [r.model_dump() for r in records]
