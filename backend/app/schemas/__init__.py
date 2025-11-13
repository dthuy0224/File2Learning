# Import all schemas here
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.document import Document, DocumentCreate, DocumentUpdate
from app.schemas.flashcard import Flashcard, FlashcardCreate, FlashcardUpdate
from app.schemas.quiz import Quiz, QuizCreate, QuizQuestion, QuizAttempt
from app.schemas.token import Token, TokenPayload
from app.schemas.progress import (
    UserStats, ActivityHeatmapPoint, PerformanceHistoryPoint,
    SkillBreakdownPoint, RecentActivityItem, ProgressResponse
)

# Adaptive Learning Schemas
from app.schemas.learning_goal import (
    LearningGoalCreate, LearningGoalUpdate, LearningGoalResponse, LearningGoalList
)
from app.schemas.daily_plan import (
    RecommendedTask, DailyStudyPlanCreate, DailyStudyPlanUpdate,
    DailyStudyPlanStart, DailyStudyPlanComplete, DailyStudyPlanResponse, TodayPlanResponse
)
from app.schemas.learning_profile import (
    LearningProfileUpdate, LearningProfileResponse, ProfileStatsResponse
)
from app.schemas.recommendation import (
    RecommendationCreate, RecommendationUpdate, RecommendationInteraction,
    RecommendationResponse, RecommendationListResponse, RecommendationStats,
    RecommendationType, RecommendationPriority
)

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Document", "DocumentCreate", "DocumentUpdate",
    "Flashcard", "FlashcardCreate", "FlashcardUpdate",
    "Quiz", "QuizCreate", "QuizQuestion", "QuizAttempt",
    "Token", "TokenPayload",
    "UserStats", "ActivityHeatmapPoint", "PerformanceHistoryPoint",
    "SkillBreakdownPoint", "RecentActivityItem", "ProgressResponse",
    # Adaptive Learning
    "LearningGoalCreate", "LearningGoalUpdate", "LearningGoalResponse", "LearningGoalList",
    "RecommendedTask", "DailyStudyPlanCreate", "DailyStudyPlanUpdate", 
    "DailyStudyPlanStart", "DailyStudyPlanComplete", "DailyStudyPlanResponse", "TodayPlanResponse",
    "LearningProfileUpdate", "LearningProfileResponse", "ProfileStatsResponse",
    "RecommendationCreate", "RecommendationUpdate", "RecommendationInteraction",
    "RecommendationResponse", "RecommendationListResponse", "RecommendationStats",
    "RecommendationType", "RecommendationPriority",
]
