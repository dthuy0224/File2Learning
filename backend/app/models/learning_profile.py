from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, DECIMAL, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    # Primary Key (One-to-One with User)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    
    # Learning Style Analysis
    learning_style = Column(String, default='balanced')
    # Options: 'visual', 'auditory', 'kinesthetic', 'reading_writing', 'balanced'
    
    preferred_difficulty = Column(String, default='medium')
    # Options: 'easy', 'medium', 'hard', 'adaptive'
    
    optimal_study_times = Column(JSON, nullable=True)
    # Example: {"morning": 0.8, "afternoon": 0.6, "evening": 0.9, "night": 0.4}
    # Performance score by time of day (0.0 - 1.0)
    
    # Performance Metrics
    avg_session_duration = Column(Integer, default=30)  # minutes
    avg_daily_study_time = Column(Integer, default=0)   # minutes
    
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    
    # Retention & Performance Rates (0.00 - 100.00)
    overall_retention_rate = Column(DECIMAL(5, 2), default=0.00)
    quiz_accuracy_rate = Column(DECIMAL(5, 2), default=0.00)
    flashcard_success_rate = Column(DECIMAL(5, 2), default=0.00)
    
    # Topic Analysis (JSON arrays)
    weak_topics = Column(JSON, nullable=True)
    # Example: [{"topic": "Grammar", "score": 45, "priority": "high", "last_attempt": "2025-11-10"}]
    
    strong_topics = Column(JSON, nullable=True)
    # Example: [{"topic": "Reading", "score": 85, "attempts": 25}]
    
    # Learning Pace
    learning_velocity = Column(DECIMAL(5, 2), default=1.00)
    # Multiplier: 0.5 = slow learner (needs more time)
    #             1.0 = normal pace
    #             1.5+ = fast learner (can handle more)
    
    recommended_daily_load = Column(Integer, default=30)  # minutes per day
    # AI-calculated optimal daily study time based on adherence & performance
    
    # Adaptation Tracking
    last_performance_analysis = Column(DateTime, nullable=True)
    last_schedule_adjustment = Column(DateTime, nullable=True)
    adaptation_count = Column(Integer, default=0)
    # Number of times schedule has been auto-adjusted
    
    # Additional Preferences
    preferred_study_days = Column(JSON, nullable=True)
    # Example: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    
    break_preference = Column(Integer, default=5)  # minutes break per 25 min study
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="learning_profile")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('overall_retention_rate >= 0 AND overall_retention_rate <= 100', 
                       name='chk_retention_rate'),
        CheckConstraint('quiz_accuracy_rate >= 0 AND quiz_accuracy_rate <= 100', 
                       name='chk_quiz_accuracy'),
        CheckConstraint('flashcard_success_rate >= 0 AND flashcard_success_rate <= 100', 
                       name='chk_flashcard_success'),
        CheckConstraint('learning_velocity > 0', name='chk_learning_velocity'),
        CheckConstraint('current_streak >= 0', name='chk_current_streak'),
        CheckConstraint('longest_streak >= 0', name='chk_longest_streak'),
        CheckConstraint('avg_session_duration > 0', name='chk_session_duration'),
        CheckConstraint('recommended_daily_load > 0', name='chk_daily_load'),
    )
    
    def __repr__(self):
        return f"<LearningProfile(user_id={self.user_id}, style={self.learning_style}, velocity={self.learning_velocity})>"


