from typing import Any, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, cast, Date
import shutil
import os
import re

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status,
    Body,
    Query,
)

from app.core.database import get_db
from app.core import deps
from app.core.security import pwd_context
from app.crud import user as crud_user
from app.models.user import User as UserModel
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserOut,
    PasswordChange,
)
from app.schemas.progress import (
    UserStats, ActivityHeatmapPoint, PerformanceHistoryPoint,
    SkillBreakdownPoint, RecentActivityItem, ProgressResponse
)

router = APIRouter()

AVATAR_DIR = "app/static/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)



@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    if crud_user.get_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    if crud_user.get_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud_user.create(db, obj_in=user_in)



@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    data: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_user),
):
    updated_user = crud_user.update(db, db_obj=current_user, obj_in=data)
    return updated_user



@router.get("/me", response_model=UserOut)
def read_user_me(current_user: UserModel = Depends(deps.get_current_user)):
    """Return current user info + whether they need onboarding setup."""
    user_data = UserOut.model_validate(current_user)
    user_data.needs_setup = not (
        current_user.learning_goals
        and len(current_user.learning_goals) > 0
        and current_user.difficulty_preference
        and current_user.daily_study_time
    )
    return user_data



from app.schemas.user import LearningSetup

@router.put("/me/setup-learning", response_model=UserOut)
def setup_learning_preferences(
    *,
    db: Session = Depends(get_db),
    setup: LearningSetup,
    current_user: UserModel = Depends(deps.get_current_user),
):
    current_user.learning_goals = setup.learning_goals
    current_user.difficulty_preference = setup.difficulty_preference
    current_user.daily_study_time = setup.daily_study_time

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user



@router.post("/me/change-password")
def change_password(
    *,
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user),
):
    user = crud_user.change_password(
        db,
        user_id=current_user.id,
        old_password=data.old_password,
        new_password=data.new_password,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid old password")
    return {"message": "Password updated successfully"}



@router.post("/me/upload-avatar")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user),
):
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
    filename = f"user_{current_user.id}_{safe_filename}"
    file_path = os.path.join(AVATAR_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.avatar = filename
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    avatar_url = f"http://localhost:8000/static/avatars/{filename}"
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "avatar_url": avatar_url,
        "learning_goals": current_user.learning_goals,
        "difficulty_preference": current_user.difficulty_preference,
        "daily_study_time": current_user.daily_study_time,
        "created_at": current_user.created_at,
    }



@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    *,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user),
):
    user_obj = crud_user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if user_obj.id != current_user.id and not crud_user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return user_obj


# Progress and Analytics Endpoints

@router.get("/me/stats", response_model=UserStats)
def get_user_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    range_days: int = Query(30, description="Number of days to look back", ge=1, le=365)
) -> Any:
    """
    Get user learning statistics and KPIs
    """
    from app.models import QuizAttempt, Flashcard, Document

    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=range_days)

    # Study streak calculation (consecutive days with activity)
    study_streak = _calculate_study_streak(db, current_user.id, start_date)

    # Words mastered (flashcards with high ease factor and repetitions)
    words_mastered = db.query(func.count(Flashcard.id)).filter(
        Flashcard.owner_id == current_user.id,
        Flashcard.ease_factor >= 2.5,
        Flashcard.repetitions >= 3
    ).scalar()

    # Average accuracy from quiz attempts
    avg_accuracy_result = db.query(func.avg(QuizAttempt.percentage)).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at >= start_date,
        QuizAttempt.is_completed == True
    ).scalar()

    avg_accuracy = float(avg_accuracy_result) if avg_accuracy_result else 0.0

    # Total study time (sum of time_taken from quiz attempts + estimated flashcard time)
    total_quiz_time = db.query(func.sum(QuizAttempt.time_taken)).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at >= start_date,
        QuizAttempt.is_completed == True
    ).scalar() or 0

    # Estimate flashcard review time (30 seconds per review)
    flashcard_reviews = db.query(func.count(Flashcard.id)).filter(
        Flashcard.owner_id == current_user.id,
        Flashcard.updated_at >= start_date
    ).scalar() or 0

    total_study_time = (total_quiz_time + (flashcard_reviews * 30)) // 60  # Convert to minutes

    # Total quizzes completed
    total_quizzes = db.query(func.count(QuizAttempt.id)).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at >= start_date,
        QuizAttempt.is_completed == True
    ).scalar()

    # Total flashcards reviewed
    total_flashcards_reviewed = flashcard_reviews

    # Documents processed
    documents_processed = db.query(func.count(Document.id)).filter(
        Document.owner_id == current_user.id,
        Document.created_at >= start_date
    ).scalar()

    return UserStats(
        study_streak=study_streak,
        words_mastered=words_mastered,
        avg_accuracy=round(avg_accuracy, 1),
        total_study_time=total_study_time,
        total_quizzes_completed=total_quizzes,
        total_flashcards_reviewed=total_flashcards_reviewed,
        documents_processed=documents_processed
    )


