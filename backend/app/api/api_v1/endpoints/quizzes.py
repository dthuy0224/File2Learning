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
    
    # TODO: Create QuizAttempt record
    # This is a placeholder implementation
    return {"message": "Quiz attempt started", "quiz_id": quiz_id}


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
    
    # TODO: Grade the quiz and save attempt
    # Calculate score, save answers, mark as completed
    # This is a placeholder implementation
    return {"message": "Quiz submitted successfully", "quiz_id": quiz_id}


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
