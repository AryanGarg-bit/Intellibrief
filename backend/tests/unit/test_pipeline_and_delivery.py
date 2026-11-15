"""Unit tests for story selection, email rendering, delivery idempotency, and daily pipeline."""

from datetime import datetime, timezone
import pytest
from fastapi import HTTPException
from app.repositories.users_repository import users_repo
from app.repositories.preferences_repository import preferences_repo
from app.repositories.articles_repository import articles_repo, ArticleModel
from app.repositories.deliveries_repository import deliveries_repo
from app.schemas import PreferenceItem
from app.personalization.select_stories import select_daily_stories
from app.reporting.render_email import render_email, generate_executive_summary
from app.delivery.delivery_service import deliver_report_for_user
from app.general_intelligence.rss_client import RawFeedItem
from app.jobs.daily_pipeline import run_daily_pipeline
from app.routes.pipeline import trigger_daily_job, DailyRunRequest
from app.config import settings


def create_dummy_article(title: str, category: str, score: float = 7.0) -> ArticleModel:
    return ArticleModel(
        title=title,
        source_name="Test Publisher",
        source_url=f"https://example.com/{abs(hash(title))}",
        published_at=datetime.now(timezone.utc),
        category=category,
        region="Global",
        importance_score=score,
        summary=f"Summary for {title}",
    )


def test_select_stories_exact_count_and_shortage():
    """Verify selecting 5+5 when available, and explicit shortage when fewer exist."""
    candidates = [
        # 3 Finance articles
        create_dummy_article("Fin 1", "Finance"),
        create_dummy_article("Fin 2", "Finance"),
        create_dummy_article("Fin 3", "Finance"),
        # 6 Tech articles
        create_dummy_article("Tech 1", "Technology"),
        create_dummy_article("Tech 2", "Technology"),
        create_dummy_article("Tech 3", "Technology"),
        create_dummy_article("Tech 4", "Technology"),
        create_dummy_article("Tech 5", "Technology"),
        create_dummy_article("Tech 6", "Technology"),
    ]

    prefs = [
        PreferenceItem(topic_id="ai_products", display_name="AI Products", category="Technology", interest_score=8)
    ]

    result = select_daily_stories(candidates, prefs, target_per_category=5)

    # Must have exactly 3 finance stories and an explicit note
    assert len(result.finance_stories) == 3
    assert result.finance_shortage_note is not None
    assert "3 of 5" in result.finance_shortage_note

    # Must have capped at 5 tech stories, no shortage note
    assert len(result.technology_stories) == 5
    assert result.tech_shortage_note is None


def test_render_email_html_and_text():
    """Verify HTML and plain-text email rendering with safe escaping and links."""
    candidates = [
        create_dummy_article("NVIDIA <Blackwell> GPU & AI", "Technology"),
        create_dummy_article("Sensex rallies 500 pts", "Finance"),
    ]
    result = select_daily_stories(candidates, [], target_per_category=5)

    subject, html_out, text_out = render_email(
        report_date="2026-11-14",
        selection=result,
        user_email="reader@example.com",
        user_id="user-123",
    )

    assert "Your Daily Intelligence Briefing — 2026-11-14" in subject
    # Escaped HTML check
    assert "&lt;Blackwell&gt;" in html_out
    assert "Manage Preferences" in html_out
    assert "Unsubscribe" in html_out

    # Plain text check
    assert "INTELLIBRIEF — Daily Briefing" in text_out
    assert "Sensex rallies 500 pts" in text_out


def test_delivery_service_and_idempotency():
    """Verify delivery intent, email send, and duplicate prevention."""
    user = users_repo.create_or_get_user("daily_user@example.com")
    users_repo.mark_quiz_completed(user.id)

    candidates = [
        create_dummy_article("Markets Today", "Finance"),
        create_dummy_article("AI Breakthrough", "Technology"),
    ]

    report_date = "2026-11-14"

    # First send should succeed
    res1 = deliver_report_for_user(user, report_date, candidates)
    assert res1["status"] == "sent"

    # Second send for the same report_date must be skipped (idempotent!)
    res2 = deliver_report_for_user(user, report_date, candidates)
    assert res2["status"] == "skipped"
    assert "Already sent" in res2["reason"]


def test_daily_pipeline_orchestration():
    """Verify running the daily pipeline with feed fixtures."""
    # Ensure active user exists
    user = users_repo.create_or_get_user("pipeline_test@example.com")
    users_repo.mark_quiz_completed(user.id)

    feed_items = [
        RawFeedItem(
            title="Global Inflation slows down in Q3",
            link="https://fin.example.com/inflation-q3",
            published=None,
            summary="Consumer price index cools globally.",
            source_name="Financial Times",
        ),
        RawFeedItem(
            title="OpenAI releases new reasoning model",
            link="https://tech.example.com/reasoning-model",
            published=None,
            summary="New artificial intelligence model benchmark results.",
            source_name="TechCrunch",
        ),
    ]

    summary = run_daily_pipeline(
        report_date="2026-11-15",
        custom_feed_items=feed_items,
    )

    assert summary["layer_a"]["total_added"] >= 2
    assert summary["layer_b"]["sent"] >= 1


from unittest.mock import patch

def test_internal_pipeline_route_auth():
    """Verify internal route security."""
    # Invalid secret must raise 401
    with pytest.raises(HTTPException) as exc_info:
        trigger_daily_job(
            req=DailyRunRequest(report_date="2026-11-16"),
            x_job_secret="wrong-secret",
        )
    assert exc_info.value.status_code == 401

    # Valid secret succeeds (mocking fetch_feed_sync to avoid network timeout)
    with patch("app.jobs.daily_pipeline.fetch_feed_sync", return_value=[]):
        res = trigger_daily_job(
            req=DailyRunRequest(report_date="2026-11-16"),
            x_job_secret=settings.internal_job_secret,
        )
        assert res["status"] == "success"

