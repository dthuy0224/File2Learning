# Import all schemas here
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.document import Document, DocumentCreate, DocumentUpdate
from app.schemas.flashcard import Flashcard, FlashcardCreate, FlashcardUpdate
from app.schemas.quiz import Quiz, QuizCreate, QuizQuestion, QuizAttempt
from app.schemas.token import Token, TokenPayload

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Document", "DocumentCreate", "DocumentUpdate", 
    "Flashcard", "FlashcardCreate", "FlashcardUpdate",
    "Quiz", "QuizCreate", "QuizQuestion", "QuizAttempt",
    "Token", "TokenPayload"
]
