from celery import shared_task
from sqlalchemy.orm import Session
from datetime import date
import logging

from app.core.database import SessionLocal
from app.models.user import User
from app.models.notification import Notification
from app.core.email import send_email
from app.crud import crud_notification

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
                    DailyStudyPlan.plan_date == today,
                )
                .first()
            )

            should_remind = False
            msg_title = ""
            msg_body = ""
            notification_type = "reminder"

            # Logic kiểm tra
            if not daily_plan:
                should_remind = True
                msg_title = "⚠️ Bạn chưa lập kế hoạch học tập!"
                msg_body = f"Xin chào {user.username or 'bạn'}, hôm nay bạn chưa thiết lập mục tiêu học tập. Hãy dành 5 phút để bắt đầu nhé!"
                notification_type = "warning"

            elif daily_plan.status != "completed":
                should_remind = True
                msg_title = "⏰ Nhắc nhở: Hoàn thành bài học ngay!"
                msg_body = f"Xin chào {user.username or 'bạn'}, bạn vẫn chưa hoàn thành kế hoạch học tập hôm nay. Cố lên, chỉ còn một chút nữa thôi!"
                notification_type = "reminder"

            # Thực hiện gửi (nếu cần)
            if should_remind:
                # 1. Lưu thông báo vào Web (với tất cả fields mới)
                notif = crud_notification.create_notification_full(
                    db=db,
                    user_id=user.id,
                    title=msg_title,
                    body=msg_body,
                    type=notification_type,
                    source_type="reminder_task",
                    daily_plan_id=daily_plan.id if daily_plan else None,
                    schedule_id=daily_plan.schedule_id if daily_plan else None,
                    action_url=(
                        f"/daily-plans/{daily_plan.id}" if daily_plan else "/dashboard"
                    ),
                )

                # 2. Gửi Email
                if user.email:
                    html_content = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                        <h2 style="color: #d97706; text-align: center;">{msg_title}</h2>
                        <p style="font-size: 16px; color: #333;">{msg_body}</p>
                        <div style="text-align: center; margin-top: 30px;">
                            <a href="http://localhost:3000{notif.action_url}" 
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

    except Exception as e:
        logger.error(f"❌ Error in check_daily_study_progress: {e}")
    finally:
        db.close()


# 🆕 THÊM: Task gửi completion notification
@shared_task(name="send_completion_notification")
def send_completion_notification(user_id: int, daily_plan_id: int):
    """
    Gửi thông báo/email khi user hoàn thành plan
    """
    db: Session = SessionLocal()
    try:
        from app.models.user import User as UserModel

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        plan = (
            db.query(DailyStudyPlan).filter(DailyStudyPlan.id == daily_plan_id).first()
        )

        if not user or not plan:
            return

        msg_title = "🎉 Chúc mừng! Bạn đã hoàn thành kế hoạch học tập!"
        msg_body = f"Tuyệt vời {user.username or 'bạn'}! Bạn đã hoàn thành bài học hôm nay với {plan.completion_percentage:.0f}% tiến độ. Tiếp tục cố gắng nhé!"

        # 1. Tạo notification
        notif = crud_notification.create_notification_full(
            db=db,
            user_id=user.id,
            title=msg_title,
            body=msg_body,
            type="achievement",
            source_type="completion",
            daily_plan_id=plan.id,
            schedule_id=plan.schedule_id,
            action_url=f"/daily-plans/{plan.id}",
        )

        # 2. Gửi email
        if user.email:
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h2 style="color: #fff; text-align: center;">{msg_title}</h2>
                <p style="font-size: 16px; color: #fff;">{msg_body}</p>
                <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <p style="margin: 5px 0;"><strong>Tiến độ:</strong> {plan.completion_percentage:.0f}%</p>
                    <p style="margin: 5px 0;"><strong>Thời gian:</strong> {plan.actual_minutes_spent} phút</p>
                    <p style="margin: 5px 0;"><strong>Nhiệm vụ hoàn thành:</strong> {plan.completed_tasks_count}/{plan.total_tasks_count}</p>
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:3000{notif.action_url}" 
                       style="background-color: #fff; color: #667eea; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                       Xem Chi Tiết 📊
                    </a>
                </div>
                <p style="margin-top: 30px; font-size: 12px; color: #fff; text-align: center;">
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

        logger.info(
            f"✅ Sent completion notification to user {user_id} for plan {daily_plan_id}"
        )

    except Exception as e:
        logger.error(f"❌ Error in send_completion_notification: {e}")
    finally:
        db.close()


@shared_task(name="auto_generate_notifications")
def auto_generate_notifications():
    pass
