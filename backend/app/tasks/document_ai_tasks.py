import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.crud import document as document_crud, quiz as quiz_crud
from app.schemas.document import DocumentUpdate
from app.schemas.quiz import QuizCreate, QuizQuestionCreate
from app.services.multi_ai_service import multi_ai_service

logger = logging.getLogger(__name__)


def _update_document_status(
    *,
    document_id: int,
    status_field: str,
    status_value: str,
    error_field: Optional[str] = None,
    error_value: Optional[str] = None,
    timestamp_field: Optional[str] = None,
) -> None:
    db = SessionLocal()
    try:
        doc = document_crud.get(db=db, id=document_id)
        if not doc:
            return

        update_payload = {
            status_field: status_value,
        }
        if error_field:
            update_payload[error_field] = error_value
        if timestamp_field:
            update_payload[timestamp_field] = datetime.utcnow()

        document_crud.update(db=db, db_obj=doc, obj_in=DocumentUpdate(**update_payload))
        db.commit()
    except Exception:  # pragma: no cover - logging only
        logger.exception("Failed to update document %s status field %s", document_id, status_field)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2, name="documents.generate_summary")
def generate_document_summary_task(self, document_id: int, max_length: int = 300) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        doc = document_crud.get(db=db, id=document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        if not doc.content:
            raise ValueError("Document has no content")

        _update_document_status(
            document_id=document_id,
            status_field="summary_status",
            status_value="processing",
            error_field="summary_error",
            error_value=None,
        )

        result = asyncio.run(
            multi_ai_service.generate_summary(
                text_content=doc.content,
                max_length=max_length,
            )
        )

        if not result.get("success"):
            raise RuntimeError(result.get("error", "Unknown summary generation error"))

        update = DocumentUpdate(
            summary=result["summary"],
            summary_status="completed",
            summary_error=None,
            summary_generated_at=datetime.utcnow(),
        )
        document_crud.update(db=db, db_obj=doc, obj_in=update)
        db.commit()

        return {
            "status": "completed",
            "ai_provider": result.get("ai_provider"),
            "ai_model": result.get("ai_model"),
        }

    except Exception as exc:
        db.rollback()
        _update_document_status(
            document_id=document_id,
            status_field="summary_status",
            status_value="failed",
            error_field="summary_error",
            error_value=str(exc),
        )
        if self.request.retries < self.max_retries:
            countdown = min(60 * (2 ** self.request.retries), 300)
            raise self.retry(exc=exc, countdown=countdown)
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2, name="documents.generate_vocabulary")
def generate_document_vocabulary_task(self, document_id: int, num_terms: int = 8) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        doc = document_crud.get(db=db, id=document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        if not doc.content:
            raise ValueError("Document has no content")

        _update_document_status(
            document_id=document_id,
            status_field="vocab_status",
            status_value="processing",
            error_field="vocab_error",
            error_value=None,
        )

        result = asyncio.run(
            multi_ai_service.generate_key_vocabulary(
                text_content=doc.content,
                num_terms=num_terms,
            )
        )

        if not result.get("success"):
            raise RuntimeError(result.get("error", "Unknown vocabulary generation error"))

        update = DocumentUpdate(
            key_vocabulary=result["key_vocabulary"],
            vocab_status="completed",
            vocab_error=None,
            vocab_generated_at=datetime.utcnow(),
        )
        document_crud.update(db=db, db_obj=doc, obj_in=update)
        db.commit()

        return {
            "status": "completed",
            "term_count": len(result["key_vocabulary"]),
        }

    except Exception as exc:
        db.rollback()
        _update_document_status(
            document_id=document_id,
            status_field="vocab_status",
            status_value="failed",
            error_field="vocab_error",
            error_value=str(exc),
        )
        if self.request.retries < self.max_retries:
            countdown = min(60 * (2 ** self.request.retries), 300)
            raise self.retry(exc=exc, countdown=countdown)
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2, name="documents.generate_quiz")
def generate_document_quiz_task(
    self,
    document_id: int,
    quiz_type: str = "mixed",
    num_questions: int = 5,
) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        doc = document_crud.get(db=db, id=document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        if not doc.content:
            raise ValueError("Document has no content")

        _update_document_status(
            document_id=document_id,
            status_field="quiz_status",
            status_value="processing",
            error_field="quiz_error",
            error_value=None,
        )

        result = asyncio.run(
            multi_ai_service.generate_quiz(
                text_content=doc.content,
                quiz_type=quiz_type,
                num_questions=num_questions,
            )
        )

        if not result.get("success"):
            raise RuntimeError(result.get("error", "Unknown quiz generation error"))

        quiz_questions = []
        for idx, question in enumerate(result["quiz"], start=1):
            question_text = question.get("question") or question.get("question_text")
            if not question_text:
                continue
            question_options = question.get("options")
            question_type_value = question.get("question_type") or (
                "multiple_choice" if question_options else "fill_blank"
            )
            quiz_questions.append(
                QuizQuestionCreate(
                    question_text=question_text.strip(),
                    question_type=question_type_value,
                    correct_answer=question.get("correct_answer", "").strip(),
                    options=question_options or [],
                    explanation=question.get("explanation") or "",
                    difficulty_level=question.get("difficulty_level", doc.difficulty_level or "medium"),
                    points=question.get("points", 1),
                    order_index=idx,
                )
            )

        if not quiz_questions:
            raise RuntimeError("AI did not return any valid quiz questions")

        quiz_in = QuizCreate(
            title=f"{doc.title or doc.original_filename} - Auto Quiz",
            description=f"AI-generated {quiz_type} quiz based on {doc.title or doc.original_filename}",
            quiz_type=quiz_type,
            difficulty_level=doc.difficulty_level or "medium",
            document_id=doc.id,
            questions=quiz_questions,
        )
        quiz_obj = quiz_crud.create_with_creator(db=db, obj_in=quiz_in, creator_id=doc.owner_id)
        db.commit()

        _update_document_status(
            document_id=document_id,
            status_field="quiz_status",
            status_value="completed",
            error_field="quiz_error",
            error_value=None,
            timestamp_field="quiz_generated_at",
        )

        return {
            "status": "completed",
            "quiz_id": quiz_obj.id,
            "question_count": len(quiz_questions),
        }

    except Exception as exc:
        db.rollback()
        _update_document_status(
            document_id=document_id,
            status_field="quiz_status",
            status_value="failed",
            error_field="quiz_error",
            error_value=str(exc),
        )
        if self.request.retries < self.max_retries:
            countdown = min(60 * (2 ** self.request.retries), 300)
            raise self.retry(exc=exc, countdown=countdown)
        raise
    finally:
        db.close()

