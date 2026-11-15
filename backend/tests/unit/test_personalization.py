"""Unit tests for onboarding quiz and preference extraction."""

from app.schemas import QuizAnswer
from app.personalization.quiz import get_quiz_questions, validate_answers
from app.personalization.extract_preferences import map_answers_to_preferences


def test_get_quiz_questions():
    """Verify that quiz questions are defined and structured."""
    questions = get_quiz_questions()
    assert len(questions) >= 4
    for q in questions:
        assert "id" in q
        assert "question" in q
        assert "options" in q
        assert len(q["options"]) > 0


def test_validate_answers():
    """Verify quiz answer validation."""
    assert validate_answers([]) is False
    assert validate_answers([QuizAnswer(question_id="q1", selected_topic_ids=["semiconductors"])]) is True


def test_map_answers_to_preferences():
    """Verify mapping quiz answers to structured preferences."""
    answers = [
        QuizAnswer(
            question_id="q_fin_sectors",
            selected_topic_ids=["indian_equities", "banking_fintech"],
            interest_level=8,
        ),
        QuizAnswer(
            question_id="q_tech_sectors",
            selected_topic_ids=["semiconductors"],
            interest_level=9,
        ),
    ]

    preferences = map_answers_to_preferences(answers)

    assert len(preferences) == 3
    topics = {p.topic_id: p for p in preferences}

    assert "indian_equities" in topics
    assert topics["indian_equities"].category == "Finance"
    assert topics["indian_equities"].interest_score == 8

    assert "semiconductors" in topics
    assert topics["semiconductors"].category == "Technology"
    assert topics["semiconductors"].interest_score == 9
