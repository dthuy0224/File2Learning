from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.study_schedule import DailyStudyPlan
from app.schemas.daily_plan import DailyStudyPlanCreate, DailyStudyPlanUpdate
from app.crud.crud_recommendation import crud_recommendation


def get_plan(db: Session, plan_id: int, user_id: int) -> Optional[DailyStudyPlan]:
    """Get a single daily plan by ID"""
    return db.query(DailyStudyPlan).filter(
        and_(DailyStudyPlan.id == plan_id, DailyStudyPlan.user_id == user_id)
    ).first()


def get_plan_by_date(db: Session, user_id: int, plan_date: date) -> Optional[DailyStudyPlan]:
    """Get daily plan for a specific date"""
    return db.query(DailyStudyPlan).filter(
        and_(
            DailyStudyPlan.user_id == user_id,
            DailyStudyPlan.plan_date == plan_date
        )
    ).first()


def get_today_plan(db: Session, user_id: int) -> Optional[DailyStudyPlan]:
    """Get today's plan"""
    return get_plan_by_date(db, user_id, date.today())


def get_plans(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[DailyStudyPlan]:
    """Get daily plans with optional filters"""
    query = db.query(DailyStudyPlan).filter(DailyStudyPlan.user_id == user_id)
    
    if start_date:
        query = query.filter(DailyStudyPlan.plan_date >= start_date)
    if end_date:
        query = query.filter(DailyStudyPlan.plan_date <= end_date)
    if status:
        query = query.filter(DailyStudyPlan.status == status)
    
    return query.order_by(DailyStudyPlan.plan_date.desc()).offset(skip).limit(limit).all()


def create_plan(db: Session, plan: DailyStudyPlanCreate, user_id: int) -> DailyStudyPlan:
    """Create a new daily study plan"""
    # Convert RecommendedTask objects to dicts
    tasks_dict = [task.model_dump() for task in plan.recommended_tasks]
    
    db_plan = DailyStudyPlan(
        user_id=user_id,
        schedule_id=plan.schedule_id,
        plan_date=plan.plan_date,
        plan_summary=plan.plan_summary,
        recommended_tasks=tasks_dict,
        total_estimated_minutes=plan.total_estimated_minutes,
        total_tasks_count=len(plan.recommended_tasks),
        priority_level=plan.priority_level,
        difficulty_level=plan.difficulty_level,
        source_recommendation_ids=plan.source_recommendation_ids,  # NEW!
        status='pending',
        is_completed=False,
        completion_percentage=0.0,
        completed_tasks_count=0,
        actual_minutes_spent=0
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    # Mark recommendations as included in plan (NEW!)
    if plan.source_recommendation_ids:
        for rec_id in plan.source_recommendation_ids:
            crud_recommendation.mark_included_in_plan(
                db,
                recommendation_id=rec_id,
                plan_id=db_plan.id,
                plan_date=plan.plan_date.isoformat()
            )
    
    return db_plan


def update_plan(
    db: Session,
    plan_id: int,
    user_id: int,
    plan_update: DailyStudyPlanUpdate
) -> Optional[DailyStudyPlan]:
    """Update a daily plan"""
    db_plan = get_plan(db, plan_id, user_id)
    if not db_plan:
        return None
    
    update_data = plan_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_plan, field, value)
    
    # Calculate completion percentage
    if db_plan.total_tasks_count > 0:
        db_plan.completion_percentage = (db_plan.completed_tasks_count / db_plan.total_tasks_count) * 100
    
    # Auto-update status based on completion
    if db_plan.completion_percentage >= 100:
        db_plan.status = 'completed'
        db_plan.is_completed = True
        if not db_plan.completed_at:
            db_plan.completed_at = datetime.utcnow()
    elif db_plan.completion_percentage > 0:
        db_plan.status = 'in_progress'
    
    db_plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_plan)
    return db_plan


def start_plan(db: Session, plan_id: int, user_id: int) -> Optional[DailyStudyPlan]:
    """Mark plan as started"""
    db_plan = get_plan(db, plan_id, user_id)
    if not db_plan:
        return None
    
    if db_plan.status == 'pending':
        db_plan.status = 'in_progress'
        db_plan.started_at = datetime.utcnow()
        db_plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_plan)
    
    return db_plan


