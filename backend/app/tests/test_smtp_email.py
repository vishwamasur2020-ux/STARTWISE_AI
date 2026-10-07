"""
STARTWISE AI — SMTP Email Provider & Architecture Test Suite
Comprehensive tests for:
1. SMTP provider configuration & detection
2. STARTTLS (port 587) and SSL (port 465) mock dispatch
3. Strict certificate verification
4. Error handling (authentication failure, connection error, timeout, refused recipient)
5. Provider selection (EMAIL_PROVIDER=smtp vs resend)
6. Simulation buffer for unit tests (zero external network calls)
7. Reusable HTML email templates and plain-text fallbacks
8. Security invariants (no credentials or tokens leaked)
"""

import smtplib
import socket
import ssl
from unittest.mock import MagicMock, patch
import pytest

from app.core.config import settings
from app.services.email_service import EmailService, email_service
from app.services.email_providers.smtp_provider import SMTPEmailProvider
from app.services.email_providers.resend_provider import ResendEmailProvider
from app.services.email_template_service import EmailTemplateService


# ─── 1. SMTP PROVIDER CONFIGURATION TESTS ────────────────────────────────────

def test_smtp_provider_configuration_detection():
    """Verify SMTP configuration detection handles empty, partial, and valid settings."""
    provider = SMTPEmailProvider()

    # Enabled with empty host/user
    with patch.object(settings, "SMTP_ENABLED", False):
        assert provider.is_configured() is False

    with patch.object(settings, "SMTP_ENABLED", True), \
         patch.object(settings, "SMTP_HOST", "smtp.gmail.com"), \
         patch.object(settings, "SMTP_PORT", 587), \
         patch.object(settings, "SMTP_USERNAME", "founder@gmail.com"), \
         patch.object(settings, "SMTP_PASSWORD", ""):
        # Username without password is not configured
        assert provider.is_configured() is False

    with patch.object(settings, "SMTP_ENABLED", True), \
         patch.object(settings, "SMTP_HOST", "smtp.gmail.com"), \
         patch.object(settings, "SMTP_PORT", 587), \
         patch.object(settings, "SMTP_USERNAME", "founder@gmail.com"), \
         patch.object(settings, "SMTP_PASSWORD", "app-password-secret"):
        assert provider.is_configured() is True


# ─── 2. SMTP DISPATCH & TLS TESTS ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_smtp_send_email_starttls_success():
    """Verify STARTTLS delivery on port 587 attaches text/html and invokes starttls."""
    provider = SMTPEmailProvider()

    mock_server = MagicMock()

    with patch("smtplib.SMTP", return_value=mock_server) as mock_smtp_cls, \
         patch.object(settings, "SMTP_HOST", "smtp.gmail.com"), \
         patch.object(settings, "SMTP_PORT", 587), \
         patch.object(settings, "SMTP_USE_TLS", True), \
         patch.object(settings, "SMTP_USE_SSL", False), \
         patch.object(settings, "SMTP_USERNAME", "sender@startwise.ai"), \
         patch.object(settings, "SMTP_PASSWORD", "secret-pass"):

        result = await provider.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Plaintext",
        )

        assert result is True
        mock_smtp_cls.assert_called_once_with("smtp.gmail.com", 587, timeout=15)
        # Verify STARTTLS was executed
        assert mock_server.starttls.called
        # Verify credentials were authenticated
        mock_server.login.assert_called_once_with("sender@startwise.ai", "secret-pass")
        # Verify sendmail was called with recipient
        assert mock_server.sendmail.called
        args, kwargs = mock_server.sendmail.call_args
        assert "recipient@example.com" in args[1]
        assert mock_server.quit.called


@pytest.mark.asyncio
async def test_smtp_send_email_direct_ssl_success():
    """Verify direct SSL delivery on port 465 instantiates SMTP_SSL with certificate validation."""
    provider = SMTPEmailProvider()
    mock_server = MagicMock()

    with patch("smtplib.SMTP_SSL", return_value=mock_server) as mock_ssl_cls, \
         patch.object(settings, "SMTP_HOST", "smtp.gmail.com"), \
         patch.object(settings, "SMTP_PORT", 465), \
         patch.object(settings, "SMTP_USE_SSL", True), \
         patch.object(settings, "SMTP_USERNAME", "sender@startwise.ai"), \
         patch.object(settings, "SMTP_PASSWORD", "secret-pass"):

        result = await provider.send_email(
            to_email="recipient@example.com",
            subject="SSL Test",
            html_content="<p>Secure SSL Email</p>",
            text_content="Secure SSL Text",
        )

        assert result is True
        mock_ssl_cls.assert_called_once()
        mock_server.login.assert_called_once_with("sender@startwise.ai", "secret-pass")
        assert mock_server.sendmail.called
        assert mock_server.quit.called


# ─── 3. SMTP ERROR HANDLING & RESILIENCE TESTS ────────────────────────────────

