from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class RecommendationType(str, enum.Enum):
    REVIEW_FLASHCARD = "review_flashcard"
    STUDY_TOPIC = "study_topic"
    TAKE_QUIZ = "take_quiz"
    READ_DOCUMENT = "read_document"
    FOCUS_WEAK_AREA = "focus_weak_area"
    REINFORCE_STRENGTH = "reinforce_strength"


class RecommendationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AdaptiveRecommendation(Base):
    __tablename__ = "adaptive_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recommendation details
    type = Column(String, nullable=False, index=True)  # Store enum values as strings
    priority = Column(String, default="medium", index=True)  # Store enum values as strings
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)  # Why this recommendation was made
    
    # Target resource (optional - depends on recommendation type)
    target_resource_type = Column(String(50), nullable=True)  # 'flashcard_set', 'quiz', 'document', 'topic'
    target_resource_id = Column(Integer, nullable=True)
    
    # Recommendation scoring
    relevance_score = Column(Float, default=0.0)  # 0-1, how relevant this is
    confidence_score = Column(Float, default=0.0)  # 0-1, AI confidence in this recommendation
    expected_impact = Column(Float, default=0.0)  # 0-1, expected learning impact
    
    # User interaction
    is_viewed = Column(Integer, default=0)  # Boolean: has user seen this?
    is_accepted = Column(Integer, default=0)  # Boolean: did user accept/act on it?
    is_dismissed = Column(Integer, default=0)  # Boolean: did user dismiss it?
    
    viewed_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    
    # Custom data (renamed from 'metadata' to avoid SQLAlchemy reserved keyword)
    extra_data = Column(JSON, nullable=True)  # Additional context/data
    
    # Expiry
    expires_at = Column(DateTime, nullable=True)  # When this recommendation becomes stale
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="adaptive_recommendations")
    
    def __repr__(self):
        return f"<AdaptiveRecommendation(id={self.id}, user_id={self.user_id}, type={self.type}, priority={self.priority})>"
    
    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_active(self) -> bool:
        return not (self.is_dismissed or self.is_accepted or self.is_expired)

