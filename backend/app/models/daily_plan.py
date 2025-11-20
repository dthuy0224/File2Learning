from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    DECIMAL,
    CheckConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class DailyStudyPlan(Base):
    __tablename__ = "daily_study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schedule_id = Column(
        Integer, ForeignKey("study_schedules.id", ondelete="CASCADE"), nullable=True
    )

    plan_date = Column(Date, nullable=False, index=True)
    plan_summary = Column(Text, nullable=True)
    recommended_tasks = Column(JSON, nullable=True)
    source_recommendation_ids = Column(JSON, nullable=True)

    total_estimated_minutes = Column(Integer, default=0)
    actual_minutes_spent = Column(Integer, default=0)

    priority_level = Column(String, default="normal")
    difficulty_level = Column(String, default="medium")

    is_completed = Column(Boolean, default=False, index=True)
    completion_percentage = Column(DECIMAL(5, 2), default=0.00)

    completed_tasks_count = Column(Integer, default=0)
    total_tasks_count = Column(Integer, default=0)

    actual_performance = Column(JSON, nullable=True)

    status = Column(String, default="pending")
    skip_reason = Column(String, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    effectiveness_rating = Column(Integer, nullable=True)
    user_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="daily_plans")
    schedule = relationship("StudySchedule", back_populates="daily_plans")

    # --- SỬA LỖI TẠI ĐÂY: BỎ COMMENT DÒNG NÀY ---
    # Sử dụng chuỗi "StudySession" để tránh import vòng lặp
    study_sessions = relationship(
        "StudySession", back_populates="daily_plan", cascade="all, delete-orphan"
    )
    # --------------------------------------------

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'partially_completed', 'skipped')",
            name="chk_plan_status",
        ),
        CheckConstraint(
            "priority_level IN ('low', 'normal', 'high', 'critical')",
            name="chk_priority_level",
        ),
        CheckConstraint(
            "difficulty_level IN ('easy', 'medium', 'hard')",
            name="chk_difficulty_level",
        ),
        CheckConstraint(
            "completion_percentage >= 0 AND completion_percentage <= 100",
            name="chk_completion_pct",
        ),
        CheckConstraint("total_tasks_count > 0", name="chk_tasks_count"),
        CheckConstraint("completed_tasks_count >= 0", name="chk_completed_count"),
        CheckConstraint(
            "effectiveness_rating IS NULL OR (effectiveness_rating >= 1 AND effectiveness_rating <= 5)",
            name="chk_effectiveness",
        ),
    )

    def __repr__(self):
        return f"<DailyStudyPlan(id={self.id}, date={self.plan_date}, status={self.status})>"
