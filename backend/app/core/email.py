import smtplib
from email.message import EmailMessage
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def send_email(subject: str, to: str, body: str, is_html: bool = False) -> None:
    """
    Gửi email hỗ trợ cả text thường và HTML.
    """
    # --- MÔI TRƯỜNG DEV/TEST (In ra console) ---
    # Nếu bạn chưa cấu hình SMTP thật, hãy giữ đoạn này để debug
    print(f"\n{'='*20} [EMAIL SIMULATION] {'='*20}")
    print(f"📨 To: {to}")
    print(f"📌 Subject: {subject}")
    print(f"📄 Body: {body[:100]}...")  # In ra 100 ký tự đầu
    print(f"{'='*60}\n")

    # Nếu đang test local mà chưa có SMTP server, hãy return tại đây
    # return

    # --- MÔI TRƯỜNG PROD (Gửi thật) ---
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to

        if is_html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)

        logger.info(f"✅ Email sent to {to}")

    except Exception as e:
        logger.error(f"❌ Failed to send email to {to}: {e}")
        # Không raise exception để tránh làm chết background task
