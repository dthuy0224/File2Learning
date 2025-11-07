from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import defaultdict

from app.core.database import get_db
from app.core import deps
from app.models.user import User as UserModel
from app.models.flashcard import Flashcard
from app.models.quiz import QuizAttempt, Quiz
from app.models.document import Document
from app.schemas.user import LearningAnalytics, ProgressOverTime, RetentionDataItem, QuizByTopic

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
        words_learned / total_reviews if total_reviews > 0 else 0.0
    )
    learning_progress = len([fc for fc in flashcards if fc.times_reviewed > 0]) / len(flashcards) if flashcards else 0.0

    # Active days
    review_dates = {fc.updated_at.date() for fc in flashcards if fc.updated_at}
    active_days = len(review_dates)

    # ===== Quiz stats =====
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.is_completed == True
    ).all()
    average_quiz_score = (
        sum(attempt.percentage for attempt in attempts) / len(attempts) / 100.0
        if attempts else 0.0
    )

    # ===== 📈 Progress Over Time (Last 6 months) =====
    progress_over_time = []
    now = datetime.now()
    
    for i in range(5, -1, -1):
        # Calculate month
        target_date = now - timedelta(days=30 * i)
        month_name = target_date.strftime("%b")
        
        # Count activities in this month
        month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = now
        else:
            next_month = target_date + timedelta(days=32)
            month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Count flashcard reviews in this month
        flashcard_count = db.query(func.count(Flashcard.id)).filter(
            Flashcard.owner_id == user_id,
            Flashcard.updated_at >= month_start,
            Flashcard.updated_at < month_end,
            Flashcard.times_reviewed > 0
        ).scalar() or 0
        
        # Count quiz attempts in this month
        quiz_count = db.query(func.count(QuizAttempt.id)).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.completed_at >= month_start,
            QuizAttempt.completed_at < month_end,
            QuizAttempt.is_completed == True
        ).scalar() or 0
        
        total_progress = flashcard_count + quiz_count
        progress_over_time.append(ProgressOverTime(month=month_name, progress=total_progress))

    # ===== 🎯 Retention Data =====
    # Flashcards mastered vs needs review
    mastered_count = len([
        fc for fc in flashcards 
        if fc.ease_factor >= 2.0 and fc.repetitions >= 2
    ])
    needs_review_count = len(flashcards) - mastered_count
    
    retention_data = [
        RetentionDataItem(name="Mastered", value=mastered_count),
        RetentionDataItem(name="Needs Review", value=needs_review_count)
    ]

    # ===== 🧠 Quiz Performance by Topic =====
    quiz_by_topic = []
    
    # Group quiz attempts by document
    quiz_topic_scores: Dict[str, list] = defaultdict(list)
    
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        if quiz and quiz.document_id:
            document = db.query(Document).filter(Document.id == quiz.document_id).first()
            if document:
                topic_name = document.title or document.original_filename
                quiz_topic_scores[topic_name].append(attempt.percentage / 100.0)
    
    # Calculate average score per topic
    for topic, scores in quiz_topic_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0.0
        quiz_by_topic.append(QuizByTopic(topic=topic, score=avg_score))
    
    # If no quiz data, add a placeholder
    if not quiz_by_topic:
        quiz_by_topic.append(QuizByTopic(topic="No quizzes yet", score=0.0))

    return LearningAnalytics(
        words_learned=words_learned,
        retention_rate=retention_rate,
        avg_quiz_score=average_quiz_score,
        progress=learning_progress,
        active_days=active_days,
        progress_over_time=progress_over_time,
        retention_data=retention_data,
        quiz_by_topic=quiz_by_topic
    )
