from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Learning preferences
    learning_goals = Column(JSON, default=list)  # ['ielts', 'toeic', 'business', 'general']
    difficulty_preference = Column(String, default='medium')  # 'easy', 'medium', 'hard'
    daily_study_time = Column(Integer, default=30)  # minutes per day

    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google', 'microsoft', 'github', etc.
    oauth_id = Column(String, nullable=True)       # Provider's unique user ID
    oauth_email = Column(String, nullable=True)    # Email from OAuth provider
    oauth_avatar = Column(String, nullable=True)   # Avatar URL from provider
    is_oauth_account = Column(Boolean, default=False)  # True if created via OAuth

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    documents = relationship("Document", back_populates="owner")
    flashcards = relationship("Flashcard", back_populates="owner")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