def complete_plan(
    db: Session,
    plan_id: int,
    user_id: int,
    actual_minutes_spent: int,
    completed_tasks_count: int,
    actual_performance: Optional[dict] = None,
    effectiveness_rating: Optional[int] = None,
    user_notes: Optional[str] = None
) -> Optional[DailyStudyPlan]:
    from app.models.study_session import StudySession, LearningAnalytics
    from app.crud import crud_learning_goal
    
    db_plan = get_plan(db, plan_id, user_id)
    if not db_plan:
        return None
    
    db_plan.status = 'completed'
    db_plan.is_completed = True
    db_plan.actual_minutes_spent = actual_minutes_spent
    db_plan.completed_tasks_count = completed_tasks_count
    db_plan.actual_performance = actual_performance or {}
    db_plan.effectiveness_rating = effectiveness_rating
    db_plan.user_notes = user_notes
    db_plan.completed_at = datetime.utcnow()
    
    # Calculate completion percentage
    if db_plan.total_tasks_count > 0:
        db_plan.completion_percentage = (completed_tasks_count / db_plan.total_tasks_count) * 100
    
    db_plan.updated_at = datetime.utcnow()
    
    # ✅ Integration 1: Create StudySession for analytics
    if db_plan.started_at:
        session = StudySession(
            user_id=user_id,
            daily_plan_id=plan_id,
            session_type='mixed',  # Daily plan contains multiple activities
            duration_seconds=actual_minutes_spent * 60,
            started_at=db_plan.started_at,
            ended_at=datetime.utcnow(),
            performance_data=actual_performance or {},
            is_planned=True
        )
        db.add(session)
    
    # ✅ Integration 2: Update LearningAnalytics
    today = db_plan.plan_date
    analytics = db.query(LearningAnalytics).filter(
        and_(
            LearningAnalytics.user_id == user_id,
            LearningAnalytics.analytics_date == today
        )
    ).first()
    
    if not analytics:
        analytics = LearningAnalytics(
            user_id=user_id,
            analytics_date=today,
            total_study_minutes=0,
            sessions_count=0
        )
        db.add(analytics)
    
    analytics.total_study_minutes += actual_minutes_spent
    analytics.sessions_count += 1
    analytics.is_active_day = True
    
    # Extract performance metrics from actual_performance
    if actual_performance:
        if 'flashcards' in actual_performance:
            fc_data = actual_performance['flashcards']
            analytics.flashcards_reviewed += fc_data.get('reviewed', 0)
            analytics.flashcards_correct += fc_data.get('correct', 0)
        
        if 'quizzes' in actual_performance:
            quiz_data = actual_performance['quizzes']
            analytics.quizzes_taken += quiz_data.get('completed', 0)
            if 'score' in quiz_data:
                # Update average score
                if analytics.quizzes_taken > 0:
                    current_avg = float(analytics.quiz_avg_score or 0)
                    new_score = quiz_data['score']
                    analytics.quiz_avg_score = (current_avg * (analytics.quizzes_taken - 1) + new_score) / analytics.quizzes_taken
    
    # ✅ Integration 3: Update Learning Goal Progress
    # Get active goals and update their progress based on completed tasks
    from app.models.learning_goal import LearningGoal
    active_goals = db.query(LearningGoal).filter(
        and_(
            LearningGoal.user_id == user_id,
            LearningGoal.status == 'active'
        )
    ).all()
    
    for goal in active_goals:
        # Increment progress by completed tasks count
        if goal.current_progress is None:
            goal.current_progress = 0
        goal.current_progress += completed_tasks_count
        
        # Update goal status if target reached
        if goal.target_metrics and 'tasks_completed' in goal.target_metrics:
            target = goal.target_metrics['tasks_completed']
            if goal.current_progress >= target:
                goal.status = 'completed'
                goal.current_progress = target
    
    db.commit()
    db.refresh(db_plan)
    return db_plan


def skip_plan(
    db: Session,
    plan_id: int,
    user_id: int,
    skip_reason: Optional[str] = None
) -> Optional[DailyStudyPlan]:
    """Mark plan as skipped"""
    db_plan = get_plan(db, plan_id, user_id)
    if not db_plan:
        return None
    
    db_plan.status = 'skipped'
    db_plan.skip_reason = skip_reason
    db_plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_plan)
    return db_plan


def delete_plan(db: Session, plan_id: int, user_id: int) -> bool:
    """Delete a daily plan"""
    db_plan = get_plan(db, plan_id, user_id)
    if not db_plan:
        return False
    
    db.delete(db_plan)
    db.commit()
    return True


def get_completion_rate(db: Session, user_id: int, days: int = 7) -> float:
    """Get plan completion rate for last N days"""
    from datetime import timedelta
    
    start_date = date.today() - timedelta(days=days)
    plans = get_plans(db, user_id, start_date=start_date)
    
    if not plans:
        return 0.0
    
    completed = len([p for p in plans if p.status == 'completed'])
    return (completed / len(plans)) * 100


def get_adherence_stats(db: Session, user_id: int, days: int = 30) -> dict:
    """Get adherence statistics"""
    from datetime import timedelta
    
    start_date = date.today() - timedelta(days=days)
    plans = get_plans(db, user_id, start_date=start_date)
    
    total = len(plans)
    if total == 0:
        return {
            "total_plans": 0,
            "completed": 0,
            "skipped": 0,
            "pending": 0,
            "completion_rate": 0.0,
            "avg_completion_percentage": 0.0,
            "total_study_minutes": 0,
            "avg_daily_minutes": 0.0
        }
    
    completed = [p for p in plans if p.status == 'completed']
    skipped = [p for p in plans if p.status == 'skipped']
    pending = [p for p in plans if p.status in ['pending', 'in_progress']]
    
    total_minutes = sum(p.actual_minutes_spent for p in plans)
    avg_completion = sum(float(p.completion_percentage) for p in plans) / total
    
    return {
        "total_plans": total,
        "completed": len(completed),
        "skipped": len(skipped),
        "pending": len(pending),
        "completion_rate": (len(completed) / total) * 100,
        "avg_completion_percentage": avg_completion,
        "total_study_minutes": total_minutes,
        "avg_daily_minutes": total_minutes / max(days, 1)
    }

