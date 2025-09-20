# Import all CRUD operations
from app.crud.crud_user import user
from app.crud.crud_document import document
from app.crud.crud_flashcard import flashcard
from app.crud.crud_quiz import quiz

__all__ = ["user", "document", "flashcard", "quiz"]
