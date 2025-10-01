from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, documents, flashcards, quizzes, ai, flashcard_sets

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(flashcard_sets.router, prefix="/flashcard-sets", tags=["flashcard-sets"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
