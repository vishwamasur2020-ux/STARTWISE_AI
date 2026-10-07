"""
STARTWISE AI — Email Template Service
Generates professional branded transactional email templates:
- Email Verification OTP
- Password Reset OTP
- Password Changed Security Notification
"""

from typing import Tuple


class EmailTemplateService:
    @staticmethod
    def _base_html(title: str, content: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #0b0f19;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #e2e8f0;
    }}
    .wrapper {{
      max-width: 580px;
      margin: 32px auto;
      background: #111827;
      border: 1px solid #1f2937;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }}
    .header {{
      background: linear-gradient(135deg, #0e7490 0%, #1d4ed8 50%, #4338ca 100%);
      padding: 32px 28px;
      text-align: center;
    }}
    .logo {{
      color: #ffffff;
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 0.5px;
      margin: 0;
    }}
    .subtitle {{
      color: #a5f3fc;
      font-size: 13px;
      font-weight: 500;
      margin-top: 6px;
    }}
    .body {{
      padding: 36px 32px;
    }}
    .greeting {{
      font-size: 17px;
      font-weight: 600;
      color: #ffffff;
      margin-top: 0;
      margin-bottom: 14px;
    }}
    .text {{
      font-size: 14px;
      line-height: 1.6;
      color: #94a3b8;
      margin: 12px 0;
    }}
    .otp-box {{
      margin: 28px 0;
      padding: 22px;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      text-align: center;
    }}
    .otp-label {{
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: #38bdf8;
      margin-bottom: 8px;
    }}
    .otp-code {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 34px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #ffffff;
      margin: 0;
    }}
    .expiry {{
      font-size: 12px;
      color: #64748b;
      margin-top: 8px;
    }}
    .footer {{
      padding: 24px 32px;
      background: #0d131f;
      border-top: 1px solid #1e293b;
      text-align: center;
      font-size: 12px;
      color: #64748b;
    }}
    .signature {{
      margin-top: 24px;
      font-size: 13px;
      color: #cbd5e1;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1 class="logo">STARTWISE AI</h1>
      <p class="subtitle">Intelligent Startup Validation & Recommendation System</p>
    </div>
    <div class="body">
      {content}
      <div class="signature">
        Regards,<br>
        <strong>STARTWISE AI Team</strong>
      </div>
    </div>
    <div class="footer">
      © STARTWISE AI. All rights reserved.<br>
      This is an automated system email. Please do not reply directly.
    </div>
  </div>
</body>
</html>"""

    @classmethod
    def get_verification_email(cls, name: str, otp: str, expiry_minutes: int = 10) -> Tuple[str, str, str]:
        """Returns (subject, text_content, html_content) for email verification."""
        display_name = name.strip() if name else "Founder"
        subject = "Verify your STARTWISE AI account"

        text_content = (
            f"Hello {display_name},\n\n"
            f"Welcome to STARTWISE AI.\n\n"
            f"Your verification code is:\n\n"
            f"{otp}\n\n"
            f"This code expires in {expiry_minutes} minutes.\n\n"
            f"If you did not create this account, you can safely ignore this email.\n\n"
            f"Regards,\n"
            f"STARTWISE AI Team\n"
        )

        html_body = f"""
      <p class="greeting">Hello {display_name},</p>
      <p class="text">Welcome to <strong>STARTWISE AI</strong>. Thank you for joining our platform to validate business ideas and explore franchise intelligence.</p>
      <div class="otp-box">
        <div class="otp-label">Your Verification Code</div>
        <p class="otp-code">{otp}</p>
        <div class="expiry">Expires in {expiry_minutes} minutes • Never share this code</div>
      </div>
      <p class="text">If you did not create this account, you can safely ignore this email.</p>
"""
        html_content = cls._base_html(subject, html_body)
        return subject, text_content, html_content

    @classmethod
    def get_password_reset_email(cls, name: str, otp: str, expiry_minutes: int = 10) -> Tuple[str, str, str]:
        """Returns (subject, text_content, html_content) for password reset."""
        display_name = name.strip() if name else "User"
        subject = "Reset your STARTWISE AI password"

        text_content = (
            f"Hello {display_name},\n\n"
            f"We received a request to reset your STARTWISE AI password.\n\n"
            f"Your verification code is:\n\n"
            f"{otp}\n\n"
            f"This code expires in {expiry_minutes} minutes.\n\n"
            f"If you did not request this, you can safely ignore this email.\n\n"
            f"Regards,\n"
            f"STARTWISE AI Team\n"
        )

        html_body = f"""
      <p class="greeting">Hello {display_name},</p>
      <p class="text">We received a request to reset the password for your STARTWISE AI account.</p>
      <div class="otp-box">
        <div class="otp-label">Password Reset Code</div>
        <p class="otp-code">{otp}</p>
        <div class="expiry">Expires in {expiry_minutes} minutes • Never share this code with anyone</div>
      </div>
      <p class="text">If you did not request this, you can safely ignore this email. Your existing password remains secure.</p>
"""
        html_content = cls._base_html(subject, html_body)
        return subject, text_content, html_content

    @classmethod
    def get_password_changed_notification(cls, name: str) -> Tuple[str, str, str]:
        """Returns (subject, text_content, html_content) for security alert on password change."""
        display_name = name.strip() if name else "User"
        subject = "Your STARTWISE AI password was changed"

        text_content = (
            f"Hello {display_name},\n\n"
            f"Your STARTWISE AI password was successfully changed.\n\n"
            f"If you did not perform this change, please contact our security team immediately.\n\n"
            f"Regards,\n"
            f"STARTWISE AI Team\n"
        )

        html_body = f"""
      <p class="greeting">Hello {display_name},</p>
      <p class="text">Your STARTWISE AI password was successfully changed.</p>
      <p class="text">All existing authentication sessions have been revoked for your security.</p>
      <p class="text" style="color: #f87171;">If you did not perform this change, please contact our security team immediately.</p>
"""
        html_content = cls._base_html(subject, html_body)
        return subject, text_content, html_content
