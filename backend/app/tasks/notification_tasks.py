from celery import shared_task
from sqlalchemy.orm import Session
from datetime import date
import logging

from app.core.database import SessionLocal
from app.models.user import User
from app.models.notification import Notification
from app.core.email import send_email

# Import đúng file model
from app.models.daily_plan import DailyStudyPlan

logger = logging.getLogger(__name__)


@shared_task(name="check_daily_study_progress")
def check_daily_study_progress():
    """
    Task chạy mỗi tối (20:00).
    Kiểm tra xem user đã hoàn thành bài học hôm nay chưa.
    """
    db: Session = SessionLocal()
    try:
        today = date.today()
        users = db.query(User).filter(User.is_active == True).all()
        count_reminded = 0

        logger.info(
            f"🚀 Bắt đầu kiểm tra tiến độ ngày {today} cho {len(users)} users..."
        )

        for user in users:
            # Tìm plan của hôm nay
            daily_plan = (
                db.query(DailyStudyPlan)
                .filter(
                    DailyStudyPlan.user_id == user.id,
                    # --- SỬA LỖI TẠI ĐÂY: Đổi .date thành .plan_date ---
                    DailyStudyPlan.plan_date == today,
                    # -------------------------------------------------
                )
                .first()
            )

            should_remind = False
            msg_title = ""
            msg_body = ""

            # Logic kiểm tra
            if not daily_plan:
                should_remind = True
                msg_title = "⚠️ Bạn chưa lập kế hoạch học tập!"
                msg_body = f"Xin chào {user.username or 'bạn'}, hôm nay bạn chưa thiết lập mục tiêu học tập. Hãy dành 5 phút để bắt đầu nhé!"

            elif daily_plan.status != "completed":
                should_remind = True
                msg_title = "⏰ Nhắc nhở: Hoàn thành bài học ngay!"
                msg_body = f"Xin chào {user.username or 'bạn'}, bạn vẫn chưa hoàn thành kế hoạch học tập hôm nay. Cố lên, chỉ còn một chút nữa thôi!"

            # Thực hiện gửi (nếu cần)
            if should_remind:
                # 1. Lưu thông báo vào Web
                new_notif = Notification(
                    user_id=user.id,
                    title=msg_title,
                    body=msg_body,
                    type="reminder",
                    is_read=False,
                )
                db.add(new_notif)

                # 2. Gửi Email
                if user.email:
                    html_content = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                        <h2 style="color: #d97706; text-align: center;">{msg_title}</h2>
                        <p style="font-size: 16px; color: #333;">{msg_body}</p>
                        <div style="text-align: center; margin-top: 30px;">
                            <a href="http://localhost:3000/dashboard" 
                               style="background-color: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                               Vào học ngay 🚀
                            </a>
                        </div>
                        <p style="margin-top: 30px; font-size: 12px; color: #666; text-align: center;">
                            File2Learning Automation System
                        </p>
                    </div>
                    """
                    send_email(
                        subject=msg_title,
                        to=user.email,
                        body=html_content,
                        is_html=True,
                    )

                count_reminded += 1

        db.commit()
        logger.info(f"✅ Hoàn tất. Đã nhắc nhở {count_reminded} người dùng.")
        return f"Reminded {count_reminded} users"

    except Exception as e:
        logger.error(f"❌ Lỗi trong quá trình chạy task: {e}")
        db.rollback()
    finally:
        db.close()


@shared_task(name="auto_generate_notifications")
def auto_generate_notifications():
    pass
