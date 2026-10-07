"""
STARTWISE AI — Base Email Provider Interface
Defines the contract for email delivery providers (SMTP, Resend).
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseEmailProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identifier for the email delivery provider."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check whether the provider has required credentials and settings."""
        pass

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Deliver an email message asynchronously.
        Must handle errors gracefully and never expose credentials or sensitive data in logs.
        """
        pass
