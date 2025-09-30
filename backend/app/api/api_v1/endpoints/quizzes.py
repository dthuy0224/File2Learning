from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import quiz
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate, QuizAttempt, QuizAttemptCreate, QuizAttemptSubmit
from app.schemas.user import User

router = APIRouter()


@router.get("/", response_model=List[Quiz])
def read_quizzes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve quizzes for current user.
    """
    quizzes = quiz.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return quizzes


@router.post("/", response_model=Quiz)
def create_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_in: QuizCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new quiz.
    """
    quiz_obj = quiz.create_with_creator(
        db=db, obj_in=quiz_in, creator_id=current_user.id
    )
    return quiz_obj


@router.get("/{quiz_id}", response_model=Quiz)
def read_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get quiz by ID.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")
    # Allow access to any user's quiz (public quizzes)
    return quiz_obj


@router.put("/{quiz_id}", response_model=Quiz)
def update_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    quiz_in: QuizUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a quiz.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz_obj.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    quiz_obj = quiz.update(db=db, db_obj=quiz_obj, obj_in=quiz_in)
    return quiz_obj


@router.post("/{quiz_id}/attempt", response_model=QuizAttempt)
def start_quiz_attempt(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Start a new quiz attempt.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Create QuizAttempt record
    from app.models.quiz import QuizAttempt
    from datetime import datetime

    attempt_obj = QuizAttempt(
        quiz_id=quiz_id,
        user_id=current_user.id,
        answers={},  # Empty initially
        score=0,     # Will be calculated later
        max_score=0, # Will be calculated later
        percentage=0, # Will be calculated later
        time_taken=None, # Will be set when completed
        is_completed=False,
        started_at=datetime.utcnow(),
        completed_at=None
    )

    db.add(attempt_obj)
    db.commit()
    db.refresh(attempt_obj)

    return attempt_obj


@router.post("/{quiz_id}/submit", response_model=QuizAttempt)
def submit_quiz_attempt(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    submission: QuizAttemptSubmit,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Submit quiz attempt answers.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Get all questions for this quiz
    from app.models.quiz import QuizQuestion
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()

    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    # Calculate scores
    correct_answers = 0
    total_points = 0
    answers_dict = {}

    for question in questions:
        question_id = question.id
        user_answer = submission.answers.get(question_id, "")
        correct_answer = question.correct_answer

        # Store the user's answer
        answers_dict[question_id] = {
            "question_text": question.question_text,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": user_answer.strip().lower() == correct_answer.strip().lower(),
            "explanation": question.explanation,
            "points": question.points
        }

        # Check if answer is correct (case-insensitive)
        if user_answer.strip().lower() == correct_answer.strip().lower():
            correct_answers += 1

        total_points += question.points

    # Calculate percentage
    percentage = int((correct_answers / len(questions)) * 100) if questions else 0

    # Update the attempt record
    attempt_obj = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.is_completed == False
    ).first()

    if not attempt_obj:
        raise HTTPException(status_code=400, detail="No active quiz attempt found")

    # Update attempt with results
    attempt_obj.answers = answers_dict
    attempt_obj.score = correct_answers * (100 // len(questions)) if questions else 0  # Score out of 100
    attempt_obj.max_score = 100
    attempt_obj.percentage = percentage
    attempt_obj.time_taken = submission.total_time
    attempt_obj.is_completed = True
    attempt_obj.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(attempt_obj)

    return attempt_obj


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttempt])
def read_quiz_attempts(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user's attempts for a specific quiz.
    """
    attempts = quiz.get_user_attempts(
        db=db, user_id=current_user.id, quiz_id=quiz_id
    )
    return attempts


@router.delete("/{quiz_id}")
def delete_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a quiz.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz_obj.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    quiz.remove(db=db, id=quiz_id)
    return {"message": "Quiz deleted successfully"}
