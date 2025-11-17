from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


# Schedule Config Schema
class ScheduleConfig(BaseModel):
    """Schedule configuration structure"""
    daily_minutes: int = Field(..., ge=15, le=300, description="Daily study time in minutes")
    days_per_week: int = Field(..., ge=1, le=7, description="Number of study days per week")
    preferred_times: Optional[List[str]] = Field(None, description="Preferred time slots (e.g., ['18:00-20:00'])")
    activity_distribution: Optional[Dict[str, float]] = Field(
        None, 
        description="Distribution of activities (e.g., {'flashcards': 0.4, 'quizzes': 0.3, 'reading': 0.3})"
    )
    difficulty_curve: Optional[str] = Field(None, description="Difficulty progression: 'gradual', 'steep', 'adaptive'")
    focus_areas: Optional[List[str]] = Field(None, description="Areas to focus on (e.g., ['Grammar', 'Vocabulary'])")
    
    @field_validator('activity_distribution')
    @classmethod
    def validate_distribution(cls, v):
        if v:
            total = sum(v.values())
            if abs(total - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError("activity_distribution values must sum to 1.0")
        return v


# Milestone Schema
class Milestone(BaseModel):
    """Milestone/checkpoint in schedule"""
    week: int = Field(..., ge=1, description="Week number")
    target: str = Field(..., description="Target description (e.g., '50 words')")
    status: str = Field(default="pending", description="Status: 'pending', 'in_progress', 'completed'")
    completed_date: Optional[str] = Field(None, description="Date when milestone was completed")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['pending', 'in_progress', 'completed']
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


# Base Schema
class StudyScheduleBase(BaseModel):
    """Base schema for study schedule"""
    schedule_name: str = Field(..., min_length=1, max_length=200, description="Name of the schedule")
    schedule_type: str = Field(..., description="Type: 'goal_based', 'time_based', 'exam_prep', 'maintenance', 'custom'")
    schedule_config: ScheduleConfig = Field(..., description="Schedule configuration")
    goal_id: Optional[int] = Field(None, description="Linked learning goal ID")
    milestones: Optional[List[Milestone]] = Field(None, description="Milestones/checkpoints")
    adaptation_mode: str = Field(default="moderate", description="Adaptation mode: 'strict', 'moderate', 'flexible', 'highly_adaptive'")
    max_daily_load: int = Field(default=60, ge=15, le=300, description="Maximum daily study time (minutes)")
    min_daily_load: int = Field(default=15, ge=5, le=120, description="Minimum daily study time (minutes)")
    catch_up_strategy: str = Field(default="gradual", description="Catch-up strategy: 'skip', 'gradual', 'intensive'")
    
    @field_validator('schedule_type')
    @classmethod
    def validate_schedule_type(cls, v):
        allowed = ['goal_based', 'time_based', 'exam_prep', 'maintenance', 'custom']
        if v not in allowed:
            raise ValueError(f"schedule_type must be one of {allowed}")
        return v
    
    @field_validator('adaptation_mode')
    @classmethod
    def validate_adaptation_mode(cls, v):
        allowed = ['strict', 'moderate', 'flexible', 'highly_adaptive']
        if v not in allowed:
            raise ValueError(f"adaptation_mode must be one of {allowed}")
        return v
    
    @field_validator('catch_up_strategy')
    @classmethod
    def validate_catch_up_strategy(cls, v):
        allowed = ['skip', 'gradual', 'intensive']
        if v not in allowed:
            raise ValueError(f"catch_up_strategy must be one of {allowed}")
        return v
    
    @field_validator('max_daily_load')
    @classmethod
    def validate_load_range(cls, v, info):
        if 'min_daily_load' in info.data and v < info.data['min_daily_load']:
            raise ValueError("max_daily_load must be >= min_daily_load")
        return v


# Create Schema
class StudyScheduleCreate(StudyScheduleBase):
    """Schema for creating a new study schedule"""
    pass


# Update Schema
class StudyScheduleUpdate(BaseModel):
    """Schema for updating a study schedule"""
    schedule_name: Optional[str] = Field(None, min_length=1, max_length=200)
    schedule_type: Optional[str] = None
    schedule_config: Optional[ScheduleConfig] = None
    goal_id: Optional[int] = None
    milestones: Optional[List[Milestone]] = None
    adaptation_mode: Optional[str] = None
    max_daily_load: Optional[int] = Field(None, ge=15, le=300)
    min_daily_load: Optional[int] = Field(None, ge=5, le=120)
    catch_up_strategy: Optional[str] = None
    is_active: Optional[bool] = None


# Response Schema
class StudyScheduleResponse(StudyScheduleBase):
    """Schema for study schedule API response"""
    id: int
    user_id: int
    is_active: bool
    effectiveness_score: Optional[Decimal] = None
    total_days_scheduled: int
    days_completed: int
    days_missed: int
    days_partially_completed: int
    avg_adherence_rate: Decimal
    last_adjusted_at: Optional[datetime] = None
    adjustment_reason: Optional[str] = None
    adjustment_count: int
    created_at: datetime
    updated_at: datetime
    deactivated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# List Response Schema
class StudyScheduleListResponse(BaseModel):
    """Schema for list of study schedules"""
    schedules: List[StudyScheduleResponse]
    total: int
    active_count: int


# Stats Schema
class StudyScheduleStats(BaseModel):
    """Statistics for study schedule"""
    schedule_id: int
    schedule_name: str
    total_days_scheduled: int
    days_completed: int
    days_missed: int
    days_partially_completed: int
    completion_rate: Decimal  # 0-100%
    avg_adherence_rate: Decimal  # 0-100%
    effectiveness_score: Optional[Decimal] = None
    current_streak: int
    longest_streak: int
    total_study_time: int  # minutes
    avg_daily_time: Decimal  # minutes

