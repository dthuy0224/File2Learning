from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.models.user import User
from app.crud import crud_learning_goal
from app.schemas import learning_goal as schemas

router = APIRouter()


def _create_goal_impl(
    *,
    db: Session,
    goal_in: schemas.LearningGoalCreate,
    current_user: User,
):
    goal = crud_learning_goal.create_goal(db, goal=goal_in, user_id=current_user.id)
    return goal


@router.post("", response_model=schemas.LearningGoalResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.LearningGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    *,
    db: Session = Depends(get_db),
    goal_in: schemas.LearningGoalCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create new learning goal
    """
    return _create_goal_impl(db=db, goal_in=goal_in, current_user=current_user)


def _read_goals_impl(
    db: Session,
    current_user: User,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
):
    """Internal implementation for read_goals"""
    goals = crud_learning_goal.get_goals(
        db, user_id=current_user.id, status=status, skip=skip, limit=limit
    )
    return goals


@router.get("", response_model=List[schemas.LearningGoalResponse])
@router.get("/", response_model=List[schemas.LearningGoalResponse])
def read_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    status: str = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all learning goals for current user
    """
    return _read_goals_impl(db=db, current_user=current_user, status=status, skip=skip, limit=limit)


@router.get("/active", response_model=List[schemas.LearningGoalResponse])
def read_active_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get all active learning goals
    """
    goals = crud_learning_goal.get_active_goals(db, user_id=current_user.id)
    return goals


@router.get("/summary")
def read_goals_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get summary of user's goals
    """
    summary = crud_learning_goal.get_goals_summary(db, user_id=current_user.id)
    return summary


@router.get("/{goal_id}", response_model=schemas.LearningGoalResponse)
def read_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get specific learning goal by ID
    """
    goal = crud_learning_goal.get_goal(db, goal_id=goal_id, user_id=current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning goal not found"
        )
    return goal


@router.put("/{goal_id}", response_model=schemas.LearningGoalResponse)
def update_goal(
    goal_id: int,
    goal_in: schemas.LearningGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update learning goal
    """
    goal = crud_learning_goal.update_goal(
        db, goal_id=goal_id, user_id=current_user.id, goal_update=goal_in
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning goal not found"
        )
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete learning goal
    """
    success = crud_learning_goal.delete_goal(db, goal_id=goal_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning goal not found"
        )
    return None