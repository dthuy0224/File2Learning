from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    
    # Flashcard content
    front_text = Column(String, nullable=False)  # Word or phrase
    back_text = Column(Text, nullable=False)     # Definition, explanation
    example_sentence = Column(Text, nullable=True)
    pronunciation = Column(String, nullable=True)  # IPA or phonetic
    word_type = Column(String, nullable=True)      # noun, verb, adjective, etc.
    
    # Spaced Repetition System (SRS) data
    ease_factor = Column(Float, default=2.5)       # SM-2 algorithm
    interval = Column(Integer, default=1)          # days until next review
    repetitions = Column(Integer, default=0)       # number of successful reviews
    next_review_date = Column(DateTime, nullable=True)
    
    # Performance tracking
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    last_review_quality = Column(Integer, nullable=True)  # 0-5 scale
    
    # Metadata
    difficulty_level = Column(String, default='medium')
    tags = Column(String, nullable=True)           # comma-separated tags
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="flashcards")
    document = relationship("Document", back_populates="flashcards")
