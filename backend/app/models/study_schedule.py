from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, JSON, Boolean, DECIMAL, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudySchedule(Base):
    __tablename__ = "study_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(Integer, ForeignKey("learning_goals.id", ondelete="CASCADE"), nullable=True)
    
    # Schedule Configuration
    schedule_name = Column(String, nullable=False)
    
    schedule_type = Column(String, nullable=False)
    # Options: 'goal_based', 'time_based', 'exam_prep', 'maintenance', 'custom'
    
    # AI Configuration (flexible JSON)
    schedule_config = Column(JSON, nullable=False)
    # {
    #   "daily_minutes": 45,
    #   "days_per_week": 5,
    #   "preferred_times": ["18:00-20:00"],
    #   "activity_distribution": {"flashcards": 0.4, "quizzes": 0.3, "reading": 0.3},
    #   "difficulty_curve": "gradual" | "steep" | "adaptive",
    #   "focus_areas": ["Grammar", "Vocabulary"]
    # }
    
    # Milestones (checkpoints)
    milestones = Column(JSON, nullable=True)
    # [
    #   {"week": 1, "target": "50 words", "status": "completed", "completed_date": "2025-11-15"},
    #   {"week": 2, "target": "100 words", "status": "in_progress"}
    # ]
    
    # Adaptation Settings
    adaptation_mode = Column(String, default='moderate')
    # Options: 'strict' (no auto-adjust), 'moderate', 'flexible', 'highly_adaptive'
    
    max_daily_load = Column(Integer, default=60)  # minutes
    min_daily_load = Column(Integer, default=15)  # minutes
    
    catch_up_strategy = Column(String, default='gradual')
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
    daily_plans = relationship("DailyStudyPlan", back_populates="schedule", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("max_daily_load >= min_daily_load", name='chk_load_range'),
        CheckConstraint("adaptation_mode IN ('strict', 'moderate', 'flexible', 'highly_adaptive')", 
                       name='chk_adaptation_mode'),
        CheckConstraint("catch_up_strategy IN ('skip', 'gradual', 'intensive')", 
                       name='chk_catch_up_strategy'),
        CheckConstraint("total_days_scheduled >= 0", name='chk_total_days'),
        CheckConstraint("days_completed >= 0", name='chk_days_completed'),
        CheckConstraint("days_missed >= 0", name='chk_days_missed'),
        CheckConstraint("avg_adherence_rate >= 0 AND avg_adherence_rate <= 100", 
                       name='chk_adherence_rate'),
    )
    
    def __repr__(self):
        return f"<StudySchedule(id={self.id}, name='{self.schedule_name}', active={self.is_active})>"


class DailyStudyPlan(Base):
    __tablename__ = "daily_study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("study_schedules.id", ondelete="CASCADE"), nullable=True)
    
    # Plan Date
    plan_date = Column(Date, nullable=False, index=True)
    
    # Plan Summary (AI-generated text)
    plan_summary = Column(Text, nullable=True)
    # "Today: Review 15 flashcards (Grammar focus), take 1 vocabulary quiz, read Climate article"
    
    # Recommended Tasks (JSON array of tasks)
    recommended_tasks = Column(JSON, nullable=False)
    # [
    #   {
    #     "type": "flashcard_review",
    #     "entity_ids": [1, 5, 12, 18, 23],
    #     "count": 15,
    #     "estimated_minutes": 10,
    #     "priority": "high",
    #     "reason": "Due for review (SRS)",
    #     "topic": "Grammar"
    #   },
    #   {
    #     "type": "quiz",
    #     "entity_id": 45,
    #     "quiz_title": "Business Vocabulary",
    #     "estimated_minutes": 15,
    #     "priority": "medium",
    #     "reason": "Weak topic: Business English (avg 65%)"
    #   }
    # ]
    
    # Time Budget
    total_estimated_minutes = Column(Integer, nullable=False)
    actual_minutes_spent = Column(Integer, default=0)
    
    # Priority & Difficulty
    priority_level = Column(String, default='normal')
    # Options: 'low', 'normal', 'high', 'critical'
    
    difficulty_level = Column(String, default='medium')
    # Options: 'easy', 'medium', 'hard' - based on user's current level
    
    # Completion Status
    is_completed = Column(Boolean, default=False, index=True)
    completion_percentage = Column(DECIMAL(5, 2), default=0.00)  # 0-100%
    
    completed_tasks_count = Column(Integer, default=0)
    total_tasks_count = Column(Integer, nullable=False)
    
    # Performance Data (filled after completion)
    actual_performance = Column(JSON, nullable=True)
    # {
    #   "flashcards": {"reviewed": 15, "correct": 12, "accuracy": 0.8},
    #   "quizzes": {"completed": 1, "score": 85},
    #   "overall_accuracy": 82
    # }
    
    # Status
    status = Column(String, default='pending')
    # Options: 'pending', 'in_progress', 'completed', 'partially_completed', 'skipped'
    
    skip_reason = Column(String, nullable=True)
    # Options: 'user_skipped', 'too_busy', 'not_feeling_well', 'technical_issue'
    
    # AI Feedback
    ai_feedback = Column(Text, nullable=True)
    # "Great job! You're 20% ahead of schedule. Keep it up! 🎉"
    
    effectiveness_rating = Column(Integer, nullable=True)
    # 1-5 stars, user rates how helpful the plan was
    
    user_notes = Column(Text, nullable=True)
    # User's personal notes about the day
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="daily_plans")
    schedule = relationship("StudySchedule", back_populates="daily_plans")
    study_sessions = relationship("StudySession", back_populates="daily_plan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'partially_completed', 'skipped')", 
                       name='chk_plan_status'),
        CheckConstraint("priority_level IN ('low', 'normal', 'high', 'critical')", 
                       name='chk_priority_level'),
        CheckConstraint("difficulty_level IN ('easy', 'medium', 'hard')", 
                       name='chk_difficulty_level'),
        CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100", 
                       name='chk_completion_pct'),
        CheckConstraint("total_tasks_count > 0", name='chk_tasks_count'),
        CheckConstraint("completed_tasks_count >= 0", name='chk_completed_count'),
        CheckConstraint("effectiveness_rating IS NULL OR (effectiveness_rating >= 1 AND effectiveness_rating <= 5)", 
                       name='chk_effectiveness'),
    )
    
    def __repr__(self):
        return f"<DailyStudyPlan(id={self.id}, date={self.plan_date}, status={self.status})>"

