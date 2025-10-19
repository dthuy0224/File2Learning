from typing import List
from datetime import datetime

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.flashcard import Flashcard
from app.schemas.flashcard import FlashcardCreate, FlashcardUpdate


class CRUDFlashcard(CRUDBase[Flashcard, FlashcardCreate, FlashcardUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Flashcard]:
        return (
            db.query(self.model)
            .filter(Flashcard.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_due_for_review(
        self, db: Session, *, user_id: int, limit: int = 50
    ) -> List[Flashcard]:
        """Get flashcards that are due for review"""
        now = datetime.utcnow()
        return (
            db.query(self.model)
            .filter(
                Flashcard.owner_id == user_id,
                Flashcard.next_review_date <= now
            )
            .limit(limit)
            .all()
        )

    def get_by_document(
        self, db: Session, *, document_id: int, skip: int = 0, limit: int = 100
    ) -> List[Flashcard]:
        return (
            db.query(self.model)
            .filter(Flashcard.document_id == document_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_owner(
        self, db: Session, *, obj_in: FlashcardCreate, owner_id: int
    ) -> Flashcard:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, owner_id=owner_id, next_review_date=datetime.utcnow())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
flashcard = CRUDFlashcard(Flashcard)
