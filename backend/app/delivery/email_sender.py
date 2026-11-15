"""Email sender interface with Resend adapter and mock local fallback."""

from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.utils.logging import logger


class SendResult:
    """Standardized delivery result."""

    def __init__(self, success: bool, message_id: Optional[str] = None, error: Optional[str] = None):
        self.success = success
        self.message_id = message_id
        self.error = error


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str,
) -> SendResult:
    """
    Send an email via Resend if RESEND_API_KEY is configured;
    otherwise logs a mock send locally for development and testing.
    """
    if not settings.resend_api_key or settings.resend_api_key == "replace_me":
        # Mock delivery for local development and testing
        mock_id = f"mock_msg_{hash(to_email + subject) % 100000}"
        logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: '{subject}' | MockID: {mock_id}")
        return SendResult(success=True, message_id=mock_id)

    # Real Resend API delivery
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": settings.email_from,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }

        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            if resp.status_code in (200, 201):
                data = resp.json()
                return SendResult(success=True, message_id=data.get("id"))
            else:
                err_msg = f"Resend error HTTP {resp.status_code}: {resp.text}"
                logger.error(err_msg)
                return SendResult(success=False, error=err_msg)
    except Exception as e:
        err_msg = f"Network exception during email send: {e}"
        logger.error(err_msg)
        return SendResult(success=False, error=err_msg)
