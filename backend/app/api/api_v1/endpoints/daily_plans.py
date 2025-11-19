from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.models.user import User
from app.crud import crud_daily_plan, crud_learning_goal
from app.schemas import daily_plan as schemas
from app.services.plan_generator import generate_daily_plan
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _calculate_user_streak(db: Session, user_id: int, max_days: int = 30) -> int:
    """Count consecutive days (up to max_days) where the user has an active/complete plan."""
    streak = 0
    for offset in range(max_days):
        check_date = date.today() - timedelta(days=offset)
        plan = crud_daily_plan.get_plan_by_date(db, user_id, check_date)
        if plan and plan.status in ('completed', 'in_progress'):
            streak += 1
        else:
            break
    return streak


def _calculate_weekly_minutes(db: Session, user_id: int) -> int:
    """Sum actual study minutes for the current calendar week."""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    plans = crud_daily_plan.get_plans(
        db,
        user_id,
        start_date=start_of_week,
        end_date=today
    )
    return sum((plan.actual_minutes_spent or 0) for plan in plans)


def _get_goals_progress(db: Session, user_id: int, limit: int = 3) -> List[Dict[str, Any]]:
    """Return a lightweight summary of active learning goals."""
    goals = crud_learning_goal.get_active_goals(db, user_id)[:limit]
    progress = []
    for goal in goals:
        progress.append({
            "goal_id": goal.id,
            "title": goal.goal_title,
            "completion_percentage": int(goal.completion_percentage or 0),
            "is_on_track": bool(goal.is_on_track),
            "days_behind": goal.days_behind or 0,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "priority": goal.priority,
        })
    return progress


def _build_today_plan_response(
    db: Session,
    user_id: int,
    *,
    plan,
    has_plan: bool,
    is_new: bool,
    message: str,
) -> schemas.TodayPlanResponse:
    """Attach contextual fields (streak, weekly minutes, goals) to the today-plan response."""
    return schemas.TodayPlanResponse(
        plan=plan,
        has_plan=has_plan,
        is_new=is_new,
        message=message,
        user_streak=_calculate_user_streak(db, user_id),
        total_study_time_this_week=_calculate_weekly_minutes(db, user_id),
        goals_progress=_get_goals_progress(db, user_id)
    )


@router.get("/today", response_model=schemas.TodayPlanResponse)
def get_today_plan(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    force_regenerate: bool = False,
):
    today = date.today()
    
    # If force_regenerate, delete existing plan first
    if force_regenerate:
        existing_plan = crud_daily_plan.get_today_plan(db, user_id=current_user.id)
        if existing_plan:
            crud_daily_plan.delete_plan(db, plan_id=existing_plan.id, user_id=current_user.id)
            logger.info(f"Deleted existing plan for user {current_user.id} to regenerate")
    
    # Check if plan already exists
    existing_plan = crud_daily_plan.get_today_plan(db, user_id=current_user.id)
    
    if existing_plan:
        logger.info(f"Returning existing plan for user {current_user.id}")
        return _build_today_plan_response(
            db,
            current_user.id,
            plan=existing_plan,
            has_plan=True,
            is_new=False,
            message="Here's your plan for today! 📚"
        )
    
    # Generate new plan
    logger.info(f"Generating new plan for user {current_user.id}")
    try:
        plan_data = generate_daily_plan(db, user_id=current_user.id, plan_date=today)
        new_plan = crud_daily_plan.create_plan(db, plan=plan_data, user_id=current_user.id)
        
        return _build_today_plan_response(
            db,
            current_user.id,
            plan=new_plan,
            has_plan=True,
            is_new=True,
            message="Fresh plan generated just for you! Let's do this! 🚀"
        )
    except Exception as e:
        logger.error(f"Error generating plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}"
        )


@router.post("/today/regenerate", response_model=schemas.TodayPlanResponse)
def regenerate_today_plan(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Force regenerate today's plan (useful after accepting recommendations)
    """
    today = date.today()
    
    # Delete existing plan if exists
    existing_plan = crud_daily_plan.get_today_plan(db, user_id=current_user.id)
    if existing_plan:
        crud_daily_plan.delete_plan(db, plan_id=existing_plan.id, user_id=current_user.id)
        logger.info(f"Deleted existing plan for user {current_user.id} to regenerate")
    
    # Generate new plan
    logger.info(f"Regenerating plan for user {current_user.id}")
    try:
        plan_data = generate_daily_plan(db, user_id=current_user.id, plan_date=today)
        new_plan = crud_daily_plan.create_plan(db, plan=plan_data, user_id=current_user.id)
        
        return _build_today_plan_response(
            db,
            current_user.id,
            plan=new_plan,
            has_plan=True,
            is_new=True,
            message="Plan regenerated with your accepted recommendations! 🎯"
        )
    except Exception as e:
        logger.error(f"Error regenerating plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate plan: {str(e)}"
        )


@router.get("/{plan_date}", response_model=schemas.DailyStudyPlanResponse)
def get_plan_by_date(
    plan_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get plan for a specific date
    """
    plan = crud_daily_plan.get_plan_by_date(db, user_id=current_user.id, plan_date=plan_date)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No plan found for {plan_date}"
        )
    return plan


@router.get("/", response_model=List[schemas.DailyStudyPlanResponse])
def read_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
):
    """
    Get daily plans with optional filters
    """
    plans = crud_daily_plan.get_plans(
        db, 
        user_id=current_user.id, 
        start_date=start_date,
        end_date=end_date,
        status=status,
        skip=skip, 
        limit=limit
    )
    return plans


@router.post("/{plan_id}/start", response_model=schemas.DailyStudyPlanResponse)
def start_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Mark plan as started
    """
    plan = crud_daily_plan.start_plan(db, plan_id=plan_id, user_id=current_user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.post("/{plan_id}/complete", response_model=schemas.DailyStudyPlanResponse)
def complete_plan(
    plan_id: int,
    completion_data: schemas.DailyStudyPlanComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Mark plan as completed with performance data
    """
    plan = crud_daily_plan.complete_plan(
        db,
        plan_id=plan_id,
        user_id=current_user.id,
        actual_minutes_spent=completion_data.actual_minutes_spent,
        completed_tasks_count=completion_data.completed_tasks_count,
        actual_performance=completion_data.actual_performance,
        effectiveness_rating=completion_data.effectiveness_rating,
        user_notes=completion_data.user_notes
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.post("/{plan_id}/skip", response_model=schemas.DailyStudyPlanResponse)
def skip_plan(
    plan_id: int,
    skip_reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Mark plan as skipped
    """
    plan = crud_daily_plan.skip_plan(
        db, plan_id=plan_id, user_id=current_user.id, skip_reason=skip_reason
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.put("/{plan_id}", response_model=schemas.DailyStudyPlanResponse)
def update_plan(
    plan_id: int,
    plan_update: schemas.DailyStudyPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update plan progress
    """
    plan = crud_daily_plan.update_plan(
        db, plan_id=plan_id, user_id=current_user.id, plan_update=plan_update
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.get("/stats/completion-rate")
def get_completion_rate(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get plan completion rate for last N days
    """
    rate = crud_daily_plan.get_completion_rate(db, user_id=current_user.id, days=days)
    return {"completion_rate": rate, "days": days}


@router.get("/stats/adherence")
def get_adherence_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get adherence statistics
    """
    stats = crud_daily_plan.get_adherence_stats(db, user_id=current_user.id, days=days)
    return stats

