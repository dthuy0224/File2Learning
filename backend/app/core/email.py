import smtplib
from email.message import EmailMessage
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(subject: str, to: str, body: str) -> None:
    # Testing phase: only print to console instead of sending real email
    print(f"📨 Simulating email to {to}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return

    # After testing, remove the "return" above to activate the code below
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to
        msg.set_content(body)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)

        logger.info(f"✅ Email sent to {to} with subject '{subject}'")

    except Exception as e:
        logger.error(f"❌ Failed to send email to {to}: {e}")
        raise HTTPException(status_code=500, detail=f"Email sending failed: {e}")
