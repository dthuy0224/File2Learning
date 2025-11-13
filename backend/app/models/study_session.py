from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, JSON, Boolean, DECIMAL, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudySession(Base):
    """
    Individual Study Session - tracks every learning activity
    Used for detailed analytics and AI learning pattern analysis
    """
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    daily_plan_id = Column(Integer, ForeignKey("daily_study_plans.id", ondelete="SET NULL"), nullable=True)
    
    # Session Type
    session_type = Column(String, nullable=False, index=True)
    # Options: 'flashcard_review', 'quiz_taking', 'document_reading', 
    #          'vocabulary_practice', 'grammar_exercise', 'free_practice'
    
    # Related Entity (what was studied)
    entity_type = Column(String, nullable=True)
    # Options: 'flashcard', 'flashcard_set', 'quiz', 'document'
    
    entity_id = Column(Integer, nullable=True)
    
    # Time Tracking
    duration_seconds = Column(Integer, nullable=False)
    
    started_at = Column(DateTime, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=False)
    
    # Performance Data (flexible JSON for different session types)
    performance_data = Column(JSON, nullable=True)
    
    # Aggregated Metrics (for quick queries)
    accuracy_rate = Column(DECIMAL(5, 2), nullable=True)  # 0-100%
    items_completed = Column(Integer, default=0)
    items_correct = Column(Integer, default=0)
    
    # Context
    device_type = Column(String, nullable=True)
    # Options: 'mobile', 'desktop', 'tablet'
    
    time_of_day = Column(String, nullable=True)
    # Options: 'morning', 'afternoon', 'evening', 'night'
    
    is_planned = Column(Boolean, default=False)
    # Was this part of daily plan or spontaneous practice?
    
    # Quality Metrics
    focus_score = Column(DECIMAL(5, 2), nullable=True)
    # 0-100, calculated based on response times & consistency
    
    interruptions_count = Column(Integer, default=0)
    # Number of times user paused/resumed
    
    # Topic/Category (for analytics)
    primary_topic = Column(String, nullable=True)
    # "Grammar", "Vocabulary", "Reading", "Writing", etc.
    
    difficulty_attempted = Column(String, nullable=True)
    # "easy", "medium", "hard"
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    daily_plan = relationship("DailyStudyPlan", back_populates="study_sessions")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("duration_seconds > 0", name='chk_duration'),
        CheckConstraint("ended_at > started_at", name='chk_session_times'),
        CheckConstraint("accuracy_rate IS NULL OR (accuracy_rate >= 0 AND accuracy_rate <= 100)", 
                       name='chk_accuracy'),
        CheckConstraint("focus_score IS NULL OR (focus_score >= 0 AND focus_score <= 100)", 
                       name='chk_focus'),
        CheckConstraint("items_completed >= 0", name='chk_items_completed'),
        CheckConstraint("items_correct >= 0", name='chk_items_correct'),
        CheckConstraint("interruptions_count >= 0", name='chk_interruptions'),
    )
    
    def __repr__(self):
        return f"<StudySession(id={self.id}, type={self.session_type}, duration={self.duration_seconds}s)>"


class LearningAnalytics(Base):
    """
    Daily Learning Analytics - aggregated statistics
    Pre-calculated daily stats for fast dashboard queries
    """
    __tablename__ = "learning_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    analytics_date = Column(Date, nullable=False, index=True)
    
    # Daily Summary
    total_study_minutes = Column(Integer, default=0)
    sessions_count = Column(Integer, default=0)
    
    # Activity Breakdown
    flashcards_reviewed = Column(Integer, default=0)
    flashcards_correct = Column(Integer, default=0)
    flashcard_accuracy = Column(DECIMAL(5, 2), default=0.00)  # 0-100%
    
    quizzes_taken = Column(Integer, default=0)
    quiz_avg_score = Column(DECIMAL(5, 2), default=0.00)  # 0-100%
    quiz_total_questions = Column(Integer, default=0)
    quiz_correct_answers = Column(Integer, default=0)
    
    documents_read = Column(Integer, default=0)
    words_learned = Column(Integer, default=0)  # new words added to flashcards
    
    # Performance Metrics
    overall_accuracy = Column(DECIMAL(5, 2), default=0.00)  # 0-100%
    focus_score = Column(DECIMAL(5, 2), default=0.00)  # 0-100%
    
    # Topic Performance (JSON)
    topic_performance = Column(JSON, nullable=True)
    
    # Weak Areas (identified by AI)
    identified_weak_areas = Column(JSON, nullable=True)
    # ["Present Perfect Tense", "Business Idioms", "Conditional Sentences"]
    
    # Strong Areas
    identified_strong_areas = Column(JSON, nullable=True)
    # ["Reading Comprehension", "Basic Vocabulary", "Simple Past"]
    
    # AI Recommendations
    ai_recommendations = Column(JSON, nullable=True)
    
    # Comparison Metrics
    vs_yesterday_improvement = Column(DECIMAL(5, 2), nullable=True)
    vs_week_ago_improvement = Column(DECIMAL(5, 2), nullable=True)
    vs_personal_best = Column(DECIMAL(5, 2), nullable=True)
    
    # Streak Tracking
    is_active_day = Column(Boolean, default=False)
    streak_maintained = Column(Boolean, default=False)
    daily_goal_met = Column(Boolean, default=False)
    
    # Study Pattern
    most_productive_time = Column(String, nullable=True)
    study_time_distribution = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="learning_analytics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("total_study_minutes >= 0", name='chk_study_minutes'),
        CheckConstraint("sessions_count >= 0", name='chk_sessions_count'),
        CheckConstraint("flashcards_reviewed >= 0", name='chk_flashcards_reviewed'),
        CheckConstraint("quizzes_taken >= 0", name='chk_quizzes_taken'),
        CheckConstraint("documents_read >= 0", name='chk_documents_read'),
        CheckConstraint("overall_accuracy >= 0 AND overall_accuracy <= 100", 
                       name='chk_overall_accuracy'),
    )
    
    def __repr__(self):
        return f"<LearningAnalytics(user_id={self.user_id}, date={self.analytics_date}, minutes={self.total_study_minutes})>"



