import logging
from typing import Optional, Dict
from datetime import date, datetime

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.recommendation_engine import generate_recommendations_for_user
from app.services.schedule_adjuster import adjust_schedule
from app.crud import crud_study_schedule

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2, name="learning.process_learning_event")
def process_learning_event_task(
    self,
    *,
    user_id: int,
    event_type: str,
    payload: Optional[Dict] = None,
) -> Dict[str, Optional[Dict]]:
    """
    Background job that keeps the adaptive learning loop in sync whenever
    the user completes a learning activity (quiz, flashcards, etc.).
    """
    db = SessionLocal()
    payload = payload or {}

    try:
        logger.info(
            "Processing learning event '%s' for user %s (payload=%s)",
            event_type,
            user_id,
            payload,
        )

        # 1. Update Learning Goals based on event type
        from app.models.learning_goal import LearningGoal
        from app.models.flashcard import Flashcard
        from sqlalchemy import func, and_
        
        active_goals = db.query(LearningGoal).filter(
            and_(
                LearningGoal.user_id == user_id,
                LearningGoal.status == 'active'
            )
        ).all()
        
        for goal in active_goals:
            if goal.goal_type == 'vocabulary_count' and event_type == 'flashcard_reviewed':
                # Update vocabulary count goal when flashcard is reviewed
                if payload and payload.get('is_correct', False):
                    # Count mastered flashcards
                    vocab_count = db.query(func.count(Flashcard.id)).filter(
                        Flashcard.owner_id == user_id,
                        Flashcard.ease_factor >= 2.0,
                        Flashcard.repetitions >= 2
                    ).scalar() or 0
                    
                    target_vocab = goal.target_metrics.get('vocabulary', 0)
                    percentage = int((vocab_count / target_vocab * 100)) if target_vocab > 0 else 0
                    
                    goal.current_progress = {
                        "vocabulary": vocab_count,
                        "percentage": float(percentage),
                        "on_track": percentage >= 0,
                        "days_active": (date.today() - goal.start_date).days
                    }
                    goal.completion_percentage = percentage
                    
                    if vocab_count >= target_vocab:
                        goal.status = 'completed'
                        goal.completed_at = datetime.utcnow()
                        goal.actual_completion_date = date.today()
            
            elif goal.goal_type == 'quiz_score' and event_type == 'quiz_completed':
                # Update quiz score goal when quiz is completed
                if payload:
                    percentage_score = payload.get('percentage', 0)
                    target_score = goal.target_metrics.get('target_score', 100)
                    goal_percentage = int((percentage_score / target_score * 100)) if target_score > 0 else 0
                    
                    goal.current_progress = {
                        "avg_score": float(percentage_score),
                        "target_score": target_score,
                        "percentage": float(goal_percentage),
                        "on_track": percentage_score >= (target_score * 0.8)
                    }
                    goal.completion_percentage = goal_percentage
                    
                    if percentage_score >= target_score:
                        goal.status = 'completed'
                        goal.completed_at = datetime.utcnow()
                        goal.actual_completion_date = date.today()
            
            # Update is_on_track and days_behind
            today = date.today()
            total_days = (goal.target_date - goal.start_date).days
            days_passed = (today - goal.start_date).days
            expected_progress = (days_passed / total_days * 100) if total_days > 0 else 0
            
            goal.is_on_track = goal.completion_percentage >= (expected_progress - 10)
            goal.days_behind = max(0, int((expected_progress - goal.completion_percentage) / (100 / total_days)) if total_days > 0 else 0)
        
        # 2. Refresh personalized recommendations (now with updated goals)
        new_recs = generate_recommendations_for_user(db, user_id, max_recommendations=10)
        logger.info("Generated %s new recommendations for user %s", new_recs, user_id)

        # 3. Adjust active schedule to reflect the latest performance
        schedule = crud_study_schedule.get_active_schedule(db, user_id=user_id)
        adjust_result: Optional[Dict] = None
        if schedule:
            adjust_result = adjust_schedule(db, schedule_id=schedule.id, user_id=user_id)
            logger.info(
                "Schedule %s adjustment result for user %s: %s",
                schedule.id,
                user_id,
                adjust_result,
            )
        else:
            logger.info("No active schedule for user %s. Skipping auto-adjust.", user_id)

        db.commit()
        return {
            "status": "completed",
            "recommendations_generated": new_recs,
            "schedule_adjustment": adjust_result,
        }

    except Exception as exc:  # pragma: no cover - logging path
        logger.exception(
            "Learning event processing failed for user %s (event=%s).",
            user_id,
            event_type,
        )
        db.rollback()

        # Retry with exponential backoff
        retry_count = self.request.retries
        if retry_count < self.max_retries:
            countdown = min(60 * (2 ** retry_count), 300)
            raise self.retry(exc=exc, countdown=countdown)
        raise

    finally:
        db.close()

