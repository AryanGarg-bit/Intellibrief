"""Repository for recording daily news email deliveries and idempotency."""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.utils.time import utc_now


class DeliveryRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    report_date: str
    article_ids: List[str]
    status: str = "pending"  # 'pending', 'sent', 'failed', 'skipped'
    provider_message_id: Optional[str] = None
    attempt_count: int = 1
    last_error: Optional[str] = None
    idempotency_key: str
    created_at: datetime = Field(default_factory=utc_now)
    sent_at: Optional[datetime] = None


class DeliveriesRepository:
    """In-memory delivery repository tracking send attempts and idempotency."""

    def __init__(self):
        # Key: idempotency_key, Value: DeliveryRecord
        self._deliveries_by_key: Dict[str, DeliveryRecord] = {}

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[DeliveryRecord]:
        """Find delivery by unique idempotency key."""
        return self._deliveries_by_key.get(idempotency_key)

    def save_delivery(self, record: DeliveryRecord) -> DeliveryRecord:
        """Save or update delivery record."""
        self._deliveries_by_key[record.idempotency_key] = record
        return record

    def list_by_user(self, user_id: str) -> List[DeliveryRecord]:
        """List past deliveries for user."""
        return [
            d for d in self._deliveries_by_key.values()
            if d.user_id == user_id
        ]


# Singleton instance
deliveries_repo = DeliveriesRepository()
