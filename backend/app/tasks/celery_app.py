from celery import Celery
from celery.schedules import crontab  # Import cái này để set giờ cụ thể
import os

celery_app = Celery(
    "file2learning",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "app.tasks.document_tasks",
        "app.tasks.notification_tasks",  # Đảm bảo dòng này có để Celery tìm thấy task
        "app.tasks.learning_tasks",
        "app.tasks.document_ai_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",  # Đổi về múi giờ Việt Nam cho chuẩn
    enable_utc=False,
)

celery_app.conf.beat_schedule = {
    # Task cũ của bạn (nếu cần giữ)
    # "auto-generate-notifs-every-minute": {
    #     "task": "auto_generate_notifications",
    #     "schedule": 60,
    # },
    # --- TASK MỚI QUAN TRỌNG ---
    "daily-study-reminder-at-8pm": {
        "task": "check_daily_study_progress",  # Tên task định nghĩa ở Bước 3
        "schedule": 60,  # crontab(hour=20, minute=0),  # Chạy lúc 20:00 mỗi ngày
    },
}
