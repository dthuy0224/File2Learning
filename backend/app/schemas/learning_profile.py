from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

# Update schema (user preferences)
class LearningProfileUpdate(BaseModel):
    """Schema for updating user preferences"""
    learning_style: Optional[str] = Field(None, description="Learning style preference")
    preferred_difficulty: Optional[str] = Field(None, description="Preferred difficulty level")
    preferred_study_days: Optional[List[str]] = Field(None, description="Preferred study days")
    break_preference: Optional[int] = Field(None, ge=1, le=30, description="Break minutes per 25min study")
    recommended_daily_load: Optional[int] = Field(None, ge=5, le=180, description="Target daily study minutes")


# Response schema
class LearningProfileResponse(BaseModel):
    """Schema for learning profile API response"""
    user_id: int
    
    # Preferences
    learning_style: str
    preferred_difficulty: str
    optimal_study_times: Optional[Dict[str, float]] = None
    
    # Performance metrics
    avg_session_duration: int
    avg_daily_study_time: int
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime] = None
    
    # Rates
    overall_retention_rate: Decimal
    quiz_accuracy_rate: Decimal
    flashcard_success_rate: Decimal
    
    # Topic analysis
    weak_topics: Optional[List[Dict[str, Any]]] = None
    strong_topics: Optional[List[Dict[str, Any]]] = None
    
    # Learning pace
    learning_velocity: Decimal
    recommended_daily_load: int
    
    # Adaptation tracking
    last_performance_analysis: Optional[datetime] = None
    last_schedule_adjustment: Optional[datetime] = None
    adaptation_count: int
    
    # Preferences
    preferred_study_days: Optional[List[str]] = None
    break_preference: int
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Dashboard stats (simplified view)
class ProfileStatsResponse(BaseModel):
    """Simplified profile stats for dashboard"""
    current_streak: int
    longest_streak: int
    total_study_time_this_week: int  # minutes
    avg_daily_study_time: int
    overall_accuracy: Decimal
    learning_velocity: Decimal
    weak_topics: List[str]  # Just topic names
    strong_topics: List[str]
    recommended_daily_minutes: int

