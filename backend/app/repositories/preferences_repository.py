"""Repository for user preferences."""

from typing import Dict, List
from app.schemas import PreferenceItem


class PreferencesRepository:
    """Simple repository to store and retrieve user preferences."""

    def __init__(self):
        # Key: user_id, Value: List[PreferenceItem]
        self._user_preferences: Dict[str, List[PreferenceItem]] = {}

    def save_preferences(self, user_id: str, preferences: List[PreferenceItem]) -> List[PreferenceItem]:
        """Save or replace user preference items."""
        self._user_preferences[user_id] = preferences
        return preferences

    def get_preferences(self, user_id: str) -> List[PreferenceItem]:
        """Retrieve preferences for a given user ID."""
        return self._user_preferences.get(user_id, [])

    def delete_preferences(self, user_id: str) -> bool:
        """Remove preferences for a user."""
        if user_id in self._user_preferences:
            del self._user_preferences[user_id]
            return True
        return False


# Singleton instance
preferences_repo = PreferencesRepository()
