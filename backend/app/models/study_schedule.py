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


class StudySchedule(Base):
    __tablename__ = "study_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    goal_id = Column(
        Integer, ForeignKey("learning_goals.id", ondelete="CASCADE"), nullable=True
    )

    # Schedule Configuration
    schedule_name = Column(String, nullable=False)

    schedule_type = Column(String, nullable=False)
    # Options: 'goal_based', 'time_based', 'exam_prep', 'maintenance', 'custom'

    # AI Configuration (flexible JSON)
    schedule_config = Column(JSON, nullable=False)

    # Milestones (checkpoints)
    milestones = Column(JSON, nullable=True)

    # Adaptation Settings
    adaptation_mode = Column(String, default="moderate")
    # Options: 'strict' (no auto-adjust), 'moderate', 'flexible', 'highly_adaptive'

    max_daily_load = Column(Integer, default=60)  # minutes
    min_daily_load = Column(Integer, default=15)  # minutes

    catch_up_strategy = Column(String, default="gradual")
    # Options: 'skip' (skip missed), 'gradual' (spread out), 'intensive' (cram)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    effectiveness_score = Column(DECIMAL(5, 2), nullable=True)
    # AI-calculated: 0-100, based on user adherence & performance improvement

    # Statistics
    total_days_scheduled = Column(Integer, default=0)
    days_completed = Column(Integer, default=0)
    days_missed = Column(Integer, default=0)
    days_partially_completed = Column(Integer, default=0)

    avg_adherence_rate = Column(DECIMAL(5, 2), default=0.00)  # 0-100%

    # Adjustment History
    last_adjusted_at = Column(DateTime, nullable=True)
    adjustment_reason = Column(Text, nullable=True)
    adjustment_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deactivated_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="study_schedules")
    goal = relationship("LearningGoal", back_populates="study_schedules")

    # Lưu ý: Ở đây dùng chuỗi string "DailyStudyPlan" để tham chiếu sang file kia,
    # tránh lỗi vòng lặp và không cần import class vào đây.
    daily_plans = relationship(
        "DailyStudyPlan", back_populates="schedule", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("max_daily_load >= min_daily_load", name="chk_load_range"),
        CheckConstraint(
            "adaptation_mode IN ('strict', 'moderate', 'flexible', 'highly_adaptive')",
            name="chk_adaptation_mode",
        ),
        CheckConstraint(
            "catch_up_strategy IN ('skip', 'gradual', 'intensive')",
            name="chk_catch_up_strategy",
        ),
        CheckConstraint("total_days_scheduled >= 0", name="chk_total_days"),
        CheckConstraint("days_completed >= 0", name="chk_days_completed"),
        CheckConstraint("days_missed >= 0", name="chk_days_missed"),
        CheckConstraint(
            "avg_adherence_rate >= 0 AND avg_adherence_rate <= 100",
            name="chk_adherence_rate",
        ),
    )

    def __repr__(self):
        return f"<StudySchedule(id={self.id}, name='{self.schedule_name}', active={self.is_active})>"


# Đã xóa class DailyStudyPlan ở đây
### Bước tiếp theo
