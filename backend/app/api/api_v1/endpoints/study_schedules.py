from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.models.user import User
from app.crud import crud_study_schedule
from app.schemas import study_schedule as schemas
from app.services.schedule_adjuster import adjust_schedule
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=schemas.StudyScheduleResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.StudyScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    schedule: schemas.StudyScheduleCreate,
):
    """
    Create a new study schedule
    """
    # If this is set to active, deactivate other active schedules
    if schedule.adaptation_mode != "strict":  # Only auto-deactivate if not strict mode
        existing_active = crud_study_schedule.get_active_schedule(db, user_id=current_user.id)
        if existing_active:
            logger.info(f"Deactivating existing active schedule {existing_active.id} for user {current_user.id}")
            crud_study_schedule.deactivate_schedule(db, existing_active.id, current_user.id)
    
    new_schedule = crud_study_schedule.create_schedule(
        db, schedule=schedule, user_id=current_user.id
    )
    return new_schedule


@router.get("", response_model=List[schemas.StudyScheduleResponse])
@router.get("/", response_model=List[schemas.StudyScheduleResponse])
def read_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    active_only: bool = Query(False, description="Only return active schedules"),
    goal_id: Optional[int] = Query(None, description="Filter by goal ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all study schedules for the current user
    """
    schedules = crud_study_schedule.get_schedules(
        db,
        user_id=current_user.id,
        active_only=active_only,
        goal_id=goal_id,
        skip=skip,
        limit=limit
    )
    return schedules


@router.get("/active", response_model=Optional[schemas.StudyScheduleResponse])
def get_active_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get the user's active study schedule
    """
    schedule = crud_study_schedule.get_active_schedule(db, user_id=current_user.id)
    if not schedule:
        return None
    return schedule


@router.get("/{schedule_id}", response_model=schemas.StudyScheduleResponse)
def read_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific study schedule by ID
    """
    schedule = crud_study_schedule.get_schedule(db, schedule_id=schedule_id, user_id=current_user.id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@router.put("/{schedule_id}", response_model=schemas.StudyScheduleResponse)
def update_schedule(
    schedule_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    schedule_update: schemas.StudyScheduleUpdate,
):
    """
    Update a study schedule
    """
    schedule = crud_study_schedule.update_schedule(
        db, schedule_id=schedule_id, user_id=current_user.id, schedule_update=schedule_update
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@router.post("/{schedule_id}/activate", response_model=schemas.StudyScheduleResponse)
def activate_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Activate a study schedule (deactivates other active schedules)
    """
    schedule = crud_study_schedule.activate_schedule(
        db, schedule_id=schedule_id, user_id=current_user.id
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@router.post("/{schedule_id}/deactivate", response_model=schemas.StudyScheduleResponse)
def deactivate_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Deactivate a study schedule
    """
    schedule = crud_study_schedule.deactivate_schedule(
        db, schedule_id=schedule_id, user_id=current_user.id
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a study schedule
    """
    success = crud_study_schedule.delete_schedule(
        db, schedule_id=schedule_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )


@router.get("/{schedule_id}/plans")
def get_schedule_plans(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """
    Get all daily plans for a schedule
    """
    from app.schemas.daily_plan import DailyStudyPlanResponse
    from app.crud import crud_daily_plan
    
    # Verify schedule belongs to user
    schedule = crud_study_schedule.get_schedule(db, schedule_id=schedule_id, user_id=current_user.id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    plans = crud_study_schedule.get_schedule_plans(
        db, schedule_id=schedule_id, user_id=current_user.id,
        start_date=start_date, end_date=end_date
    )
    return plans


@router.get("/{schedule_id}/upcoming")
def get_upcoming_plans(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(7, ge=1, le=30, description="Number of days ahead"),
):
    """
    Get upcoming plans for a schedule
    """
    from app.schemas import daily_plan as plan_schemas
    
    # Verify schedule belongs to user
    schedule = crud_study_schedule.get_schedule(db, schedule_id=schedule_id, user_id=current_user.id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    plans = crud_study_schedule.get_upcoming_plans(
        db, schedule_id=schedule_id, user_id=current_user.id, days=days
    )
    return plans


@router.post("/{schedule_id}/update-stats", response_model=schemas.StudyScheduleResponse)
def update_schedule_stats(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Recalculate and update schedule statistics
    """
    schedule = crud_study_schedule.update_schedule_stats(
        db, schedule_id=schedule_id, user_id=current_user.id
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@router.post("/{schedule_id}/adjust", response_model=Dict[str, Any])
def adjust_schedule_endpoint(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Analyze and automatically adjust schedule based on performance
    """
    result = adjust_schedule(db, schedule_id=schedule_id, user_id=current_user.id)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    # Refresh schedule if adjusted
    if result.get("adjusted"):
        schedule = crud_study_schedule.get_schedule(db, schedule_id=schedule_id, user_id=current_user.id)
        result["schedule"] = schemas.StudyScheduleResponse.model_validate(schedule)
    
    return result

