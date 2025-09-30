from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    quiz_type = Column(String, nullable=False)  # 'vocabulary', 'reading_comprehension', 'mixed'
    difficulty_level = Column(String, default='medium')
    time_limit = Column(Integer, nullable=True)  # in minutes, null = no limit
    
    # Foreign keys
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="quizzes")
    creator = relationship("User")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # 'multiple_choice', 'fill_blank', 'true_false'
    
    # For multiple choice questions
    options = Column(JSON, nullable=True)  # List of answer options
    correct_answer = Column(String, nullable=False)
    
    # For fill-in-the-blank
    blank_position = Column(Integer, nullable=True)  # Position of blank in question
    
    # Metadata
    explanation = Column(Text, nullable=True)  # Why this answer is correct
    difficulty_level = Column(String, default='medium')
    points = Column(Integer, default=1)
    order_index = Column(Integer, nullable=False)  # Order in quiz
    
    # Foreign key
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship
    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Attempt data
    answers = Column(JSON, nullable=False)  # User's answers
    score = Column(Integer, nullable=False)  # Points scored
    max_score = Column(Integer, nullable=False)  # Maximum possible points
    percentage = Column(Integer, nullable=False)  # Score percentage
    time_taken = Column(Integer, nullable=True)  # in seconds
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Timestamps
    started_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
