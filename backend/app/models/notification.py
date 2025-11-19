from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # 🆕 THÊM: Liên kết đến DailyPlan & Schedule
    daily_plan_id = Column(Integer, ForeignKey("daily_study_plans.id"), nullable=True)
    schedule_id = Column(Integer, ForeignKey("study_schedules.id"), nullable=True)

    title = Column(String, nullable=False)
    body = Column(String, nullable=False)

    # Thêm trường này để phân loại (reminder, achievement, system, warning, milestone)
    type = Column(String, default="system")

    # 🆕 THÊM: Loại nguồn (reminder_task, completion, goal, schedule, etc)
    source_type = Column(String, default="system")

    # 🆕 THÊM: Link hành động (ví dụ: /daily-plans/123)
    action_url = Column(String, nullable=True)

    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
