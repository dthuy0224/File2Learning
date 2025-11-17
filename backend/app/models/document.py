from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # in bytes
    document_type = Column(String, nullable=False)  # 'pdf', 'docx', 'txt'
    content = Column(Text)  # extracted text content
    
    # Metadata
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    difficulty_level = Column(String, default='medium')  # 'easy', 'medium', 'hard'
    
    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Processing status
    processing_status = Column(String, default='pending')  # 'pending', 'processing', 'completed', 'failed'
    processing_error = Column(Text, nullable=True)
    key_vocabulary = Column(JSON, nullable=True)

    # Content quality metrics
    content_quality = Column(String, nullable=True)  # 'excellent', 'good', 'fair', 'poor', 'empty', 'invalid'
    quality_score = Column(Integer, nullable=True)   # 0-100 score
    language_detected = Column(String, nullable=True)  # detected language
    encoding_issues = Column(Integer, default=0)     # number of encoding issues found

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime, nullable=True)  # when processing completed
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    flashcards = relationship("Flashcard", back_populates="document")
    quizzes = relationship("Quiz", back_populates="document")
