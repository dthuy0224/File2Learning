from typing import Optional, Dict, Any, List
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


# Base schema
class LearningGoalBase(BaseModel):
    goal_type: str = Field(..., description="Type of goal: vocabulary_count, quiz_score, exam_preparation, etc.")
    goal_title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: Optional[str] = Field(None, description="Detailed description")
    target_metrics: Dict[str, Any] = Field(..., description="Target metrics as JSON")
    start_date: date = Field(..., description="Goal start date")
    target_date: date = Field(..., description="Goal target completion date")
    priority: str = Field(default="medium", description="Priority: low, medium, high, urgent")
    
    @field_validator('goal_type')
    @classmethod
    def validate_goal_type(cls, v):
        allowed = ['vocabulary_count', 'quiz_score', 'exam_preparation', 'time_based', 'fluency', 'topic_mastery']
        if v not in allowed:
            raise ValueError(f"goal_type must be one of {allowed}")
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        allowed = ['low', 'medium', 'high', 'urgent']
        if v not in allowed:
            raise ValueError(f"priority must be one of {allowed}")
        return v
    
    @field_validator('target_date')
    @classmethod
    def validate_dates(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("target_date must be after start_date")
        return v


# Create schema (what user sends)
class LearningGoalCreate(LearningGoalBase):
    """Schema for creating a new learning goal"""
    pass


# Update schema (partial updates)
class LearningGoalUpdate(BaseModel):
    """Schema for updating a learning goal"""
    goal_type: Optional[str] = None
    goal_title: Optional[str] = None
    description: Optional[str] = None
    target_metrics: Optional[Dict[str, Any]] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed = ['draft', 'active', 'paused', 'completed', 'abandoned']
            if v not in allowed:
                raise ValueError(f"status must be one of {allowed}")
        return v


# Response schema (what API returns)
class LearningGoalResponse(LearningGoalBase):
    """Schema for learning goal API response"""
    id: int
    user_id: int
    current_progress: Optional[Dict[str, Any]] = None
    actual_completion_date: Optional[date] = None
    status: str
    is_on_track: bool
    days_behind: int
    estimated_completion_date: Optional[date] = None
    completion_percentage: int
    milestones: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# List response
class LearningGoalList(BaseModel):
    """Schema for list of learning goals"""
    goals: List[LearningGoalResponse]
    total: int
    active_count: int
    completed_count: int

