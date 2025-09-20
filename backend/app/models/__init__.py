# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt

__all__ = ["User", "Document", "Flashcard", "Quiz", "QuizQuestion", "QuizAttempt"]
