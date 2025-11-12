from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.learning_goal import LearningGoal
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate


def get_goal(db: Session, goal_id: int, user_id: int) -> Optional[LearningGoal]:
    return db.query(LearningGoal).filter(
        and_(LearningGoal.id == goal_id, LearningGoal.user_id == user_id)
    ).first()


def get_goals(
    db: Session, 
    user_id: int, 
    status: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[LearningGoal]:
    query = db.query(LearningGoal).filter(LearningGoal.user_id == user_id)
    
    if status:
        query = query.filter(LearningGoal.status == status)
    
    return query.order_by(LearningGoal.created_at.desc()).offset(skip).limit(limit).all()


def get_active_goals(db: Session, user_id: int) -> List[LearningGoal]:
    return db.query(LearningGoal).filter(
        and_(
            LearningGoal.user_id == user_id,
            LearningGoal.status == 'active'
        )
    ).order_by(LearningGoal.priority.desc(), LearningGoal.target_date.asc()).all()


def create_goal(db: Session, goal: LearningGoalCreate, user_id: int) -> LearningGoal:
    db_goal = LearningGoal(
        user_id=user_id,
        goal_type=goal.goal_type,
        goal_title=goal.goal_title,
        description=goal.description,
        target_metrics=goal.target_metrics,
        start_date=goal.start_date,
        target_date=goal.target_date,
        priority=goal.priority,
        status='active',
        is_on_track=True,
        days_behind=0,
        completion_percentage=0,
        current_progress={}
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def update_goal(
    db: Session, 
    goal_id: int, 
    user_id: int, 
    goal_update: LearningGoalUpdate
) -> Optional[LearningGoal]:
    """Update a learning goal"""
    db_goal = get_goal(db, goal_id, user_id)
    if not db_goal:
        return None
    
    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)
    
    db_goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_goal)
    return db_goal


def update_goal_progress(
    db: Session,
    goal_id: int,
    user_id: int,
    current_progress: dict,
    completion_percentage: int
) -> Optional[LearningGoal]:
    """Update goal progress (called by system)"""
    db_goal = get_goal(db, goal_id, user_id)
    if not db_goal:
        return None
    
    db_goal.current_progress = current_progress
    db_goal.completion_percentage = completion_percentage
    
    # Check if on track
    today = date.today()
    total_days = (db_goal.target_date - db_goal.start_date).days
    days_passed = (today - db_goal.start_date).days
    expected_progress = (days_passed / total_days * 100) if total_days > 0 else 0
    
    db_goal.is_on_track = completion_percentage >= (expected_progress - 10)  # 10% tolerance
    db_goal.days_behind = max(0, int((expected_progress - completion_percentage) / (100 / total_days)))
    
    # Auto-complete if 100%
    if completion_percentage >= 100 and db_goal.status == 'active':
        db_goal.status = 'completed'
        db_goal.completed_at = datetime.utcnow()
        db_goal.actual_completion_date = today
    
    db_goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_goal)
    return db_goal


def delete_goal(db: Session, goal_id: int, user_id: int) -> bool:
    """Delete a learning goal"""
    db_goal = get_goal(db, goal_id, user_id)
    if not db_goal:
        return False
    
    db.delete(db_goal)
    db.commit()
    return True


def get_goals_summary(db: Session, user_id: int) -> dict:
    """Get summary of user's goals"""
    goals = get_goals(db, user_id)
    
    return {
        "total": len(goals),
        "active": len([g for g in goals if g.status == 'active']),
        "completed": len([g for g in goals if g.status == 'completed']),
        "paused": len([g for g in goals if g.status == 'paused']),
        "on_track": len([g for g in goals if g.is_on_track and g.status == 'active']),
        "behind": len([g for g in goals if not g.is_on_track and g.status == 'active']),
    }

