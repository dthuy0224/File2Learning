# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt

# Adaptive Learning Models
from app.models.learning_profile import LearningProfile
from app.models.learning_goal import LearningGoal
from app.models.study_schedule import StudySchedule, DailyStudyPlan
from app.models.study_session import StudySession, LearningAnalytics

__all__ = [
    # Core Models
    "User", 
    "Document", 
    "Flashcard", 
    "Quiz", 
    "QuizQuestion", 
    "QuizAttempt",
    # Adaptive Learning Models
    "LearningProfile",
    "LearningGoal",
    "StudySchedule",
    "DailyStudyPlan",
    "StudySession",
    "LearningAnalytics",
]
