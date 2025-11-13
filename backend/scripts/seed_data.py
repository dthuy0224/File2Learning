#!/usr/bin/env python3
"""
Database seeding script for File2Learning

This script creates sample data for development and testing purposes.
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt
from app.models.learning_profile import LearningProfile
from app.models.learning_goal import LearningGoal
from app.models.study_schedule import StudySchedule, DailyStudyPlan
from app.models.study_session import StudySession


def create_sample_users(db: Session) -> list[User]:
    """Create sample users"""
    users_data = [
        {
            "email": "john@example.com",
            "username": "john_doe",
            "hashed_password": get_password_hash("password123"),
            "full_name": "John Doe",
            "legacy_learning_goals": ["ielts", "business"],  # For backward compatibility
            "difficulty_preference": "medium",
            "daily_study_time": 45,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "mary@example.com",
            "username": "mary_smith",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Mary Smith",
            "legacy_learning_goals": ["toeic", "general"],
            "difficulty_preference": "easy",
            "daily_study_time": 30,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "admin@example.com",
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Admin User",
            "is_superuser": True,
            "legacy_learning_goals": ["business", "academic"],
            "difficulty_preference": "hard",
            "daily_study_time": 60,
            "is_active": True
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    db.commit()
    # Refresh to get IDs
    for user in users:
        db.refresh(user)
    
    return users


def create_sample_documents(db: Session, users: list[User]) -> list[Document]:
    """Create sample documents"""
    documents_data = [
        {
            "filename": "business_english_vocab.pdf",
            "original_filename": "Business English Vocabulary.pdf",
            "file_path": "uploads/business_english_vocab.pdf",
            "file_size": 1234567,
            "document_type": "pdf",
            "content": "This document contains essential business English vocabulary including terms for meetings, presentations, negotiations, and email communication. Key terms include: agenda, quarterly report, stakeholder, ROI, KPI, deadline, milestone, deliverable, profit margin, market share...",
            "title": "Business English Vocabulary",
            "summary": "Comprehensive guide to business English vocabulary covering meetings, presentations, and communications.",
            "word_count": 2450,
            "difficulty_level": "medium",
            "owner_id": users[0].id,
            "processed_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "filename": "ielts_reading_practice.docx",
            "original_filename": "IELTS Reading Practice.docx",
            "file_path": "uploads/ielts_reading_practice.docx",
            "file_size": 987654,
            "document_type": "docx",
            "content": "IELTS Reading practice passages covering topics in science, technology, environment, and society. Practice questions include multiple choice, matching headings, and gap-fill exercises. Vocabulary includes: biodiversity, sustainable, innovative, fundamental, comprehensive, substantial, inevitable, significant...",
            "title": "IELTS Reading Practice",
            "summary": "Practice materials for IELTS Academic Reading with passages and exercises.",
            "word_count": 1850,
            "difficulty_level": "hard",
            "owner_id": users[1].id,
            "processed_at": datetime.utcnow() - timedelta(hours=1)
        },
        {
            "filename": "daily_conversation.txt",
            "original_filename": "Daily Conversation.txt",
            "file_path": "uploads/daily_conversation.txt",
            "file_size": 456789,
            "document_type": "txt",
            "content": "Common phrases and expressions for daily conversation including greetings, shopping, ordering food, asking for directions, and small talk. Examples: How's it going?, I'd like to..., Could you help me?, What do you recommend?, See you later...",
            "title": "Daily Conversation Guide",
            "summary": "Essential phrases for everyday English conversations.",
            "word_count": 1200,
            "difficulty_level": "easy",
            "owner_id": users[0].id,
            "processed_at": datetime.utcnow()
        }
    ]
    
    documents = []
    for doc_data in documents_data:
        document = Document(**doc_data)
        db.add(document)
        documents.append(document)
    
    db.commit()
    # Refresh to get IDs
    for document in documents:
        db.refresh(document)
    return documents


def create_sample_flashcards(db: Session, users: list[User], documents: list[Document]):
    """Create sample flashcards"""
    flashcards_data = [
        # Business vocabulary flashcards
        {
            "front_text": "stakeholder",
            "back_text": "A person with an interest or concern in something, especially a business",
            "example_sentence": "All stakeholders should be informed about the new policy changes.",
            "pronunciation": "/ˈsteɪkˌhoʊldər/",
            "word_type": "noun",
            "ease_factor": 2.5,
            "interval": 1,
            "repetitions": 0,
            "next_review_date": datetime.utcnow() + timedelta(days=1),
            "difficulty_level": "medium",
            "tags": "business,corporate",
            "owner_id": users[0].id,
            "document_id": documents[0].id
        },
        {
            "front_text": "ROI",
            "back_text": "Return on Investment - a measure of the efficiency of an investment",
            "example_sentence": "The marketing campaign showed a positive ROI of 150%.",
            "word_type": "acronym",
            "ease_factor": 2.3,
            "interval": 2,
            "repetitions": 1,
            "next_review_date": datetime.utcnow(),
            "times_reviewed": 1,
            "times_correct": 1,
            "last_review_quality": 4,
            "difficulty_level": "medium",
            "tags": "business,finance",
            "owner_id": users[0].id,
            "document_id": documents[0].id
        },
        # IELTS vocabulary flashcards
        {
            "front_text": "biodiversity",
            "back_text": "The variety of plant and animal life in the world or in a particular habitat",
            "example_sentence": "The rainforest is known for its incredible biodiversity.",
            "pronunciation": "/ˌbaɪoʊdaɪˈvɜrsɪti/",
            "word_type": "noun",
            "ease_factor": 2.7,
            "interval": 3,
            "repetitions": 2,
            "next_review_date": datetime.utcnow() + timedelta(days=2),
            "times_reviewed": 2,
            "times_correct": 2,
            "last_review_quality": 5,
            "difficulty_level": "hard",
            "tags": "ielts,environment,academic",
            "owner_id": users[1].id,
            "document_id": documents[1].id
        }
    ]
    
    for card_data in flashcards_data:
        flashcard = Flashcard(**card_data)
        db.add(flashcard)
    
    db.commit()


def create_sample_learning_profiles(db: Session, users: list[User]):
    """Create learning profiles for users"""
    profiles_data = [
        {
            "user_id": users[0].id,
            "learning_style": "balanced",
            "preferred_difficulty": "medium",
            "optimal_study_times": {"morning": 0.6, "afternoon": 0.7, "evening": 0.9, "night": 0.4},
            "avg_session_duration": 45,
            "avg_daily_study_time": 45,
            "current_streak": 7,
            "longest_streak": 15,
            "overall_retention_rate": Decimal("75.50"),
            "quiz_accuracy_rate": Decimal("78.00"),
            "flashcard_success_rate": Decimal("72.00"),
            "weak_topics": [{"topic": "Grammar", "score": 65, "priority": "high"}],
            "strong_topics": [{"topic": "Vocabulary", "score": 85, "attempts": 30}],
            "learning_velocity": Decimal("1.10"),
            "recommended_daily_load": 45,
            "preferred_study_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "break_preference": 5
        },
        {
            "user_id": users[1].id,
            "learning_style": "visual",
            "preferred_difficulty": "easy",
            "optimal_study_times": {"morning": 0.8, "afternoon": 0.6, "evening": 0.5, "night": 0.3},
            "avg_session_duration": 30,
            "avg_daily_study_time": 30,
            "current_streak": 3,
            "longest_streak": 8,
            "overall_retention_rate": Decimal("68.00"),
            "quiz_accuracy_rate": Decimal("70.00"),
            "flashcard_success_rate": Decimal("65.00"),
            "weak_topics": [{"topic": "Reading", "score": 55, "priority": "high"}],
            "strong_topics": [{"topic": "Speaking", "score": 80, "attempts": 20}],
            "learning_velocity": Decimal("0.90"),
            "recommended_daily_load": 30,
            "preferred_study_days": ["monday", "wednesday", "friday"],
            "break_preference": 10
        },
        {
            "user_id": users[2].id,
            "learning_style": "reading_writing",
            "preferred_difficulty": "hard",
            "optimal_study_times": {"morning": 0.7, "afternoon": 0.8, "evening": 0.9, "night": 0.6},
            "avg_session_duration": 60,
            "avg_daily_study_time": 60,
            "current_streak": 12,
            "longest_streak": 25,
            "overall_retention_rate": Decimal("85.00"),
            "quiz_accuracy_rate": Decimal("88.00"),
            "flashcard_success_rate": Decimal("82.00"),
            "weak_topics": [],
            "strong_topics": [
                {"topic": "Business English", "score": 90, "attempts": 50},
                {"topic": "Academic Writing", "score": 88, "attempts": 40}
            ],
            "learning_velocity": Decimal("1.30"),
            "recommended_daily_load": 60,
            "preferred_study_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
            "break_preference": 5
        }
    ]
    
    for profile_data in profiles_data:
        profile = LearningProfile(**profile_data)
        db.add(profile)
    
    db.commit()


def create_sample_learning_goals(db: Session, users: list[User]) -> list[LearningGoal]:
    """Create learning goals for users"""
    today = date.today()
    
    goals_data = [
        {
            "user_id": users[0].id,
            "goal_type": "exam_preparation",
            "goal_title": "IELTS 6.5",
            "description": "Prepare for IELTS exam and achieve overall band score of 6.5",
            "target_metrics": {
                "exam": "IELTS",
                "target_score": 6.5,
                "sections": ["reading", "writing", "listening", "speaking"]
            },
            "current_progress": {
                "vocabulary": 350,
                "percentage": 35.0,
                "on_track": True,
                "days_active": 20
            },
            "start_date": today - timedelta(days=30),
            "target_date": today + timedelta(days=60),
            "status": "active",
            "priority": "high",
            "is_on_track": True,
            "completion_percentage": 35
        },
        {
            "user_id": users[0].id,
            "goal_type": "vocabulary_count",
            "goal_title": "Learn 500 Business Words",
            "description": "Master 500 essential business English vocabulary words",
            "target_metrics": {"vocabulary": 500, "unit": "words"},
            "current_progress": {
                "vocabulary": 200,
                "percentage": 40.0,
                "on_track": True,
                "days_active": 15
            },
            "start_date": today - timedelta(days=20),
            "target_date": today + timedelta(days=40),
            "status": "active",
            "priority": "medium",
            "is_on_track": True,
            "completion_percentage": 40
        },
        {
            "user_id": users[1].id,
            "goal_type": "time_based",
            "goal_title": "Study 30 Hours",
            "description": "Complete 30 hours of study time over the next 2 months",
            "target_metrics": {"study_time": 30, "unit": "hours"},
            "current_progress": {
                "study_time": 12,
                "percentage": 40.0,
                "on_track": True,
                "days_active": 18
            },
            "start_date": today - timedelta(days=25),
            "target_date": today + timedelta(days=35),
            "status": "active",
            "priority": "medium",
            "is_on_track": True,
            "completion_percentage": 40
        },
        {
            "user_id": users[2].id,
            "goal_type": "topic_mastery",
            "goal_title": "Master Business English",
            "description": "Achieve 90% accuracy in business English topics",
            "target_metrics": {"topic": "Business English", "target_accuracy": 90},
            "current_progress": {
                "accuracy": 85,
                "percentage": 94.4,
                "on_track": True,
                "days_active": 45
            },
            "start_date": today - timedelta(days=60),
            "target_date": today + timedelta(days=30),
            "status": "active",
            "priority": "high",
            "is_on_track": True,
            "completion_percentage": 94
        }
    ]
    
    goals = []
    for goal_data in goals_data:
        goal = LearningGoal(**goal_data)
        db.add(goal)
        goals.append(goal)
    
    db.commit()
    # Refresh to get IDs
    for goal in goals:
        db.refresh(goal)
    
    return goals


def create_sample_study_schedules(db: Session, users: list[User], goals: list[LearningGoal]) -> list[StudySchedule]:
    """Create study schedules for users"""
    schedules_data = [
        {
            "user_id": users[0].id,
            "goal_id": goals[0].id if len(goals) > 0 else None,
            "schedule_name": "IELTS Preparation Schedule",
            "schedule_type": "exam_prep",
            "schedule_config": {
                "daily_minutes": 45,
                "days_per_week": 5,
                "preferred_times": ["18:00-20:00"],
                "activity_distribution": {"flashcards": 0.4, "quizzes": 0.3, "reading": 0.3},
                "difficulty_curve": "gradual",
                "focus_areas": ["Grammar", "Vocabulary"]
            },
            "adaptation_mode": "moderate",
            "max_daily_load": 60,
            "min_daily_load": 30,
            "catch_up_strategy": "gradual",
            "is_active": True,
            "total_days_scheduled": 30,
            "days_completed": 20,
            "days_missed": 2,
            "avg_adherence_rate": Decimal("85.00")
        },
        {
            "user_id": users[1].id,
            "goal_id": goals[2].id if len(goals) > 2 else None,
            "schedule_name": "Daily Practice Routine",
            "schedule_type": "time_based",
            "schedule_config": {
                "daily_minutes": 30,
                "days_per_week": 3,
                "preferred_times": ["09:00-10:00"],
                "activity_distribution": {"flashcards": 0.5, "quizzes": 0.3, "reading": 0.2},
                "difficulty_curve": "adaptive",
                "focus_areas": ["Reading", "Speaking"]
            },
            "adaptation_mode": "flexible",
            "max_daily_load": 45,
            "min_daily_load": 15,
            "catch_up_strategy": "skip",
            "is_active": True,
            "total_days_scheduled": 20,
            "days_completed": 12,
            "days_missed": 3,
            "avg_adherence_rate": Decimal("70.00")
        }
    ]
    
    schedules = []
    for schedule_data in schedules_data:
        schedule = StudySchedule(**schedule_data)
        db.add(schedule)
        schedules.append(schedule)
    
    db.commit()
    # Refresh to get IDs
    for schedule in schedules:
        db.refresh(schedule)
    
    return schedules


def create_sample_daily_plans(db: Session, users: list[User], schedules: list[StudySchedule]):
    """Create daily study plans"""
    today = date.today()
    
    # Create plans for the next 7 days for first user
    for i in range(7):
        plan_date = today + timedelta(days=i)
        is_today = (i == 0)
        
        plan = DailyStudyPlan(
            user_id=users[0].id,
            schedule_id=schedules[0].id if len(schedules) > 0 else None,
            plan_date=plan_date,
            plan_summary=f"Day {i+1}: Review flashcards, practice vocabulary quiz, read business article",
            recommended_tasks=[
                {
                    "type": "flashcard_review",
                    "entity_ids": [1, 2, 3, 4, 5],
                    "count": 15,
                    "estimated_minutes": 10,
                    "priority": "high",
                    "reason": "Due for review (SRS)",
                    "topic": "Grammar"
                },
                {
                    "type": "quiz",
                    "entity_id": 1,
                    "quiz_title": "Business Vocabulary",
                    "estimated_minutes": 15,
                    "priority": "medium",
                    "reason": "Weak topic: Business English"
                }
            ],
            total_estimated_minutes=45,
            actual_minutes_spent=40 if is_today else 0,
            priority_level="normal",
            difficulty_level="medium",
            is_completed=is_today,
            completion_percentage=Decimal("88.89") if is_today else Decimal("0.00"),
            completed_tasks_count=2 if is_today else 0,
            total_tasks_count=2,
            status="completed" if is_today else "pending",
            actual_performance={
                "flashcards": {"reviewed": 15, "correct": 12, "accuracy": 0.8},
                "quizzes": {"completed": 1, "score": 85},
                "overall_accuracy": 82
            } if is_today else None,
            started_at=datetime.utcnow() - timedelta(hours=2) if is_today else None,
            completed_at=datetime.utcnow() - timedelta(hours=1) if is_today else None
        )
        db.add(plan)
    
    db.commit()


def create_sample_study_sessions(db: Session, users: list[User], daily_plans: list[DailyStudyPlan]):
    """Create sample study sessions"""
    # Get today's plan
    today_plan = next((p for p in daily_plans if p.plan_date == date.today()), None)
    
    sessions_data = [
        {
            "user_id": users[0].id,
            "daily_plan_id": today_plan.id if today_plan else None,
            "session_type": "flashcard_review",
            "entity_type": "flashcard",
            "entity_id": 1,
            "duration_seconds": 600,  # 10 minutes
            "started_at": datetime.utcnow() - timedelta(hours=2),
            "ended_at": datetime.utcnow() - timedelta(hours=2, minutes=10),
            "performance_data": {
                "cards_reviewed": 15,
                "correct": 12,
                "incorrect": 3,
                "accuracy": 0.8
            },
            "accuracy_rate": Decimal("80.00"),
            "items_completed": 15,
            "items_correct": 12,
            "device_type": "desktop",
            "time_of_day": "evening",
            "is_planned": True
        },
        {
            "user_id": users[0].id,
            "daily_plan_id": today_plan.id if today_plan else None,
            "session_type": "quiz_taking",
            "entity_type": "quiz",
            "entity_id": 1,
            "duration_seconds": 900,  # 15 minutes
            "started_at": datetime.utcnow() - timedelta(hours=1, minutes=30),
            "ended_at": datetime.utcnow() - timedelta(hours=1, minutes=15),
            "performance_data": {
                "quiz_id": 1,
                "score": 85,
                "max_score": 100,
                "questions_answered": 10
            },
            "accuracy_rate": Decimal("85.00"),
            "items_completed": 10,
            "items_correct": 8,
            "device_type": "desktop",
            "time_of_day": "evening",
            "is_planned": True
        }
    ]
    
    for session_data in sessions_data:
        session = StudySession(**session_data)
        db.add(session)
    
    db.commit()


def create_sample_quizzes(db: Session, users: list[User], documents: list[Document]):
    """Create sample quizzes and questions"""
    # Create Business English Quiz
    business_quiz = Quiz(
        title="Business English Vocabulary Quiz",
        description="Test your knowledge of essential business English terms",
        quiz_type="vocabulary",
        difficulty_level="medium",
        time_limit=15,
        document_id=documents[0].id,
        created_by=users[2].id  # Admin created
    )
    db.add(business_quiz)
    db.commit()
    db.refresh(business_quiz)
    
    # Add questions to business quiz
    business_questions = [
        {
            "question_text": "What does ROI stand for?",
            "question_type": "multiple_choice",
            "options": ["Return on Investment", "Rate of Interest", "Revenue of Income", "Risk of Investment"],
            "correct_answer": "Return on Investment",
            "explanation": "ROI (Return on Investment) measures the efficiency of an investment.",
            "difficulty_level": "medium",
            "points": 2,
            "order_index": 1,
            "quiz_id": business_quiz.id
        },
        {
            "question_text": "A _______ is someone who has an interest in a business or project.",
            "question_type": "fill_blank",
            "correct_answer": "stakeholder",
            "blank_position": 2,
            "explanation": "A stakeholder is a person with an interest or concern in something, especially a business.",
            "difficulty_level": "medium",
            "points": 1,
            "order_index": 2,
            "quiz_id": business_quiz.id
        }
    ]
    
    for q_data in business_questions:
        question = QuizQuestion(**q_data)
        db.add(question)
    
    # Create quiz attempt
    quiz_attempt = QuizAttempt(
        answers={
            "1": "Return on Investment",
            "2": "stakeholder"
        },
        score=3,
        max_score=3,
        percentage=100,
        time_taken=320,  # 5 minutes 20 seconds
        is_completed=True,
        completed_at=datetime.utcnow() - timedelta(hours=2),
        user_id=users[0].id,
        quiz_id=business_quiz.id
    )
    db.add(quiz_attempt)
    
    db.commit()

def seed_database():
    """Main seeding function"""
    print("Starting database seeding...")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already contains data. Skipping seed.")
            return

        print("Creating sample users...")
        users = create_sample_users(db)
        print(f"Created {len(users)} users")

        print("Creating learning profiles...")
        create_sample_learning_profiles(db, users)
        print(f"Created {len(users)} learning profiles")

        print("Creating learning goals...")
        goals = create_sample_learning_goals(db, users)
        print(f"Created {len(goals)} learning goals")

        print("Creating study schedules...")
        schedules = create_sample_study_schedules(db, users, goals)
        print(f"Created {len(schedules)} study schedules")

        print("Creating sample documents...")
        documents = create_sample_documents(db, users)
        print(f"Created {len(documents)} documents")

        print("Creating sample flashcards...")
        create_sample_flashcards(db, users, documents)
        flashcard_count = db.query(Flashcard).count()
        print(f"Created {flashcard_count} flashcards")

        print("Creating sample quizzes...")
        create_sample_quizzes(db, users, documents)
        quiz_count = db.query(Quiz).count()
        question_count = db.query(QuizQuestion).count()
        attempt_count = db.query(QuizAttempt).count()
        print(f"Created {quiz_count} quizzes with {question_count} questions and {attempt_count} attempts")

        print("Creating daily study plans...")
        daily_plans = db.query(DailyStudyPlan).all()
        create_sample_daily_plans(db, users, schedules)
        daily_plan_count = db.query(DailyStudyPlan).count()
        print(f"Created {daily_plan_count} daily study plans")

        print("Creating study sessions...")
        all_daily_plans = db.query(DailyStudyPlan).all()
        create_sample_study_sessions(db, users, all_daily_plans)
        session_count = db.query(StudySession).count()
        print(f"Created {session_count} study sessions")

        print("\n" + "="*60)
        print("Database seeding completed successfully!")
        print("="*60)
        print("\nSummary:")
        print(f"  Users: {len(users)}")
        print(f"  Learning Profiles: {len(users)}")
        print(f"  Learning Goals: {len(goals)}")
        print(f"  Study Schedules: {len(schedules)}")
        print(f"  Daily Study Plans: {daily_plan_count}")
        print(f"  Study Sessions: {session_count}")
        print(f"  Documents: {len(documents)}")
        print(f"  Flashcards: {flashcard_count}")
        print(f"  Quizzes: {quiz_count}")
        print(f"  Quiz Questions: {question_count}")
        print(f"  Quiz Attempts: {attempt_count}")

        print("\nLogin credentials:")
        print("  john@example.com / password123")
        print("  mary@example.com / password123")
        print("  admin@example.com / admin123")

    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
