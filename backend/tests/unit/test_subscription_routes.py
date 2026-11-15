"""Unit tests for subscription, quiz, and preferences routes."""

import pytest
from fastapi import HTTPException
from app.schemas import SubscribeRequest, QuizSubmissionRequest, QuizAnswer, UnsubscribeRequest
from app.routes.subscription import subscribe, get_questions, complete_quiz, get_user_preferences, unsubscribe
from app.repositories.users_repository import users_repo
from app.repositories.preferences_repository import preferences_repo


def test_subscribe_creates_user():
    """Verify that subscribe endpoint creates and normalizes user."""
    req = SubscribeRequest(email="  TEST.USER@EXAMPLE.COM  ")
    res = subscribe(req)

    assert res.email == "test.user@example.com"
    assert res.subscription_status == "active"
    assert res.quiz_completed is False
    assert len(res.user_id) > 10


def test_subscribe_existing_user_no_duplicate():
    """Verify subscribing same email twice returns same user_id."""
    req1 = SubscribeRequest(email="investor@example.com")
    res1 = subscribe(req1)

    req2 = SubscribeRequest(email="INVESTOR@example.com")
    res2 = subscribe(req2)

    assert res1.user_id == res2.user_id


def test_get_quiz_questions_endpoint():
    """Verify questions endpoint returns quiz."""
    questions = get_questions()
    assert len(questions) >= 4
    assert any("geo" in q["id"] for q in questions)


def test_complete_quiz_and_fetch_preferences():
    """Verify full quiz completion flow."""
    user = users_repo.create_or_get_user("techie@example.com")

    submission = QuizSubmissionRequest(
        user_id=user.id,
        answers=[
            QuizAnswer(
                question_id="q_tech_sectors",
                selected_topic_ids=["semiconductors", "ai_ml_research"],
                interest_level=9,
            ),
            QuizAnswer(
                question_id="q_fin_sectors",
                selected_topic_ids=["indian_equities"],
                interest_level=8,
            ),
        ],
    )

    res = complete_quiz(submission)
    assert res.user_id == user.id
    assert len(res.preferences) == 3

    # Verify user record updated
    updated_user = users_repo.get_by_id(user.id)
    assert updated_user.quiz_completed is True

    # Verify fetch preferences
    pref_res = get_user_preferences(user.id)
    assert len(pref_res.preferences) == 3
    topics = {p.topic_id: p for p in pref_res.preferences}
    assert "semiconductors" in topics
    assert topics["semiconductors"].interest_score == 9


def test_complete_quiz_invalid_user_raises_404():
    """Verify 404 error when user ID does not exist."""
    submission = QuizSubmissionRequest(
        user_id="non-existent-uuid",
        answers=[QuizAnswer(question_id="q1", selected_topic_ids=["semiconductors"])],
    )
    with pytest.raises(HTTPException) as exc_info:
        complete_quiz(submission)
    assert exc_info.value.status_code == 404


def test_unsubscribe_endpoint():
    """Verify unsubscribe endpoint."""
    user = users_repo.create_or_get_user("leaving@example.com")
    assert user.subscription_status == "active"

    res = unsubscribe(UnsubscribeRequest(email="leaving@example.com"))
    assert "Successfully unsubscribed" in res["message"]

    unsubbed_user = users_repo.get_by_email("leaving@example.com")
    assert unsubbed_user.subscription_status == "unsubscribed"
