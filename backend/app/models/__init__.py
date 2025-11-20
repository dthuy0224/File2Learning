# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt
from app.models.notification import Notification

# Adaptive Learning Models
# Dòng này giữ lại import DailyStudyPlan
from app.models.daily_plan import DailyStudyPlan
from app.models.learning_profile import LearningProfile
from app.models.learning_goal import LearningGoal

# Dòng này CHỈ CÒN StudySchedule (đã xóa DailyStudyPlan)
from app.models.study_schedule import StudySchedule

from app.models.study_session import StudySession, LearningAnalytics
from app.models.recommendation import (
    AdaptiveRecommendation,
    RecommendationType,
    RecommendationPriority,
)

__all__ = [
    # Core Models
    "User",
    "Document",
    "Flashcard",
    "Quiz",
    "QuizQuestion",
    "QuizAttempt",
    "Notification",
    # Adaptive Learning Models
    "LearningProfile",
    "LearningGoal",
    "StudySchedule",
    "DailyStudyPlan",  # Giữ lại một lần duy nhất
    "StudySession",
    "LearningAnalytics",
    "AdaptiveRecommendation",
    "RecommendationType",
    "RecommendationPriority",
]
