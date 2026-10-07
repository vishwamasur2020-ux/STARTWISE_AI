"""
STARTWISE AI — Unified Email Delivery Service (Provider-Based Architecture)
Orchestrates email dispatch across configurable providers:
- SMTP (Default, via standard smtplib + email MIME with STARTTLS/SSL)
- Resend (HTTP API provider)
- Automated Test / Local Simulation Fallback
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from app.core.config import settings
from app.core.logging import get_logger
from app.services.email_providers.base import BaseEmailProvider
from app.services.email_providers.smtp_provider import SMTPEmailProvider
from app.services.email_providers.resend_provider import ResendEmailProvider

logger = get_logger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_provider = SMTPEmailProvider()
        self.resend_provider = ResendEmailProvider()
        # In-memory buffer for automated testing, inspection, and verification
        self.sent_emails_history: List[Dict[str, Any]] = []

    def get_provider(self, name: Optional[str] = None) -> BaseEmailProvider:
        """Resolve active email provider instance based on name or configuration."""
        provider_name = (name or settings.EMAIL_PROVIDER or "smtp").lower().strip()
        if provider_name == "smtp":
            return self.smtp_provider
        elif provider_name == "resend":
            return self.resend_provider
        else:
            logger.warning(
                f"[EmailService] Unknown provider '{provider_name}'. Defaulting to SMTP provider."
            )
            return self.smtp_provider

    def is_configured(self) -> bool:
        """Return True if active email provider is properly configured."""
        if not settings.EMAIL_ENABLED:
            return False
        return self.get_provider().is_configured()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """
        Deliver an email using the configured provider (SMTP or Resend).
        Handles argument ordering flexibly for backward compatibility.
        Falls back to local simulation in test and unconfigured environments.
        Never logs passwords, tokens, or OTP codes.
        """
        # Accommodate callers passing (to_email, subject, text_content, html_content)
        # by checking if html_content doesn't have HTML tags but text_content does
        if html_content and not text_content:
            if not any(tag in html_content for tag in ("<html", "<body", "<p", "<div", "<table")):
                text_content = html_content
                html_content = kwargs.get("html_content")

        # Fallback text content if only HTML provided
        effective_html = html_content or ""
        effective_text = text_content or kwargs.get("text_content") or ""

        active_provider = self.get_provider()
        provider_name = active_provider.provider_name

        record: Dict[str, Any] = {
            "to": to_email,
            "subject": subject,
            "html": effective_html,
            "text": effective_text,
            "provider": provider_name,
            "status": "pending",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.sent_emails_history.append(record)

        # In dev/test or when disabled/unconfigured, run simulation mode
        should_live_dispatch = bool(settings.EMAIL_ENABLED and active_provider.is_configured())

        if not should_live_dispatch:
            record["status"] = "simulated"
            domain = to_email.split("@")[-1] if "@" in to_email else "recipient"
            logger.info(
                f"[EmailService Simulation] Simulated dispatch to @{domain} via provider '{provider_name}'."
            )
            return True

        # Live dispatch via active provider
        try:
            success = await active_provider.send_email(
                to_email=to_email,
                subject=subject,
                html_content=effective_html,
                text_content=effective_text,
            )
            if success:
                record["status"] = "sent"
                return True
            else:
                record["status"] = "failed"
                # Optional fallback to Resend if SMTP failed and Resend is configured
                if provider_name == "smtp" and self.resend_provider.is_configured():
                    logger.info("[EmailService] SMTP delivery failed. Attempting fallback to Resend...")
                    fallback_success = await self.resend_provider.send_email(
                        to_email=to_email,
                        subject=subject,
                        html_content=effective_html,
                        text_content=effective_text,
                    )
                    if fallback_success:
                        record["status"] = "sent_via_fallback"
                        record["fallback_provider"] = "resend"
                        return True
                return False

        except Exception as e:
            record["status"] = "error"
            logger.error(
                f"[EmailService] Unexpected failure in provider '{provider_name}': {type(e).__name__}"
            )
            return False

    def clear_history(self) -> None:
        """Reset sent emails history buffer."""
        self.sent_emails_history.clear()


# Global Singleton Instance
email_service = EmailService()
