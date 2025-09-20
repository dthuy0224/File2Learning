from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.quiz import Quiz, QuizAttempt
from app.schemas.quiz import QuizCreate, QuizUpdate


class CRUDQuiz(CRUDBase[Quiz, QuizCreate, QuizUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Quiz]:
        return (
            db.query(self.model)
            .filter(Quiz.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_document(
        self, db: Session, *, document_id: int, skip: int = 0, limit: int = 100
    ) -> List[Quiz]:
        return (
            db.query(self.model)
            .filter(Quiz.document_id == document_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_creator(
        self, db: Session, *, obj_in: QuizCreate, creator_id: int
    ) -> Quiz:
        obj_in_data = obj_in.dict(exclude={"questions"})
        db_obj = self.model(**obj_in_data, created_by=creator_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Add questions if provided
        if obj_in.questions:
            from app.models.quiz import QuizQuestion
            for question_data in obj_in.questions:
                question = QuizQuestion(
                    **question_data.dict(),
                    quiz_id=db_obj.id
                )
                db.add(question)
            db.commit()
            db.refresh(db_obj)
        
        return db_obj

    def get_user_attempts(
        self, db: Session, *, user_id: int, quiz_id: int
    ) -> List[QuizAttempt]:
        return (
            db.query(QuizAttempt)
            .filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id
            )
            .all()
        )


quiz = CRUDQuiz(Quiz)
