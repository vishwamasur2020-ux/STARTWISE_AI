"""
STARTWISE AI — Email Delivery Service
Delivers transactional emails using the existing Resend API integration.
Falls back safely to local simulation in test and development modes.
"""

from typing import Optional, List, Dict, Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_address = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
        self.enabled = settings.EMAIL_ENABLED
        # In-memory buffer for testing and dev mode verification
        self.sent_emails_history: List[Dict[str, Any]] = []

    async def send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
    ) -> bool:
        """
        Deliver email via Resend API or mock logger.
        Never reveals API keys, passwords, or raw secrets.
        """
        record = {
            "to": to_email,
            "subject": subject,
            "text": text_content,
            "html": html_content,
            "status": "pending",
        }
        self.sent_emails_history.append(record)

        # Check if live Resend delivery is configured and enabled
        is_live = bool(self.enabled and self.api_key and len(self.api_key) > 10)

        if not is_live:
            record["status"] = "simulated"
            logger.info(
                f"[EmailService Simulation] Email to '{to_email}' with subject '{subject}' simulated successfully."
            )
            return True

        # Live Resend HTTP dispatch
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": self.from_address,
            "to": [to_email],
            "subject": subject,
            "text": text_content,
        }
        if html_content:
            payload["html"] = html_content

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    record["status"] = "sent"
                    logger.info(f"[EmailService] Email sent successfully to {to_email}")
                    return True
                else:
                    record["status"] = "failed"
                    logger.warning(
                        f"[EmailService] Resend API returned status {response.status_code}: {response.text[:120]}"
                    )
                    return False
        except Exception as e:
            record["status"] = "error"
            logger.error(f"[EmailService] Failed to send email via Resend API: {e}")
            return False


# Singleton instance
email_service = EmailService()
