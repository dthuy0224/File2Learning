from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=True)

    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    legacy_learning_goals = Column(JSON, nullable=True)  # Old field, kept for backward compatibility
    difficulty_preference = Column(String, nullable=True)
    daily_study_time = Column(Integer, nullable=True)
    


    # OAuth fields
    oauth_provider = Column(String, nullable=True)   # 'google', 'microsoft', 'github', etc.
    oauth_id = Column(String, nullable=True)         # Provider's unique user ID
    oauth_email = Column(String, nullable=True)      # Email from OAuth provider
    oauth_avatar = Column(String, nullable=True)     # Avatar URL from provider
    is_oauth_account = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="owner")
    flashcards = relationship("Flashcard", back_populates="owner")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    
    # Adaptive Learning Relationships
    learning_profile = relationship("LearningProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    learning_goals = relationship("LearningGoal", back_populates="user", cascade="all, delete-orphan")
    study_schedules = relationship("StudySchedule", back_populates="user", cascade="all, delete-orphan")
    daily_plans = relationship("DailyStudyPlan", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    learning_analytics = relationship("LearningAnalytics", back_populates="user", cascade="all, delete-orphan")
    adaptive_recommendations = relationship("AdaptiveRecommendation", back_populates="user", cascade="all, delete-orphan")