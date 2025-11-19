from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

# --- SỬA IMPORT QUAN TRỌNG TẠI ĐÂY ---
from app.models.daily_plan import DailyStudyPlan
from app.models.study_schedule import StudySchedule

# -------------------------------------

from app.schemas.daily_plan import DailyStudyPlanCreate, DailyStudyPlanUpdate


def get_today_plan(db: Session, user_id: int) -> Optional[DailyStudyPlan]:
    """Get today's study plan for a user"""
    today = date.today()
    return (
        db.query(DailyStudyPlan)
        .filter(
            and_(DailyStudyPlan.user_id == user_id, DailyStudyPlan.plan_date == today)
        )
        .first()
    )


def get_plan_by_date(
    db: Session, user_id: int, plan_date: date
) -> Optional[DailyStudyPlan]:
    """Get plan for a specific date"""
    return (
        db.query(DailyStudyPlan)
        .filter(
            and_(
                DailyStudyPlan.user_id == user_id, DailyStudyPlan.plan_date == plan_date
            )
        )
        .first()
    )


def get_plans(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
) -> List[DailyStudyPlan]:
    """Get multiple plans with filtering"""
    query = db.query(DailyStudyPlan).filter(DailyStudyPlan.user_id == user_id)

    if start_date:
        query = query.filter(DailyStudyPlan.plan_date >= start_date)
    if end_date:
        query = query.filter(DailyStudyPlan.plan_date <= end_date)
    if status:
        query = query.filter(DailyStudyPlan.status == status)

    return (
        query.order_by(desc(DailyStudyPlan.plan_date)).offset(skip).limit(limit).all()
    )


def create_plan(
    db: Session, plan: DailyStudyPlanCreate, user_id: int
) -> DailyStudyPlan:
    """Create a new daily plan"""
    # Convert Pydantic models to dict/JSON if necessary
    tasks_data = [
        t.model_dump() if hasattr(t, "model_dump") else t
        for t in plan.recommended_tasks
    ]

    db_plan = DailyStudyPlan(
        user_id=user_id,
        schedule_id=plan.schedule_id,
        plan_date=plan.plan_date,
        plan_summary=plan.plan_summary,
        recommended_tasks=tasks_data,
        total_estimated_minutes=plan.total_estimated_minutes,
        total_tasks_count=len(tasks_data),
        priority_level=plan.priority_level,
        status="pending",
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def start_plan(db: Session, plan_id: int, user_id: int) -> Optional[DailyStudyPlan]:
    """Mark plan as in progress"""
    plan = (
        db.query(DailyStudyPlan)
        .filter(and_(DailyStudyPlan.id == plan_id, DailyStudyPlan.user_id == user_id))
        .first()
    )

    if plan and plan.status == "pending":
        plan.status = "in_progress"
        plan.started_at = func.now()
        db.commit()
        db.refresh(plan)
    return plan


def complete_plan(
    db: Session,
    plan_id: int,
    user_id: int,
    actual_minutes_spent: int,
    completed_tasks_count: int,
    actual_performance: dict,
    effectiveness_rating: Optional[int] = None,
    user_notes: Optional[str] = None,
) -> Optional[DailyStudyPlan]:
    """Mark plan as completed"""
    plan = (
        db.query(DailyStudyPlan)
        .filter(and_(DailyStudyPlan.id == plan_id, DailyStudyPlan.user_id == user_id))
        .first()
    )

    if not plan:
        return None

    plan.status = "completed"
    plan.is_completed = True
    plan.completed_at = func.now()
    plan.actual_minutes_spent = actual_minutes_spent
    plan.completed_tasks_count = completed_tasks_count
    plan.actual_performance = actual_performance

    if effectiveness_rating:
        plan.effectiveness_rating = effectiveness_rating
    if user_notes:
        plan.user_notes = user_notes

    # Calculate completion percentage
    if plan.total_tasks_count > 0:
        plan.completion_percentage = (
            completed_tasks_count / plan.total_tasks_count
        ) * 100
    else:
        plan.completion_percentage = 100

    db.commit()
    db.refresh(plan)
    return plan


def update_plan(
    db: Session, plan_id: int, user_id: int, plan_update: DailyStudyPlanUpdate
) -> Optional[DailyStudyPlan]:
    """Update plan details"""
    plan = (
        db.query(DailyStudyPlan)
        .filter(and_(DailyStudyPlan.id == plan_id, DailyStudyPlan.user_id == user_id))
        .first()
    )

    if not plan:
        return None

    update_data = plan_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)
    return plan


def skip_plan(
    db: Session, plan_id: int, user_id: int, skip_reason: str
) -> Optional[DailyStudyPlan]:
    """Mark plan as skipped"""
    plan = (
        db.query(DailyStudyPlan)
        .filter(and_(DailyStudyPlan.id == plan_id, DailyStudyPlan.user_id == user_id))
        .first()
    )

    if not plan:
        return None

    plan.status = "skipped"
    plan.skip_reason = skip_reason
    db.commit()
    db.refresh(plan)
    return plan


def get_completion_rate(db: Session, user_id: int, days: int = 7) -> float:
    """Calculate completion rate for past N days"""
    # ... implementation details ...
    return 0.0  # Placeholder logic


### Bước cuối cùng: Restart Backend
