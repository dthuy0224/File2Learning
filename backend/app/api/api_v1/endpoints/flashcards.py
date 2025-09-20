from typing import Any, List

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
    
    # TODO: Implement SRS algorithm (SM-2 or similar)
    # This will update ease_factor, interval, repetitions, next_review_date
    # based on the quality score (0-5)
    
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
    flashcard_obj = flashcard.get(db=db, id=flashcard_id)
    if not flashcard_obj:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if flashcard_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    flashcard.remove(db=db, id=flashcard_id)
    return {"message": "Flashcard deleted successfully"}
