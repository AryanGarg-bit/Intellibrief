"""Delivery service orchestrating subscriber validation, idempotency, and sending."""

from typing import Dict, Any, List
from app.repositories.users_repository import UserRecord, users_repo
from app.repositories.preferences_repository import preferences_repo
from app.repositories.articles_repository import articles_repo, ArticleModel
from app.repositories.deliveries_repository import DeliveryRecord, deliveries_repo
from app.personalization.select_stories import select_daily_stories
from app.reporting.render_email import render_email
from app.delivery.email_sender import send_email
from app.utils.time import utc_now, today_ist_date_string
from app.utils.logging import logger


def deliver_report_for_user(
    user: UserRecord,
    report_date: str,
    candidates: List[ArticleModel],
) -> Dict[str, Any]:
    """
    Deliver personalized daily report to a subscriber safely:
    - Verifies active status and completed quiz
    - Enforces idempotency to avoid duplicate sends
    - Selects 5 Finance + 5 Tech stories (with shortage notes)
    - Records delivery intent, dispatches email, and updates status
    """
    # 1. Eligibility Check
    if user.subscription_status != "active":
        return {"status": "skipped", "reason": "User is unsubscribed"}

    if not user.quiz_completed:
        return {"status": "skipped", "reason": "User has not completed quiz"}

    # 2. Idempotency Check
    idempotency_key = f"{user.id}:{report_date}:daily"
    existing = deliveries_repo.get_by_idempotency_key(idempotency_key)
    if existing and existing.status == "sent":
        logger.info(f"Skipping already sent briefing for user {user.id} on {report_date}")
        return {"status": "skipped", "reason": "Already sent for this report date"}

    # 3. Personalization & Story Selection
    preferences = preferences_repo.get_preferences(user.id)
    selection = select_daily_stories(candidates, preferences, target_per_category=5)

    all_selected_ids = [s.id for s in selection.finance_stories] + [s.id for s in selection.technology_stories]

    # 4. Record Pre-send Intent
    delivery_record = DeliveryRecord(
        user_id=user.id,
        report_date=report_date,
        article_ids=all_selected_ids,
        status="processing",
        idempotency_key=idempotency_key,
    )
    deliveries_repo.save_delivery(delivery_record)

    # 5. Render Email
    subject, html_content, text_content = render_email(
        report_date=report_date,
        selection=selection,
        user_email=user.email,
        user_id=user.id,
    )

    # 6. Dispatch Email
    send_result = send_email(
        to_email=user.email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )

    # 7. Update Record with Result
    if send_result.success:
        delivery_record.status = "sent"
        delivery_record.provider_message_id = send_result.message_id
        delivery_record.sent_at = utc_now()
        deliveries_repo.save_delivery(delivery_record)
        return {"status": "sent", "message_id": send_result.message_id, "story_count": selection.total_count}
    else:
        delivery_record.status = "failed"
        delivery_record.last_error = send_result.error
        deliveries_repo.save_delivery(delivery_record)
        return {"status": "failed", "error": send_result.error}
