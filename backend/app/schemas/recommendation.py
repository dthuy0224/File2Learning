from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RecommendationType(str, Enum):
    """Types of recommendations"""
    REVIEW_FLASHCARD = "review_flashcard"
    STUDY_TOPIC = "study_topic"
    TAKE_QUIZ = "take_quiz"
    READ_DOCUMENT = "read_document"
    FOCUS_WEAK_AREA = "focus_weak_area"
    REINFORCE_STRENGTH = "reinforce_strength"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Base schema
class RecommendationBase(BaseModel):
    type: RecommendationType
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    reason: Optional[str] = None
    target_resource_type: Optional[str] = None
    target_resource_id: Optional[int] = None
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    expected_impact: float = Field(default=0.0, ge=0.0, le=1.0)
    extra_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


# Schema for creating a recommendation
class RecommendationCreate(RecommendationBase):
    pass


# Schema for updating a recommendation
class RecommendationUpdate(BaseModel):
    priority: Optional[RecommendationPriority] = None
    description: Optional[str] = None
    reason: Optional[str] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_impact: Optional[float] = Field(None, ge=0.0, le=1.0)
    extra_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


# Schema for user interaction with recommendation
class RecommendationInteraction(BaseModel):
    is_viewed: Optional[bool] = None
    is_accepted: Optional[bool] = None
    is_dismissed: Optional[bool] = None


# Schema for response
class RecommendationResponse(RecommendationBase):
    id: int
    user_id: int
    is_viewed: bool = False
    is_accepted: bool = False
    is_dismissed: bool = False
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_expired: bool = False
    is_active: bool = True

    model_config = {"from_attributes": True}


# Schema for list of recommendations
class RecommendationListResponse(BaseModel):
    total: int
    active_count: int
    recommendations: list[RecommendationResponse]


# Schema for recommendation statistics
class RecommendationStats(BaseModel):
    total_generated: int
    active_recommendations: int
    viewed_count: int
    accepted_count: int
    dismissed_count: int
    expired_count: int
    acceptance_rate: float
    by_type: Dict[str, int]
    by_priority: Dict[str, int]

