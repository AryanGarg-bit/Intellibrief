"""Repository for user management (database abstraction)."""

import uuid
from typing import Dict, Optional, List
from pydantic import BaseModel
from app.utils.time import utc_now


class UserRecord(BaseModel):
    id: str
    email: str
    subscription_status: str = "active"  # 'active', 'unsubscribed', 'pending'
    quiz_completed: bool = False
    timezone: str = "Asia/Kolkata"
    created_at: str
    updated_at: str


class UsersRepository:
    """Simple in-memory user repository with basic persistence methods."""

    def __init__(self):
        # Key: user_id, Value: UserRecord
        self._users_by_id: Dict[str, UserRecord] = {}
        # Key: normalized_email, Value: user_id
        self._email_to_id: Dict[str, str] = {}

    def get_by_email(self, email: str) -> Optional[UserRecord]:
        """Find user by normalized email."""
        norm_email = email.strip().lower()
        user_id = self._email_to_id.get(norm_email)
        if user_id:
            return self._users_by_id.get(user_id)
        return None

    def get_by_id(self, user_id: str) -> Optional[UserRecord]:
        """Find user by UUID."""
        return self._users_by_id.get(user_id)

    def create_or_get_user(self, email: str) -> UserRecord:
        """Create new active subscriber or return existing record safely."""
        norm_email = email.strip().lower()
        existing = self.get_by_email(norm_email)
        if existing:
            # Re-activate if was previously unsubscribed
            if existing.subscription_status != "active":
                existing.subscription_status = "active"
                existing.updated_at = utc_now().isoformat()
            return existing

        now_str = utc_now().isoformat()
        new_user = UserRecord(
            id=str(uuid.uuid4()),
            email=norm_email,
            subscription_status="active",
            quiz_completed=False,
            timezone="Asia/Kolkata",
            created_at=now_str,
            updated_at=now_str,
        )
        self._users_by_id[new_user.id] = new_user
        self._email_to_id[norm_email] = new_user.id
        return new_user

    def mark_quiz_completed(self, user_id: str) -> Optional[UserRecord]:
        """Set quiz_completed to True."""
        user = self.get_by_id(user_id)
        if user:
            user.quiz_completed = True
            user.updated_at = utc_now().isoformat()
        return user

    def unsubscribe(self, email: str) -> bool:
        """Set subscription_status to unsubscribed."""
        user = self.get_by_email(email)
        if user:
            user.subscription_status = "unsubscribed"
            user.updated_at = utc_now().isoformat()
            return True
        return False

    def get_active_subscribers(self) -> List[UserRecord]:
        """Return all active users who completed the quiz."""
        return [
            u for u in self._users_by_id.values()
            if u.subscription_status == "active" and u.quiz_completed
        ]


# Singleton instance for local and test use
users_repo = UsersRepository()
