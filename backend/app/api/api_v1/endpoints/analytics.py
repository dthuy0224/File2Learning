from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core import deps
from app.models.user import User as UserModel
from app.models.flashcard import Flashcard
from app.models.quiz import QuizAttempt
from app.schemas.user import LearningAnalytics

router = APIRouter()


@router.get("/learning-stats", response_model=LearningAnalytics)
def get_learning_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    user_id = current_user.id

    # ===== Flashcard stats =====
    flashcards = db.query(Flashcard).filter(Flashcard.owner_id == user_id).all()
    words_learned = sum(fc.times_correct for fc in flashcards)
    total_reviews = sum(fc.times_reviewed for fc in flashcards)
    retention_rate = (
        words_learned / total_reviews if total_reviews > 0 else 0
    )
    learning_progress = len([fc for fc in flashcards if fc.times_reviewed > 0]) / len(flashcards) if flashcards else 0

    # Active days
    review_dates = {fc.updated_at.date() for fc in flashcards if fc.updated_at}
    active_days = len(review_dates)

    # ===== Quiz stats =====
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.is_completed == True
    ).all()
    average_quiz_score = (
        sum(attempt.percentage for attempt in attempts) / len(attempts)
        if attempts else 0
    )

    return LearningAnalytics(
        words_learned=words_learned,
        retention_rate=retention_rate,
        average_quiz_score=average_quiz_score,
        learning_progress=learning_progress,
        active_days=active_days
    )
