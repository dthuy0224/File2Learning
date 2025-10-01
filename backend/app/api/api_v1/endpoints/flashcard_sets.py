from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core import deps
from app.models import Document, Flashcard, User
from app.schemas.flashcard_set import FlashcardSet
from app.schemas.flashcard import Flashcard as FlashcardSchema

router = APIRouter()

@router.get("/", response_model=List[FlashcardSet])
def read_flashcard_sets(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve all documents that have flashcards, effectively acting as flashcard sets.
    """
    results = (
        db.query(
            Document.id,
            Document.title,
            Document.original_filename,
            func.count(Flashcard.id).label("card_count"),
            Document.created_at
        )
        .join(Flashcard, Document.id == Flashcard.document_id)
        .filter(Document.owner_id == current_user.id)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return results

@router.get("/{set_id}/cards", response_model=List[FlashcardSchema])
def read_flashcards_in_set(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve all flashcards for a specific set (document).
    """
    # Check if the flashcard set exists and belongs to the user
    document = db.query(Document).filter(Document.id == set_id, Document.owner_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Flashcard set not found")

    return document.flashcards
