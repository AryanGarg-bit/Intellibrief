"""Subscription and quiz onboarding routes."""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    SubscribeRequest,
    SubscribeResponse,
    UnsubscribeRequest,
    QuizSubmissionRequest,
    UserPreferencesResponse,
    PreferenceItem,
)
from app.repositories.users_repository import users_repo
from app.repositories.preferences_repository import preferences_repo
from app.personalization.quiz import get_quiz_questions, validate_answers
from app.personalization.extract_preferences import map_answers_to_preferences

router = APIRouter(prefix="/api", tags=["Subscriptions & Preferences"])


@router.post("/subscriptions", response_model=SubscribeResponse, status_code=status.HTTP_200_OK)
def subscribe(request: SubscribeRequest) -> SubscribeResponse:
    """
    Subscribe a user with email address.
    Normalizes email and creates or returns existing user record.
    """
    clean_email = request.email.strip().lower()
    user = users_repo.create_or_get_user(clean_email)

    message = (
        "Welcome! Please complete the short preference quiz to start your daily feed."
        if not user.quiz_completed
        else "Subscription active. Your daily briefing is scheduled for 07:00 IST."
    )

    return SubscribeResponse(
        user_id=user.id,
        email=user.email,
        subscription_status=user.subscription_status,
        quiz_completed=user.quiz_completed,
        message=message,
    )


@router.get("/quiz/questions", response_model=List[Dict[str, Any]])
def get_questions() -> List[Dict[str, Any]]:
    """Return the 5-10 question onboarding quiz."""
    return get_quiz_questions()


@router.post("/quiz/complete", response_model=UserPreferencesResponse)
def complete_quiz(submission: QuizSubmissionRequest) -> UserPreferencesResponse:
    """
    Validate quiz answers, derive structured preferences,
    persist them, and mark user onboarding as complete.
    """
    user = users_repo.get_by_id(submission.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not validate_answers(submission.answers):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz answers cannot be empty",
        )

    # Convert answers to structured preferences
    preferences = map_answers_to_preferences(submission.answers)

    # Save preferences and update user status
    preferences_repo.save_preferences(submission.user_id, preferences)
    users_repo.mark_quiz_completed(submission.user_id)

    return UserPreferencesResponse(
        user_id=submission.user_id,
        preferences=preferences,
    )


@router.get("/preferences/{user_id}", response_model=UserPreferencesResponse)
def get_user_preferences(user_id: str) -> UserPreferencesResponse:
    """Retrieve stored preferences for a user."""
    user = users_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    prefs = preferences_repo.get_preferences(user_id)
    return UserPreferencesResponse(
        user_id=user_id,
        preferences=prefs,
    )


@router.post("/subscriptions/unsubscribe")
def unsubscribe(request: UnsubscribeRequest) -> Dict[str, str]:
    """Unsubscribe a user by email."""
    clean_email = request.email.strip().lower()
    success = users_repo.unsubscribe(clean_email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email address not found in subscribers",
        )

    return {"message": "Successfully unsubscribed. You will not receive future briefings."}
