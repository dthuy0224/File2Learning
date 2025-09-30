from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date


class UserStats(BaseModel):
    """User statistics and KPIs"""
    study_streak: int
    words_mastered: int
    avg_accuracy: float
    total_study_time: int  # in minutes
    total_quizzes_completed: int
    total_flashcards_reviewed: int
    documents_processed: int


class ActivityHeatmapPoint(BaseModel):
    """Single point in activity heatmap"""
    date: date
    count: int  # number of activities on this day


class PerformanceHistoryPoint(BaseModel):
    """Single point in performance history"""
    date: date
    accuracy: float
    quizzes_completed: int
    avg_score: float


class SkillBreakdownPoint(BaseModel):
    """Skill analysis by difficulty level"""
    level: str  # 'easy', 'medium', 'hard'
    accuracy: float
    quizzes_completed: int
    total_questions: int


class RecentActivityItem(BaseModel):
    """Recent activity item"""
    id: int
    type: str  # 'quiz', 'flashcard', 'document'
    title: str
    score: Optional[str] = None
    time_ago: str
    created_at: datetime


class ProgressResponse(BaseModel):
    """Main progress response containing all data"""
    stats: UserStats
    activity_heatmap: List[ActivityHeatmapPoint]
    performance_history: List[PerformanceHistoryPoint]
    skill_breakdown: List[SkillBreakdownPoint]
    recent_activities: List[RecentActivityItem]
