from celery import Celery
import os

# Celery configuration
celery_app = Celery(
    "file2learning",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "app.tasks.document_tasks",  # task cũ
        "app.tasks.notification_tasks"  # thêm dòng này
    ]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "auto-generate-notifs-every-minute": {
        "task": "auto_generate_notifications",
        "schedule": 60,
    }
}
