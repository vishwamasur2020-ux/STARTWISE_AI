"""
STARTWISE AI — SMTP Email Provider
Implements secure email delivery using Python's standard email and smtplib libraries.
Supports STARTTLS (port 587) and direct SSL (port 465) with strict certificate validation.
"""

import asyncio
import smtplib
import ssl
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.email_providers.base import BaseEmailProvider

logger = get_logger(__name__)


class SMTPEmailProvider(BaseEmailProvider):
    @property
    def provider_name(self) -> str:
        return "smtp"

    def _get_password(self) -> Optional[str]:
        """Extract unmasked password from SecretStr or plain string."""
        pwd = settings.SMTP_PASSWORD
        if hasattr(pwd, "get_secret_value"):
            return pwd.get_secret_value()
        return str(pwd) if pwd else None

    def _get_from_address(self) -> str:
        """Resolve from address and display name."""
        from_email = settings.SMTP_FROM_EMAIL or settings.EMAIL_FROM or "noreply@startwise.ai"
        # Parse if EMAIL_FROM contains "Name <email@domain>"
        parsed_name, parsed_addr = parseaddr(from_email)
        clean_addr = parsed_addr if parsed_addr else from_email
        clean_name = settings.SMTP_FROM_NAME or settings.EMAIL_FROM_NAME or parsed_name or "STARTWISE AI"
        return clean_name, clean_addr

    def is_configured(self) -> bool:
        """Check if SMTP host and credentials/settings are populated."""
        if not settings.SMTP_ENABLED:
            return False
        host = (settings.SMTP_HOST or "").strip()
        port = settings.SMTP_PORT
        user = (settings.SMTP_USERNAME or "").strip()
        pwd = self._get_password()
        # Minimum requirement: host and port specified; if auth is needed, user+pwd present
        return bool(host and port and (not user or bool(pwd)))

    def _send_smtp_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Synchronous worker executed in worker thread via asyncio.to_thread.
        Configures MIME multipart alternative message with STARTTLS or SSL.
        Strict certificate verification is maintained.
        """
        host = (settings.SMTP_HOST or "smtp.gmail.com").strip()
        port = int(settings.SMTP_PORT or 587)
        user = (settings.SMTP_USERNAME or "").strip()
        pwd = self._get_password()
        use_ssl = bool(settings.SMTP_USE_SSL or port == 465)
        use_tls = bool(settings.SMTP_USE_TLS and not use_ssl)
        timeout = int(settings.SMTP_TIMEOUT or 15)

        from_name, from_email = self._get_from_address()

        # Build MIME multipart message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((from_name, from_email))
        msg["To"] = to_email

        # Attach text fallback first, then HTML
        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
        if html_content:
            msg.attach(MIMEText(html_content, "html", "utf-8"))

        # Strict SSL context with system CA certificates (Certificate verification NEVER disabled)
        ssl_context = ssl.create_default_context()

        server = None
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(host, port, context=ssl_context, timeout=timeout)
            else:
                server = smtplib.SMTP(host, port, timeout=timeout)
                if use_tls:
                    server.starttls(context=ssl_context)

            if user and pwd:
                server.login(user, pwd)

            server.sendmail(from_email, [to_email], msg.as_string())
            domain = to_email.split("@")[-1] if "@" in to_email else "unknown"
            logger.info(f"[SMTPEmailProvider] Successfully delivered email to recipient @{domain} via {host}:{port}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"[SMTPEmailProvider] Authentication failed for user on {host}:{port} (code {e.smtp_code})")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"[SMTPEmailProvider] Connection failed to {host}:{port} (code {e.smtp_code})")
            return False
        except (socket.timeout, TimeoutError):
            logger.error(f"[SMTPEmailProvider] Connection timed out while communicating with {host}:{port}")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.warning(f"[SMTPEmailProvider] Recipient address was refused by server on {host}:{port}")
            return False
        except smtplib.SMTPSenderRefused:
            logger.warning(f"[SMTPEmailProvider] Sender address was refused by server on {host}:{port}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"[SMTPEmailProvider] SMTP protocol error ({type(e).__name__}): {str(e)[:120]}")
            return False
        except Exception as e:
            logger.error(f"[SMTPEmailProvider] Unexpected error during SMTP delivery ({type(e).__name__}): {str(e)[:120]}")
            return False
        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Asynchronously send email using smtplib offloaded to thread pool."""
        return await asyncio.to_thread(
            self._send_smtp_sync,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )
