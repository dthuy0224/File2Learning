# app/tasks/notification_tasks.py
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.crud import crud_notification
from app.schemas.notification import NotificationCreate
from app.models.user import User

@celery_app.task(name="auto_generate_notifications")
def auto_generate_notifications():
    """
    Mỗi phút task này sẽ chạy và tạo thông báo mới cho user.
    Sau này bạn chỉ cần thay logic check điều kiện là được.
    """
    db: Session = SessionLocal()

    try:
        # Lấy tất cả user (bạn có thể filter theo active)
        users = db.query(User).all()

        created = 0

        for user in users:

            # --- LOGIC TẠM THỜI ---
            # Ví dụ: Mỗi phút gửi 1 thông báo cho mỗi user để test
            notif_data = NotificationCreate(
                user_id=user.id,
                title="Thông báo mới tự động",
                body="Đây là thông báo được Celery tạo tự động.",
            )
            crud_notification.create_notification(db, notif_data)
            created += 1

        print(f"[Celery] Created {created} notifications.")

        return {"created": created}

    except Exception as e:
        print("❌ Celery error:", e)
        return {"error": str(e)}

    finally:
        db.close()
