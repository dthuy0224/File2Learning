from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from app.api.api_v1.endpoints import (
    auth, users, documents, flashcards, quizzes, ai, flashcard_sets, analytics,
    learning_goals, daily_plans, recommendations
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(flashcard_sets.router, prefix="/flashcard-sets", tags=["flashcard-sets"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])

# Adaptive Learning Endpoints
api_router.include_router(learning_goals.router, prefix="/goals", tags=["learning-goals"])
api_router.include_router(daily_plans.router, prefix="/plans", tags=["daily-plans"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
