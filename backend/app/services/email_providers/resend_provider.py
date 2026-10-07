"""
STARTWISE AI — Resend Email Provider
Maintains backward compatibility with Resend API for transactional email delivery.
"""

from typing import Optional
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.services.email_providers.base import BaseEmailProvider

logger = get_logger(__name__)


class ResendEmailProvider(BaseEmailProvider):
    @property
    def provider_name(self) -> str:
        return "resend"

    def _get_api_key(self) -> str:
        key = settings.RESEND_API_KEY
        if hasattr(key, "get_secret_value"):
            return key.get_secret_value()
        return str(key or "").strip()

    def is_configured(self) -> bool:
        key = self._get_api_key()
        return bool(key and len(key) > 10)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Deliver email via Resend HTTP API."""
        api_key = self._get_api_key()
        if not api_key:
            logger.warning("[ResendEmailProvider] API key missing or unconfigured.")
            return False

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        from_address = settings.EMAIL_FROM or "STARTWISE AI <onboarding@resend.dev>"
        payload = {
            "from": from_address,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        if text_content:
            payload["text"] = text_content

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    domain = to_email.split("@")[-1] if "@" in to_email else "unknown"
                    logger.info(f"[ResendEmailProvider] Successfully sent email to recipient @{domain}")
                    return True
                else:
                    logger.warning(
                        f"[ResendEmailProvider] Resend API error status {response.status_code}: {response.text[:120]}"
                    )
                    return False
        except Exception as e:
            logger.error(f"[ResendEmailProvider] Failed to dispatch email via Resend API: {type(e).__name__}")
            return False
