import logging
from typing import Optional, Dict

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

        # 1. Refresh personalized recommendations
        new_recs = generate_recommendations_for_user(db, user_id, max_recommendations=10)
        logger.info("Generated %s new recommendations for user %s", new_recs, user_id)

        # 2. Adjust active schedule to reflect the latest performance
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

