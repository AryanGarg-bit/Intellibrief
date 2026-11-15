"""Map quiz answers to structured user preferences."""

from typing import List, Dict
from app.schemas import QuizAnswer, PreferenceItem
from app.personalization.taxonomy import TAXONOMY


def map_answers_to_preferences(answers: List[QuizAnswer]) -> List[PreferenceItem]:
    """
    Convert a list of QuizAnswer objects into structured PreferenceItems.
    Aggregates topic selections and assigns interest scores (1-10).
    """
    topic_scores: Dict[str, int] = {}

    for ans in answers:
        # Default interest score is ans.interest_level (1-10)
        score = max(1, min(10, ans.interest_level))

        for topic_id in ans.selected_topic_ids:
            if topic_id in TAXONOMY:
                # If topic was selected multiple times across questions, boost interest
                current_score = topic_scores.get(topic_id, 0)
                topic_scores[topic_id] = min(10, max(current_score, score))

    # Convert to PreferenceItem models
    preferences: List[PreferenceItem] = []
    for topic_id, score in topic_scores.items():
        definition = TAXONOMY[topic_id]
        preferences.append(
            PreferenceItem(
                topic_id=topic_id,
                display_name=definition.display_name,
                category=definition.category,
                interest_score=score,
                keywords=definition.keywords,
            )
        )

    return preferences
