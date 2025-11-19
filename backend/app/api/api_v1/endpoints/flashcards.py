from typing import Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import flashcard
from app.schemas.flashcard import Flashcard, FlashcardCreate, FlashcardUpdate, FlashcardReview
from app.schemas.user import User

router = APIRouter()


@router.get("/", response_model=List[Flashcard])
def read_flashcards(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve flashcards for current user.
    """
    flashcards = flashcard.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return flashcards


@router.get("/due", response_model=List[Flashcard])
def read_due_flashcards(
    db: Session = Depends(get_db),
    limit: int = 50,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get flashcards due for review.
    """
    flashcards = flashcard.get_due_for_review(
        db=db, user_id=current_user.id, limit=limit
    )
    return flashcards


@router.post("/", response_model=Flashcard)
def create_flashcard(
    *,
    db: Session = Depends(get_db),
    flashcard_in: FlashcardCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new flashcard.
    """
    flashcard_obj = flashcard.create_with_owner(
        db=db, obj_in=flashcard_in, owner_id=current_user.id
    )
    return flashcard_obj


@router.get("/{flashcard_id}", response_model=Flashcard)
def read_flashcard(
    *,
    db: Session = Depends(get_db),
    flashcard_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get flashcard by ID.
    """
    flashcard_obj = flashcard.get(db=db, id=flashcard_id)
    if not flashcard_obj:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if flashcard_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return flashcard_obj


@router.put("/{flashcard_id}", response_model=Flashcard)
def update_flashcard(
    *,
    db: Session = Depends(get_db),
    flashcard_id: int,
    flashcard_in: FlashcardUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a flashcard.
    """
    flashcard_obj = flashcard.get(db=db, id=flashcard_id)
    if not flashcard_obj:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if flashcard_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    flashcard_obj = flashcard.update(db=db, db_obj=flashcard_obj, obj_in=flashcard_in)
    return flashcard_obj


@router.post("/{flashcard_id}/review", response_model=Flashcard)
def review_flashcard(
    *,
    db: Session = Depends(get_db),
    flashcard_id: int,
    review: FlashcardReview,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Review a flashcard (update SRS data).
    """
    flashcard_obj = flashcard.get(db=db, id=flashcard_id)
    if not flashcard_obj:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if flashcard_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # --- Start SRS (SM-2) logic ---
    quality = review.quality # User rating quality (0-5)

    if quality >= 3: # If answer is correct (easy, medium, hard)
        if flashcard_obj.repetitions == 0:
            interval = 1
        elif flashcard_obj.repetitions == 1:
            interval = 6
        else:
            interval = round(flashcard_obj.interval * flashcard_obj.ease_factor)

        flashcard_obj.repetitions += 1
        flashcard_obj.ease_factor = flashcard_obj.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    else: # If answer is wrong
        flashcard_obj.repetitions = 0 # Reset repetitions count
        interval = 1 # See you tomorrow

    # Ensure ease_factor is not too low
    if flashcard_obj.ease_factor < 1.3:
        flashcard_obj.ease_factor = 1.3

    # Update next review date
    flashcard_obj.next_review_date = datetime.utcnow() + timedelta(days=interval)
    flashcard_obj.interval = interval
    flashcard_obj.last_review_quality = quality
    flashcard_obj.times_reviewed += 1
    if quality >= 3:
        flashcard_obj.times_correct += 1

    db.commit()
    db.refresh(flashcard_obj)

    # Trigger adaptive learning updates asynchronously (feedback loop)
    try:
        from app.tasks.learning_tasks import process_learning_event_task
        process_learning_event_task.delay(
            user_id=current_user.id,
            event_type="flashcard_reviewed",
            payload={
                "flashcard_id": flashcard_id,
                "quality": quality,
                "is_correct": quality >= 3,
                "repetitions": flashcard_obj.repetitions,
                "ease_factor": flashcard_obj.ease_factor,
            },
        )
    except Exception as background_error:
        import logging
        logging.getLogger(__name__).warning(
            "Failed to enqueue learning event for flashcard %s (user %s): %s",
            flashcard_id,
            current_user.id,
            background_error,
        )

    return flashcard_obj


@router.delete("/{flashcard_id}")
def delete_flashcard(
    *,
    db: Session = Depends(get_db),
    flashcard_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a flashcard.
    """
    flashcard_obj = flashcard.remove(db=db, id=flashcard_id)
    if not flashcard_obj:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if flashcard_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return {"message": "Flashcard deleted successfully"}