@router.get("/me/activity-heatmap", response_model=List[ActivityHeatmapPoint])
def get_activity_heatmap(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    range_days: int = Query(90, description="Number of days to look back", ge=1, le=365)
) -> Any:
    """
    Get activity heatmap data for the specified time range
    """
    from app.models import QuizAttempt, Flashcard, Document

    start_date = datetime.utcnow() - timedelta(days=range_days)

    # Get daily activity counts from different sources
    quiz_activities = db.query(
        cast(QuizAttempt.started_at, Date).label('date'),
        func.count(QuizAttempt.id).label('quiz_count')
    ).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.started_at >= start_date
    ).group_by(cast(QuizAttempt.started_at, Date)).all()

    flashcard_activities = db.query(
        cast(Flashcard.updated_at, Date).label('date'),
        func.count(Flashcard.id).label('flashcard_count')
    ).filter(
        Flashcard.owner_id == current_user.id,
        Flashcard.updated_at >= start_date
    ).group_by(cast(Flashcard.updated_at, Date)).all()

    document_activities = db.query(
        cast(Document.created_at, Date).label('date'),
        func.count(Document.id).label('document_count')
    ).filter(
        Document.owner_id == current_user.id,
        Document.created_at >= start_date
    ).group_by(cast(Document.created_at, Date)).all()

    # Combine all activities by date
    activity_map = {}

    for activity in quiz_activities + flashcard_activities + document_activities:
        date_str = activity.date.isoformat()
        if date_str not in activity_map:
            activity_map[date_str] = 0
        activity_map[date_str] += activity[1]  # Add the count

    # Convert to response format
    result = []
    for date_str, count in activity_map.items():
        result.append(ActivityHeatmapPoint(
            date=datetime.fromisoformat(date_str).date(),
            count=min(count, 10)  # Cap at 10 for better visualization
        ))

    # Sort by date
    result.sort(key=lambda x: x.date)
    return result


@router.get("/me/performance-history", response_model=List[PerformanceHistoryPoint])
def get_performance_history(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    range_days: int = Query(30, description="Number of days to look back", ge=1, le=365)
) -> Any:
    """
    Get performance history over time
    """
    from app.models import QuizAttempt

    start_date = datetime.utcnow() - timedelta(days=range_days)

    # Get daily performance data
    daily_performance = db.query(
        cast(QuizAttempt.completed_at, Date).label('date'),
        func.count(QuizAttempt.id).label('quizzes_completed'),
        func.avg(QuizAttempt.percentage).label('avg_accuracy'),
        func.avg(QuizAttempt.score).label('avg_score')
    ).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at >= start_date,
        QuizAttempt.is_completed == True
    ).group_by(cast(QuizAttempt.completed_at, Date)).all()

    # Convert to response format
    result = []
    for perf in daily_performance:
        if perf.avg_accuracy is not None:
            result.append(PerformanceHistoryPoint(
                date=perf.date,
                accuracy=round(float(perf.avg_accuracy), 1),
                quizzes_completed=perf.quizzes_completed,
                avg_score=round(float(perf.avg_score), 1)
            ))

    # Sort by date
    result.sort(key=lambda x: x.date)
    return result


@router.get("/me/skill-breakdown", response_model=List[SkillBreakdownPoint])
def get_skill_breakdown(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    range_days: int = Query(30, description="Number of days to look back", ge=1, le=365)
) -> Any:
    """
    Get skill breakdown by difficulty level
    """
    from app.models import QuizAttempt, Quiz

    start_date = datetime.utcnow() - timedelta(days=range_days)

    # Get quiz attempts with difficulty information
    attempts_with_difficulty = db.query(
        QuizAttempt,
        Quiz.difficulty_level
    ).join(
        Quiz, QuizAttempt.quiz_id == Quiz.id
    ).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at >= start_date,
        QuizAttempt.is_completed == True
    ).all()

    # Group by difficulty level
    difficulty_stats = {'easy': [], 'medium': [], 'hard': []}

    for attempt, difficulty in attempts_with_difficulty:
        if difficulty in difficulty_stats:
            difficulty_stats[difficulty].append(attempt.percentage)

    # Calculate statistics for each difficulty
    result = []
    for level in ['easy', 'medium', 'hard']:
        percentages = difficulty_stats[level]
        if percentages:
            avg_accuracy = sum(percentages) / len(percentages)
            total_questions = len(percentages) * 10  # Assuming average 10 questions per quiz
            result.append(SkillBreakdownPoint(
                level=level.title(),
                accuracy=round(avg_accuracy, 1),
                quizzes_completed=len(percentages),
                total_questions=total_questions
            ))

    return result