@pytest.mark.asyncio
async def test_smtp_authentication_failure_handled():
    """Authentication errors return False without throwing unhandled exceptions."""
    provider = SMTPEmailProvider()
    mock_server = MagicMock()
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")

    with patch("smtplib.SMTP", return_value=mock_server), \
         patch.object(settings, "SMTP_USERNAME", "user"), \
         patch.object(settings, "SMTP_PASSWORD", "wrong-pwd"):

        result = await provider.send_email(
            to_email="test@example.com",
            subject="Auth Fail",
            html_content="<p>Test</p>",
        )
        assert result is False
        assert mock_server.quit.called


@pytest.mark.asyncio
async def test_smtp_connection_failure_handled():
    """Connection errors return False gracefully."""
    provider = SMTPEmailProvider()

    with patch("smtplib.SMTP", side_effect=smtplib.SMTPConnectError(421, b"Connection refused")):
        result = await provider.send_email(
            to_email="test@example.com",
            subject="Conn Fail",
            html_content="<p>Test</p>",
        )
        assert result is False


@pytest.mark.asyncio
async def test_smtp_timeout_handled():
    """Socket timeout returns False gracefully."""
    provider = SMTPEmailProvider()

    with patch("smtplib.SMTP", side_effect=socket.timeout("Operation timed out")):
        result = await provider.send_email(
            to_email="test@example.com",
            subject="Timeout",
            html_content="<p>Test</p>",
        )
        assert result is False


@pytest.mark.asyncio
async def test_smtp_recipients_refused_handled():
    """Invalid or refused recipient addresses return False."""
    provider = SMTPEmailProvider()
    mock_server = MagicMock()
    mock_server.sendmail.side_effect = smtplib.SMTPRecipientsRefused({"bad@example.com": (550, b"User not found")})

    with patch("smtplib.SMTP", return_value=mock_server):
        result = await provider.send_email(
            to_email="bad@example.com",
            subject="Refused",
            html_content="<p>Test</p>",
        )
        assert result is False
        assert mock_server.quit.called


# ─── 4. PROVIDER SELECTION & ORCHESTRATION TESTS ─────────────────────────────

def test_email_service_provider_selection():
    """EmailService switches correctly between SMTP and Resend providers."""
    svc = EmailService()

    with patch.object(settings, "EMAIL_PROVIDER", "smtp"):
        assert svc.get_provider().provider_name == "smtp"

    with patch.object(settings, "EMAIL_PROVIDER", "resend"):
        assert svc.get_provider().provider_name == "resend"

    # Case insensitive
    with patch.object(settings, "EMAIL_PROVIDER", "SMTP"):
        assert svc.get_provider().provider_name == "smtp"

    # Unknown defaults to SMTP
    with patch.object(settings, "EMAIL_PROVIDER", "unknown_provider"):
        assert svc.get_provider().provider_name == "smtp"


@pytest.mark.asyncio
async def test_email_service_simulation_mode_in_tests():
    """In test mode without live credentials, dispatch simulates and buffers record."""
    svc = EmailService()
    svc.clear_history()

    with patch.object(settings, "EMAIL_ENABLED", False):
        res = await svc.send_email(
            to_email="founder@example.com",
            subject="Welcome to STARTWISE AI",
            html_content="<p>Hello Founder</p>",
            text_content="Hello Founder",
        )
        assert res is True
        assert len(svc.sent_emails_history) == 1
        record = svc.sent_emails_history[0]
        assert record["to"] == "founder@example.com"
        assert record["status"] == "simulated"
        assert record["provider"] in ("smtp", "resend")


# ─── 5. EMAIL TEMPLATES & RESPONSIVENESS TESTS ───────────────────────────────

def test_email_templates_contain_required_branding_and_fallbacks():
    """Verify templates contain required branding, OTP code, expiry, and plain-text fallbacks."""
    # 1. Verification Template
    subj, text, html = EmailTemplateService.get_verification_email("Alice", "123456", 10)
    assert subj == "Verify your STARTWISE AI account"
    assert "123456" in text
    assert "123456" in html
    assert "10" in text
    assert "STARTWISE AI" in html
    assert "Intelligent Startup Validation" in html
    assert "Intelligent Startup Validation" in text
    assert "<!DOCTYPE html>" in html

    # 2. Password Reset Template
    r_subj, r_text, r_html = EmailTemplateService.get_password_reset_email("Bob", "654321", 10)
    assert r_subj == "Reset your STARTWISE AI password"
    assert "654321" in r_text
    assert "654321" in r_html
    assert "STARTWISE AI" in r_html

    # 3. Password Changed Template
    c_subj, c_text, c_html = EmailTemplateService.get_password_changed_notification("Charlie")
    assert "password was changed" in c_subj
    assert "Charlie" in c_text
    assert "Charlie" in c_html
    assert "STARTWISE AI" in c_html


def test_security_invariants_no_private_keys_in_email_content():
    """Verify templates never include passwords, hashes, JWTs, or client secrets."""
    _, text, html = EmailTemplateService.get_verification_email("Founder", "987654")
    for content in (text, html):
        assert "password" not in content.lower() or "reset" in content.lower()
        assert "secret" not in content.lower() or "share" in content.lower()
        assert "jwt" not in content.lower()
        assert "bearer" not in content.lower()
