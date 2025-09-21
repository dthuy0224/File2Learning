#!/usr/bin/env python3
"""
Database seeding script for AI Learning Material Generator

This script creates sample data for development and testing purposes.
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt


def create_sample_users(db: Session) -> list[User]:
    """Create sample users"""
    users_data = [
        {
            "email": "john@example.com",
            "username": "john_doe",
            "hashed_password": get_password_hash("password123"),
            "full_name": "John Doe",
            "learning_goals": ["ielts", "business"],
            "difficulty_preference": "medium",
            "daily_study_time": 45
        },
        {
            "email": "mary@example.com",
            "username": "mary_smith",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Mary Smith",
            "learning_goals": ["toeic", "general"],
            "difficulty_preference": "easy",
            "daily_study_time": 30
        },
        {
            "email": "admin@example.com",
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Admin User",
            "is_superuser": True,
            "learning_goals": ["business", "academic"],
            "difficulty_preference": "hard",
            "daily_study_time": 60
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    db.commit()
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
    print("🌱 Starting database seeding...")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("❌ Database already contains data. Skipping seed.")
            return
        
        print("👤 Creating sample users...")
        users = create_sample_users(db)
        print(f"✅ Created {len(users)} users")
        
        print("📄 Creating sample documents...")
        documents = create_sample_documents(db, users)
        print(f"✅ Created {len(documents)} documents")
        
        print("🃏 Creating sample flashcards...")
        create_sample_flashcards(db, users, documents)
        flashcard_count = db.query(Flashcard).count()
        print(f"✅ Created {flashcard_count} flashcards")
        
        print("🧠 Creating sample quizzes...")
        create_sample_quizzes(db, users, documents)
        quiz_count = db.query(Quiz).count()
        question_count = db.query(QuizQuestion).count()
        attempt_count = db.query(QuizAttempt).count()
        print(f"✅ Created {quiz_count} quizzes with {question_count} questions and {attempt_count} attempts")
        
        print("🎉 Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"  Users: {len(users)}")
        print(f"  Documents: {len(documents)}")
        print(f"  Flashcards: {flashcard_count}")
        print(f"  Quizzes: {quiz_count}")
        print(f"  Quiz Questions: {question_count}")
        print(f"  Quiz Attempts: {attempt_count}")
        
        print("\n🔐 Login credentials:")
        print("  john@example.com / password123")
        print("  mary@example.com / password123")
        print("  admin@example.com / admin123")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