@router.get("/me/recent-activities", response_model=List[RecentActivityItem])
def get_recent_activities(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = Query(10, description="Number of activities to return", ge=1, le=50)
) -> Any:
    """
    Get recent learning activities
    """
    from app.models import QuizAttempt, Flashcard, Document

    activities = []

    # Get recent quiz attempts
    quiz_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.is_completed == True
    ).order_by(QuizAttempt.completed_at.desc()).limit(limit).all()

    for attempt in quiz_attempts:
        time_diff = datetime.utcnow() - attempt.completed_at
        time_ago = _format_time_ago(time_diff)

        activities.append(RecentActivityItem(
            id=attempt.id,
            type='quiz',
            title=f'Quiz completed: {attempt.quiz.title}',
            score=f'{attempt.percentage}%',
            time_ago=time_ago,
            created_at=attempt.completed_at
        ))

    # Get recent flashcard reviews
    flashcard_reviews = db.query(Flashcard).filter(
        Flashcard.owner_id == current_user.id,
        Flashcard.updated_at >= datetime.utcnow() - timedelta(days=7)
    ).order_by(Flashcard.updated_at.desc()).limit(limit // 2).all()

    for card in flashcard_reviews:
        time_diff = datetime.utcnow() - card.updated_at
        time_ago = _format_time_ago(time_diff)

        activities.append(RecentActivityItem(
            id=card.id,
            type='flashcard',
            title=f'Reviewed: {card.front_text}',
            score=f'Ease: {card.ease_factor:.1f}',
            time_ago=time_ago,
            created_at=card.updated_at
        ))

    # Get recent documents
    documents = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).order_by(Document.created_at.desc()).limit(limit // 3).all()

    for doc in documents:
        time_diff = datetime.utcnow() - doc.created_at
        time_ago = _format_time_ago(time_diff)

        activities.append(RecentActivityItem(
            id=doc.id,
            type='document',
            title=f'Read: {doc.title or doc.original_filename}',
            score='Completed',
            time_ago=time_ago,
            created_at=doc.created_at
        ))

    # Sort by time and limit results
    activities.sort(key=lambda x: x.created_at, reverse=True)
    return activities[:limit]


@router.get("/me/progress", response_model=ProgressResponse)
def get_full_progress(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    range_days: int = Query(30, description="Number of days to look back", ge=1, le=365)
) -> Any:
    """
    Get complete progress data for the dashboard
    """
    return ProgressResponse(
        stats=get_user_stats(db=db, current_user=current_user, range_days=range_days),
        activity_heatmap=get_activity_heatmap(db=db, current_user=current_user, range_days=range_days),
        performance_history=get_performance_history(db=db, current_user=current_user, range_days=range_days),
        skill_breakdown=get_skill_breakdown(db=db, current_user=current_user, range_days=range_days),
        recent_activities=get_recent_activities(db=db, current_user=current_user, limit=10)
    )


# Helper functions

def _calculate_study_streak(db: Session, user_id: int, since_date: datetime) -> int:
    """
    Calculate current study streak (consecutive days with learning activity)
    """
    from app.models import QuizAttempt, Flashcard, Document

    # Get all activity dates since the start date
    quiz_dates = db.query(cast(QuizAttempt.started_at, Date)).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.started_at >= since_date
    ).distinct().all()

    flashcard_dates = db.query(cast(Flashcard.updated_at, Date)).filter(
        Flashcard.owner_id == user_id,
        Flashcard.updated_at >= since_date
    ).distinct().all()

    document_dates = db.query(cast(Document.created_at, Date)).filter(
        Document.owner_id == user_id,
        Document.created_at >= since_date
    ).distinct().all()

    # Combine all unique dates
    activity_dates = set()
    for date_tuple in quiz_dates + flashcard_dates + document_dates:
        activity_dates.add(date_tuple[0])

    if not activity_dates:
        return 0

    # Sort dates and calculate streak
    sorted_dates = sorted(activity_dates, reverse=True)
    streak = 0
    current_date = date.today()

    for activity_date in sorted_dates:
        expected_date = current_date - timedelta(days=streak)
        if activity_date == expected_date:
            streak += 1
        else:
            break

    return streak


def _format_time_ago(time_diff: timedelta) -> str:
    """
    Format timedelta to human-readable time ago string
    """
    days = time_diff.days
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days} days ago"
    elif hours > 0:
        return f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minutes ago"
    else:
        return "Just now"
