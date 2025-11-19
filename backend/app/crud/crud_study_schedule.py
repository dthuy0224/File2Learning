from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from decimal import Decimal

from app.models.study_schedule import StudySchedule
from app.models.daily_plan import DailyStudyPlan
from app.schemas.study_schedule import StudyScheduleCreate, StudyScheduleUpdate


def get_schedule(
    db: Session, schedule_id: int, user_id: int
) -> Optional[StudySchedule]:
    """Get a single study schedule by ID"""
    return (
        db.query(StudySchedule)
        .filter(and_(StudySchedule.id == schedule_id, StudySchedule.user_id == user_id))
        .first()
    )


def get_schedules(
    db: Session,
    user_id: int,
    active_only: bool = False,
    goal_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[StudySchedule]:
    """Get study schedules with optional filters"""
    query = db.query(StudySchedule).filter(StudySchedule.user_id == user_id)

    if active_only:
        query = query.filter(StudySchedule.is_active == True)

    if goal_id:
        query = query.filter(StudySchedule.goal_id == goal_id)

    return (
        query.order_by(StudySchedule.created_at.desc()).offset(skip).limit(limit).all()
    )


def get_active_schedule(db: Session, user_id: int) -> Optional[StudySchedule]:
    """Get the user's active study schedule"""
    return (
        db.query(StudySchedule)
        .filter(and_(StudySchedule.user_id == user_id, StudySchedule.is_active == True))
        .first()
    )


def create_schedule(
    db: Session, schedule: StudyScheduleCreate, user_id: int
) -> StudySchedule:
    """Create a new study schedule"""
    # Convert schedule_config and milestones to dicts
    config_dict = (
        schedule.schedule_config.model_dump()
        if hasattr(schedule.schedule_config, "model_dump")
        else schedule.schedule_config
    )
    milestones_dict = None
    if schedule.milestones:
        milestones_dict = [
            m.model_dump() if hasattr(m, "model_dump") else m
            for m in schedule.milestones
        ]

    db_schedule = StudySchedule(
        user_id=user_id,
        goal_id=schedule.goal_id,
        schedule_name=schedule.schedule_name,
        schedule_type=schedule.schedule_type,
        schedule_config=config_dict,
        milestones=milestones_dict,
        adaptation_mode=schedule.adaptation_mode,
        max_daily_load=schedule.max_daily_load,
        min_daily_load=schedule.min_daily_load,
        catch_up_strategy=schedule.catch_up_strategy,
        is_active=True,
    )

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def update_schedule(
    db: Session, schedule_id: int, user_id: int, schedule_update: StudyScheduleUpdate
) -> Optional[StudySchedule]:
    """Update a study schedule"""
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None

    update_data = schedule_update.model_dump(exclude_unset=True)

    # Handle schedule_config conversion
    if "schedule_config" in update_data and update_data["schedule_config"]:
        if hasattr(update_data["schedule_config"], "model_dump"):
            update_data["schedule_config"] = update_data["schedule_config"].model_dump()

    # Handle milestones conversion
    if "milestones" in update_data and update_data["milestones"]:
        update_data["milestones"] = [
            m.model_dump() if hasattr(m, "model_dump") else m
            for m in update_data["milestones"]
        ]

    for field, value in update_data.items():
        setattr(db_schedule, field, value)

    db_schedule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def deactivate_schedule(
    db: Session, schedule_id: int, user_id: int
) -> Optional[StudySchedule]:
    """Deactivate a study schedule"""
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None

    db_schedule.is_active = False
    db_schedule.deactivated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def activate_schedule(
    db: Session, schedule_id: int, user_id: int
) -> Optional[StudySchedule]:
    """Activate a study schedule (deactivates other active schedules for the user)"""
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None

    # Deactivate all other active schedules for this user
    db.query(StudySchedule).filter(
        and_(
            StudySchedule.user_id == user_id,
            StudySchedule.id != schedule_id,
            StudySchedule.is_active == True,
        )
    ).update({"is_active": False, "deactivated_at": datetime.utcnow()})

    # Activate this schedule
    db_schedule.is_active = True
    db_schedule.deactivated_at = None
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def delete_schedule(db: Session, schedule_id: int, user_id: int) -> bool:
    """Delete a study schedule (cascade deletes daily plans)"""
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return False

    db.delete(db_schedule)
    db.commit()
    return True


def update_schedule_stats(
    db: Session, schedule_id: int, user_id: int
) -> Optional[StudySchedule]:
    """Recalculate and update schedule statistics"""
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None

    # Get all plans for this schedule
    plans = (
        db.query(DailyStudyPlan).filter(DailyStudyPlan.schedule_id == schedule_id).all()
    )

    # Calculate statistics
    total_days = len(plans)
    completed = sum(1 for p in plans if p.is_completed)
    missed = sum(1 for p in plans if p.status == "skipped")
    partially = sum(1 for p in plans if p.status == "partially_completed")

    # Calculate adherence rate
    adherence_rate = Decimal(0.0)
    if total_days > 0:
        adherence_rate = Decimal((completed / total_days) * 100)

    # Update schedule
    db_schedule.total_days_scheduled = total_days
    db_schedule.days_completed = completed
    db_schedule.days_missed = missed
    db_schedule.days_partially_completed = partially
    db_schedule.avg_adherence_rate = adherence_rate

    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_schedule_plans(
    db: Session,
    schedule_id: int,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[DailyStudyPlan]:
    """Get all daily plans for a schedule"""
    # Verify schedule belongs to user
    schedule = get_schedule(db, schedule_id, user_id)
    if not schedule:
        return []

    query = db.query(DailyStudyPlan).filter(DailyStudyPlan.schedule_id == schedule_id)

    if start_date:
        query = query.filter(DailyStudyPlan.plan_date >= start_date)
    if end_date:
        query = query.filter(DailyStudyPlan.plan_date <= end_date)

    return query.order_by(DailyStudyPlan.plan_date).all()


def get_upcoming_plans(
    db: Session, schedule_id: int, user_id: int, days: int = 7
) -> List[DailyStudyPlan]:
    """Get upcoming plans for a schedule"""
    today = date.today()
    end_date = today + timedelta(days=days)
    return get_schedule_plans(
        db, schedule_id, user_id, start_date=today, end_date=end_date
    )
