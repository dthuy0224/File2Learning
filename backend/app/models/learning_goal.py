from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, JSON, Boolean, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Goal Definition
    goal_type = Column(String, nullable=False)
    # Options: 'vocabulary_count', 'quiz_score', 'exam_preparation', 
    #          'time_based', 'fluency', 'topic_mastery'
    
    goal_title = Column(String, nullable=False)
    # Examples: "IELTS 6.5", "Learn 500 Business Words", "Master Grammar"
    
    description = Column(Text, nullable=True)
    
    # Target Metrics (flexible JSON for different goal types)
    target_metrics = Column(JSON, nullable=False)
    # Examples:
    # {"vocabulary": 500, "unit": "words"}
    # {"exam": "IELTS", "target_score": 6.5, "sections": ["reading", "writing"]}
    # {"study_time": 50, "unit": "hours"}
    # {"topic": "Grammar", "target_accuracy": 85}
    
    current_progress = Column(JSON, nullable=True)
    # Auto-updated by system
    # {"vocabulary": 123, "percentage": 24.6, "on_track": true, "days_active": 15}
    
    # Timeline
    start_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    actual_completion_date = Column(Date, nullable=True)
    
    # Status
    status = Column(String, default='active')
    # Options: 'draft', 'active', 'paused', 'completed', 'abandoned'
    
    priority = Column(String, default='medium')
    # Options: 'low', 'medium', 'high', 'urgent'
    
    # Tracking
    is_on_track = Column(Boolean, default=True)
    days_behind = Column(Integer, default=0)
    estimated_completion_date = Column(Date, nullable=True)
    # AI prediction based on current pace
    
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # Milestones (optional sub-goals)
    milestones = Column(JSON, nullable=True)
    # [
    #   {"week": 1, "target": "50 words", "status": "completed"},
    #   {"week": 2, "target": "100 words", "status": "in_progress"}
    # ]
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="learning_goals")
    study_schedules = relationship("StudySchedule", back_populates="goal", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("target_date >= start_date", name='chk_goal_dates'),
        CheckConstraint("status IN ('draft', 'active', 'paused', 'completed', 'abandoned')", 
                       name='chk_goal_status'),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", 
                       name='chk_goal_priority'),
        CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100", 
                       name='chk_completion_percentage'),
        CheckConstraint("days_behind >= 0", name='chk_days_behind'),
    )
    
    def __repr__(self):
        return f"<LearningGoal(id={self.id}, title='{self.goal_title}', status={self.status})>"


