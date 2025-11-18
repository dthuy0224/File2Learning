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
from app.models.study_session import StudySession, LearningAnalytics
from app.models.recommendation import AdaptiveRecommendation


def create_sample_users(db: Session) -> list[User]:
    """Create sample users"""
    users_data = [
        {
            "email": "john@example.com",
            "username": "john_doe",
            "hashed_password": get_password_hash("password123"),
            "full_name": "John Doe",
            "legacy_learning_goals": ["ielts", "business"],
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
        },
        {
            "email": "david.chen@example.com",
            "username": "davidchen",
            "hashed_password": get_password_hash("password123"),
            "full_name": "David Chen",
            "legacy_learning_goals": ["ielts", "academic"],
            "difficulty_preference": "hard",
            "daily_study_time": 60,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "sarah.johnson@example.com",
            "username": "sarahj",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Sarah Johnson",
            "legacy_learning_goals": ["business", "professional"],
            "difficulty_preference": "medium",
            "daily_study_time": 40,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "michael.brown@example.com",
            "username": "mikebrown",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Michael Brown",
            "legacy_learning_goals": ["toeic", "business"],
            "difficulty_preference": "medium",
            "daily_study_time": 35,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "emily.wilson@example.com",
            "username": "emilyw",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Emily Wilson",
            "legacy_learning_goals": ["general", "conversation"],
            "difficulty_preference": "easy",
            "daily_study_time": 25,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "james.taylor@example.com",
            "username": "jamest",
            "hashed_password": get_password_hash("password123"),
            "full_name": "James Taylor",
            "legacy_learning_goals": ["ielts", "academic"],
            "difficulty_preference": "hard",
            "daily_study_time": 50,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "lisa.anderson@example.com",
            "username": "lisaand",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Lisa Anderson",
            "legacy_learning_goals": ["business", "professional"],
            "difficulty_preference": "medium",
            "daily_study_time": 45,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "robert.martinez@example.com",
            "username": "robmart",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Robert Martinez",
            "legacy_learning_goals": ["general", "travel"],
            "difficulty_preference": "easy",
            "daily_study_time": 20,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "jennifer.lee@example.com",
            "username": "jenlee",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Jennifer Lee",
            "legacy_learning_goals": ["toeic", "business"],
            "difficulty_preference": "medium",
            "daily_study_time": 40,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "william.garcia@example.com",
            "username": "willg",
            "hashed_password": get_password_hash("password123"),
            "full_name": "William Garcia",
            "legacy_learning_goals": ["ielts", "academic"],
            "difficulty_preference": "hard",
            "daily_study_time": 55,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "patricia.davis@example.com",
            "username": "patdavis",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Patricia Davis",
            "legacy_learning_goals": ["business", "professional"],
            "difficulty_preference": "medium",
            "daily_study_time": 35,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "daniel.rodriguez@example.com",
            "username": "danrod",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Daniel Rodriguez",
            "legacy_learning_goals": ["general", "conversation"],
            "difficulty_preference": "easy",
            "daily_study_time": 30,
            "is_active": True,
            "is_superuser": False
        },
        {
            "email": "nancy.miller@example.com",
            "username": "nancym",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Nancy Miller",
            "legacy_learning_goals": ["toeic", "business"],
            "difficulty_preference": "medium",
            "daily_study_time": 45,
            "is_active": True,
            "is_superuser": False
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
        # User 0 (John)
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
            "processed_at": datetime.utcnow() - timedelta(hours=2),
            "processing_status": "completed",
            "content_quality": "good"
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
            "processed_at": datetime.utcnow(),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 1 (Mary)
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
            "processed_at": datetime.utcnow() - timedelta(hours=1),
            "processing_status": "completed",
            "content_quality": "excellent"
        },
        {
            "filename": "toeic_vocabulary.pdf",
            "original_filename": "TOEIC Vocabulary.pdf",
            "file_path": "uploads/toeic_vocabulary.pdf",
            "file_size": 1567890,
            "document_type": "pdf",
            "content": "TOEIC vocabulary list covering common words and phrases used in business and professional settings. Topics include: office communication, business travel, human resources, marketing, finance, and technology.",
            "title": "TOEIC Vocabulary Guide",
            "summary": "Essential vocabulary for TOEIC test preparation.",
            "word_count": 3200,
            "difficulty_level": "medium",
            "owner_id": users[1].id,
            "processed_at": datetime.utcnow() - timedelta(days=1),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 2 (Admin)
        {
            "filename": "academic_writing_guide.pdf",
            "original_filename": "Academic Writing Guide.pdf",
            "file_path": "uploads/academic_writing_guide.pdf",
            "file_size": 2345678,
            "document_type": "pdf",
            "content": "Comprehensive guide to academic writing covering essay structure, citation styles, argumentation, and formal language. Includes examples of thesis statements, introductions, body paragraphs, and conclusions.",
            "title": "Academic Writing Guide",
            "summary": "Complete guide to academic writing techniques and structures.",
            "word_count": 4500,
            "difficulty_level": "hard",
            "owner_id": users[2].id,
            "processed_at": datetime.utcnow() - timedelta(days=2),
            "processing_status": "completed",
            "content_quality": "excellent"
        },
        # User 3 (David)
        {
            "filename": "ielts_writing_samples.pdf",
            "original_filename": "IELTS Writing Samples.pdf",
            "file_path": "uploads/ielts_writing_samples.pdf",
            "file_size": 1897654,
            "document_type": "pdf",
            "content": "Sample IELTS writing tasks with model answers and feedback. Includes Task 1 (report writing) and Task 2 (essay writing) examples with band scores and detailed explanations.",
            "title": "IELTS Writing Samples",
            "summary": "Sample IELTS writing tasks with model answers.",
            "word_count": 3800,
            "difficulty_level": "hard",
            "owner_id": users[3].id,
            "processed_at": datetime.utcnow() - timedelta(days=1),
            "processing_status": "completed",
            "content_quality": "excellent"
        },
        {
            "filename": "academic_reading_passages.docx",
            "original_filename": "Academic Reading Passages.docx",
            "file_path": "uploads/academic_reading_passages.docx",
            "file_size": 1123456,
            "document_type": "docx",
            "content": "Academic reading passages on various topics: climate change, urban development, psychology, economics, and technology. Each passage includes comprehension questions and vocabulary exercises.",
            "title": "Academic Reading Passages",
            "summary": "Collection of academic reading passages with exercises.",
            "word_count": 2800,
            "difficulty_level": "hard",
            "owner_id": users[3].id,
            "processed_at": datetime.utcnow() - timedelta(hours=12),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 4 (Sarah)
        {
            "filename": "business_meetings_phrases.pdf",
            "original_filename": "Business Meetings Phrases.pdf",
            "file_path": "uploads/business_meetings_phrases.pdf",
            "file_size": 987654,
            "document_type": "pdf",
            "content": "Useful phrases for business meetings: opening meetings, expressing opinions, agreeing and disagreeing, making suggestions, and closing meetings. Perfect for professionals working in international business.",
            "title": "Business Meeting Phrases",
            "summary": "Essential phrases for effective business meetings.",
            "word_count": 1650,
            "difficulty_level": "medium",
            "owner_id": users[4].id,
            "processed_at": datetime.utcnow() - timedelta(hours=6),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 5 (Michael)
        {
            "filename": "toeic_reading_comprehension.pdf",
            "original_filename": "TOEIC Reading Comprehension.pdf",
            "file_path": "uploads/toeic_reading_comprehension.pdf",
            "file_size": 1456789,
            "document_type": "pdf",
            "content": "TOEIC reading comprehension practice tests with passages on business topics, advertisements, emails, and articles. Includes answer keys and explanations.",
            "title": "TOEIC Reading Comprehension",
            "summary": "TOEIC reading comprehension practice materials.",
            "word_count": 2200,
            "difficulty_level": "medium",
            "owner_id": users[5].id,
            "processed_at": datetime.utcnow() - timedelta(days=3),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 6 (Emily)
        {
            "filename": "travel_english_phrases.txt",
            "original_filename": "Travel English Phrases.txt",
            "file_path": "uploads/travel_english_phrases.txt",
            "file_size": 456789,
            "document_type": "txt",
            "content": "Essential English phrases for travelers: at the airport, hotel check-in, ordering food, shopping, asking for directions, and emergency situations. Practical vocabulary for everyday travel situations.",
            "title": "Travel English Phrases",
            "summary": "Essential phrases for English travelers.",
            "word_count": 980,
            "difficulty_level": "easy",
            "owner_id": users[6].id,
            "processed_at": datetime.utcnow() - timedelta(hours=4),
            "processing_status": "completed",
            "content_quality": "good"
        },
        {
            "filename": "casual_conversation_topics.txt",
            "original_filename": "Casual Conversation Topics.txt",
            "file_path": "uploads/casual_conversation_topics.txt",
            "file_size": 345678,
            "document_type": "txt",
            "content": "Topics and questions for casual English conversations: hobbies, weather, weekend plans, movies, books, sports, and more. Includes conversation starters and follow-up questions.",
            "title": "Casual Conversation Topics",
            "summary": "Topics and phrases for casual English conversations.",
            "word_count": 750,
            "difficulty_level": "easy",
            "owner_id": users[6].id,
            "processed_at": datetime.utcnow() - timedelta(hours=2),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 7 (James)
        {
            "filename": "ielts_listening_practice.pdf",
            "original_filename": "IELTS Listening Practice.pdf",
            "file_path": "uploads/ielts_listening_practice.pdf",
            "file_size": 1678901,
            "document_type": "pdf",
            "content": "IELTS listening practice exercises covering various accents and topics: academic lectures, everyday conversations, and monologues. Includes transcripts and answer keys.",
            "title": "IELTS Listening Practice",
            "summary": "IELTS listening practice materials with transcripts.",
            "word_count": 3100,
            "difficulty_level": "hard",
            "owner_id": users[7].id,
            "processed_at": datetime.utcnow() - timedelta(days=2),
            "processing_status": "completed",
            "content_quality": "excellent"
        },
        # User 8 (Lisa)
        {
            "filename": "professional_email_writing.pdf",
            "original_filename": "Professional Email Writing.pdf",
            "file_path": "uploads/professional_email_writing.pdf",
            "file_size": 1345678,
            "document_type": "pdf",
            "content": "Guide to writing professional emails: greetings, formal language, requesting information, scheduling meetings, following up, and closing. Includes templates and examples.",
            "title": "Professional Email Writing",
            "summary": "Complete guide to professional email communication.",
            "word_count": 2600,
            "difficulty_level": "medium",
            "owner_id": users[8].id,
            "processed_at": datetime.utcnow() - timedelta(days=1),
            "processing_status": "completed",
            "content_quality": "excellent"
        },
        # User 9 (Robert)
        {
            "filename": "restaurant_ordering_guide.txt",
            "original_filename": "Restaurant Ordering Guide.txt",
            "file_path": "uploads/restaurant_ordering_guide.txt",
            "file_size": 234567,
            "document_type": "txt",
            "content": "English phrases for ordering food in restaurants: asking for recommendations, dietary restrictions, making special requests, and paying the bill.",
            "title": "Restaurant Ordering Guide",
            "summary": "Essential phrases for ordering food in English.",
            "word_count": 520,
            "difficulty_level": "easy",
            "owner_id": users[9].id,
            "processed_at": datetime.utcnow() - timedelta(hours=8),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 10 (Jennifer)
        {
            "filename": "toeic_grammar_guide.pdf",
            "original_filename": "TOEIC Grammar Guide.pdf",
            "file_path": "uploads/toeic_grammar_guide.pdf",
            "file_size": 1789012,
            "document_type": "pdf",
            "content": "TOEIC grammar review covering tenses, passive voice, conditionals, modals, and complex sentence structures. Includes practice exercises and answer keys.",
            "title": "TOEIC Grammar Guide",
            "summary": "Comprehensive TOEIC grammar review and practice.",
            "word_count": 3400,
            "difficulty_level": "medium",
            "owner_id": users[10].id,
            "processed_at": datetime.utcnow() - timedelta(days=2),
            "processing_status": "completed",
            "content_quality": "excellent"
        },
        # User 11 (William)
        {
            "filename": "academic_vocabulary_list.pdf",
            "original_filename": "Academic Vocabulary List.pdf",
            "file_path": "uploads/academic_vocabulary_list.pdf",
            "file_size": 2123456,
            "document_type": "pdf",
            "content": "Academic Word List (AWL) with definitions, example sentences, and collocations. Essential vocabulary for academic reading and writing.",
            "title": "Academic Vocabulary List",
            "summary": "Comprehensive academic vocabulary list with examples.",
            "word_count": 4200,
            "difficulty_level": "hard",
            "owner_id": users[11].id,
            "processed_at": datetime.utcnow() - timedelta(days=3),
            "processing_status": "completed",
            "content_quality": "excellent"
        },
        # User 12 (Patricia)
        {
            "filename": "presentation_skills_guide.pdf",
            "original_filename": "Presentation Skills Guide.pdf",
            "file_path": "uploads/presentation_skills_guide.pdf",
            "file_size": 1456789,
            "document_type": "pdf",
            "content": "English phrases and vocabulary for giving presentations: introductions, transitions, explaining data, handling questions, and conclusions.",
            "title": "Presentation Skills Guide",
            "summary": "Essential phrases for professional presentations.",
            "word_count": 2800,
            "difficulty_level": "medium",
            "owner_id": users[12].id,
            "processed_at": datetime.utcnow() - timedelta(days=1),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 13 (Daniel)
        {
            "filename": "daily_small_talk.txt",
            "original_filename": "Daily Small Talk.txt",
            "file_path": "uploads/daily_small_talk.txt",
            "file_size": 345678,
            "document_type": "txt",
            "content": "Small talk phrases for daily interactions: weather, weekend plans, work, family, and general chit-chat. Perfect for building conversational confidence.",
            "title": "Daily Small Talk",
            "summary": "Phrases for everyday small talk in English.",
            "word_count": 650,
            "difficulty_level": "easy",
            "owner_id": users[13].id,
            "processed_at": datetime.utcnow() - timedelta(hours=5),
            "processing_status": "completed",
            "content_quality": "good"
        },
        # User 14 (Nancy)
        {
            "filename": "business_negotiations.pdf",
            "original_filename": "Business Negotiations.pdf",
            "file_path": "uploads/business_negotiations.pdf",
            "file_size": 1890123,
            "document_type": "pdf",
            "content": "English vocabulary and phrases for business negotiations: making offers, bargaining, reaching agreements, and handling disagreements professionally.",
            "title": "Business Negotiations",
            "summary": "Vocabulary and phrases for business negotiations.",
            "word_count": 3600,
            "difficulty_level": "medium",
            "owner_id": users[14].id,
            "processed_at": datetime.utcnow() - timedelta(days=2),
            "processing_status": "completed",
            "content_quality": "excellent"
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
    import random
    
        # Business vocabulary flashcards
    business_vocab = [
        ("stakeholder", "A person with an interest or concern in something, especially a business", "All stakeholders should be informed about the new policy changes.", "/ˈsteɪkˌhoʊldər/"),
        ("ROI", "Return on Investment - a measure of the efficiency of an investment", "The marketing campaign showed a positive ROI of 150%.", None),
        ("KPI", "Key Performance Indicator - a measurable value that shows how effectively a company is achieving objectives", "Our main KPI this quarter is customer satisfaction.", None),
        ("deadline", "The latest time or date by which something should be completed", "We need to meet the deadline for the project submission.", "/ˈdɛdlaɪn/"),
        ("milestone", "An important event or stage in the development of something", "Completing the prototype was a major milestone.", "/ˈmaɪlstoʊn/"),
        ("deliverable", "Something that can be provided, especially as a product of a development process", "The final deliverable for this project is the software documentation.", "/dɪˈlɪvərəbəl/"),
        ("quarterly", "Occurring once every quarter of a year", "We review our performance quarterly.", "/ˈkwɔrtərli/"),
        ("agenda", "A list of items to be discussed at a formal meeting", "The meeting agenda includes budget review and new projects.", "/əˈdʒɛndə/"),
        ("profit margin", "The percentage of revenue that exceeds the costs", "Our profit margin increased by 5% this year.", None),
        ("market share", "The percentage of total sales in a market generated by a particular company", "Our company has a 30% market share in this sector.", None),
    ]
    
    # IELTS/Academic vocabulary
    academic_vocab = [
        ("biodiversity", "The variety of plant and animal life in the world or in a particular habitat", "The rainforest is known for its incredible biodiversity.", "/ˌbaɪoʊdaɪˈvɜrsɪti/"),
        ("sustainable", "Able to be maintained at a certain rate or level", "We need to find sustainable energy solutions.", "/səˈsteɪnəbəl/"),
        ("innovative", "Featuring new methods; advanced and original", "The company is known for its innovative approach to technology.", "/ˈɪnəveɪtɪv/"),
        ("fundamental", "Forming a necessary base or core; of central importance", "Understanding grammar is fundamental to learning a language.", "/ˌfʌndəˈmentəl/"),
        ("comprehensive", "Complete and including everything that is necessary", "We need a comprehensive review of the situation.", "/ˌkɑmprɪˈhensɪv/"),
        ("substantial", "Of considerable importance, size, or worth", "The project requires substantial investment.", "/səbˈstænʃəl/"),
        ("inevitable", "Certain to happen; unavoidable", "Change in technology is inevitable.", "/ɪˈnevɪtəbəl/"),
        ("significant", "Sufficiently great or important to be worthy of attention", "There was a significant increase in sales.", "/sɪɡˈnɪfɪkənt/"),
        ("hypothesis", "A supposition or proposed explanation made on the basis of limited evidence", "Scientists test their hypothesis through experiments.", "/haɪˈpɑθəsɪs/"),
        ("methodology", "A system of methods used in a particular area of study or activity", "The research methodology was clearly explained.", "/ˌmeθəˈdɑlədʒi/"),
    ]
    
    # TOEIC vocabulary
    toeic_vocab = [
        ("commute", "Travel some distance between one's home and place of work on a regular basis", "I commute to work by train every day.", "/kəˈmjuːt/"),
        ("subsidiary", "A company controlled by a holding company", "The company opened a subsidiary in Asia.", "/səbˈsɪdiəri/"),
        ("warehouse", "A large building where raw materials or manufactured goods may be stored", "The products are stored in the warehouse.", "/ˈwɛrhaʊs/"),
        ("invoice", "A list of goods sent or services provided, with a statement of the sum due", "Please send me the invoice for the services.", "/ˈɪnvɔɪs/"),
        ("receipt", "A written acknowledgment that something has been received", "Keep your receipt in case you need to return the item.", "/rɪˈsiːt/"),
    ]
    
    # General/Travel vocabulary
    general_vocab = [
        ("excuse me", "Used to politely get someone's attention or ask to pass", "Excuse me, could you tell me where the restroom is?", None),
        ("I'd like to", "Used to politely express a wish or preference", "I'd like to order the salmon, please.", None),
        ("Could you help me?", "A polite way to ask for assistance", "Could you help me find the train station?", None),
        ("What do you recommend?", "Asking for someone's suggestion", "What do you recommend from the menu?", None),
        ("See you later", "A casual way to say goodbye", "Thanks for your help, see you later!", None),
    ]
    
    flashcards_data = []
    
    # Add business flashcards for user 0
    for word, defn, example, pron in business_vocab[:5]:
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "noun" if word not in ["ROI", "KPI"] else "acronym",
            "ease_factor": round(2.3 + random.random() * 0.4, 2),
            "interval": random.randint(1, 3),
            "repetitions": random.randint(0, 3),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(0, 3)),
            "times_reviewed": random.randint(0, 5),
            "times_correct": random.randint(0, 5),
            "last_review_quality": random.randint(3, 5) if random.random() > 0.3 else None,
            "difficulty_level": "medium",
            "tags": "business,corporate",
            "owner_id": users[0].id,
            "document_id": documents[0].id if documents else None
        })
    
    # Add IELTS flashcards for user 1
    for word, defn, example, pron in academic_vocab[:5]:
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "noun" if word.endswith("ity") or word.endswith("sis") else "adjective",
            "ease_factor": round(2.5 + random.random() * 0.4, 2),
            "interval": random.randint(2, 5),
            "repetitions": random.randint(1, 5),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(1, 5)),
            "times_reviewed": random.randint(1, 8),
            "times_correct": random.randint(1, 8),
            "last_review_quality": random.randint(3, 5),
            "difficulty_level": "hard",
            "tags": "ielts,academic",
            "owner_id": users[1].id,
            "document_id": documents[2].id if len(documents) > 2 else None
        })
    
    # Add TOEIC flashcards for user 1
    for word, defn, example, pron in toeic_vocab:
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "noun" if word != "commute" else "verb",
            "ease_factor": round(2.2 + random.random() * 0.5, 2),
            "interval": random.randint(1, 4),
            "repetitions": random.randint(0, 4),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(0, 4)),
            "times_reviewed": random.randint(0, 6),
            "times_correct": random.randint(0, 6),
            "last_review_quality": random.randint(3, 5) if random.random() > 0.4 else None,
            "difficulty_level": "medium",
            "tags": "toeic,business",
            "owner_id": users[1].id,
            "document_id": documents[3].id if len(documents) > 3 else None
        })
    
    # Add general flashcards for user 0
    for word, defn, example, pron in general_vocab:
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "phrase",
            "ease_factor": round(2.0 + random.random() * 0.3, 2),
            "interval": random.randint(1, 2),
            "repetitions": random.randint(0, 2),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(0, 2)),
            "times_reviewed": random.randint(0, 3),
            "times_correct": random.randint(0, 3),
            "last_review_quality": random.randint(3, 5) if random.random() > 0.5 else None,
            "difficulty_level": "easy",
            "tags": "general,conversation",
            "owner_id": users[0].id,
            "document_id": documents[1].id if len(documents) > 1 else None
        })
    
    # Add flashcards for other users
    # User 3 (David) - IELTS vocabulary
    for word, defn, example, pron in academic_vocab[5:10]:
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "adjective" if word.endswith("ive") or word.endswith("al") or word.endswith("ant") else "noun",
            "ease_factor": round(2.4 + random.random() * 0.4, 2),
            "interval": random.randint(2, 6),
            "repetitions": random.randint(1, 6),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(1, 6)),
            "times_reviewed": random.randint(1, 10),
            "times_correct": random.randint(1, 10),
            "last_review_quality": random.randint(4, 5),
            "difficulty_level": "hard",
            "tags": "ielts,academic",
            "owner_id": users[3].id,
            "document_id": documents[5].id if len(documents) > 5 else None
        })
    
    # User 4 (Sarah) - Business phrases
    business_phrases = [
        ("on the same page", "Having the same understanding or opinion", "Let's make sure we're all on the same page before proceeding.", None),
        ("think outside the box", "Think creatively, unconventionally", "We need to think outside the box to solve this problem.", None),
        ("ballpark figure", "An approximate number", "Can you give me a ballpark figure for the project cost?", None),
        ("touch base", "Make contact with someone", "Let's touch base next week to discuss progress.", None),
        ("action item", "A task that needs to be completed", "We have three action items from today's meeting.", None),
    ]
    
    for word, defn, example, pron in business_phrases:
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "phrase",
            "ease_factor": round(2.1 + random.random() * 0.4, 2),
            "interval": random.randint(1, 3),
            "repetitions": random.randint(0, 4),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(0, 3)),
            "times_reviewed": random.randint(0, 5),
            "times_correct": random.randint(0, 5),
            "last_review_quality": random.randint(3, 5) if random.random() > 0.3 else None,
            "difficulty_level": "medium",
            "tags": "business,idiom",
            "owner_id": users[4].id,
            "document_id": documents[7].id if len(documents) > 7 else None
        })
    
    # User 5 (Michael) - TOEIC vocabulary
    for word, defn, example, pron in toeic_vocab * 2:  # Repeat to have more cards
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "noun" if word != "commute" else "verb",
            "ease_factor": round(2.2 + random.random() * 0.5, 2),
            "interval": random.randint(1, 4),
            "repetitions": random.randint(0, 5),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(0, 4)),
            "times_reviewed": random.randint(0, 7),
            "times_correct": random.randint(0, 7),
            "last_review_quality": random.randint(3, 5) if random.random() > 0.4 else None,
            "difficulty_level": "medium",
            "tags": "toeic,business",
            "owner_id": users[5].id,
            "document_id": documents[8].id if len(documents) > 8 else None
        })
    
    # User 6 (Emily) - Travel phrases
    travel_phrases = [
        ("check-in", "Register one's arrival, especially at a hotel or airport", "We need to check-in at the hotel before 3 PM.", None),
        ("boarding pass", "A card or document that allows a passenger to board an airplane", "Please have your boarding pass ready.", None),
        ("carry-on", "A piece of luggage that can be taken into the passenger cabin", "This bag is too large to be a carry-on.", None),
        ("currency exchange", "A place where you can exchange one currency for another", "Where is the currency exchange counter?", None),
        ("hotel reservation", "A booking for a hotel room", "I have a hotel reservation under my name.", None),
    ]
    
    for word, defn, example, pron in travel_phrases:
        flashcards_data.append({
            "front_text": word,
            "back_text": defn,
            "example_sentence": example,
            "pronunciation": pron,
            "word_type": "noun" if " " in word else "phrase",
            "ease_factor": round(1.9 + random.random() * 0.4, 2),
            "interval": random.randint(1, 2),
            "repetitions": random.randint(0, 3),
            "next_review_date": datetime.utcnow() + timedelta(days=random.randint(0, 2)),
            "times_reviewed": random.randint(0, 4),
            "times_correct": random.randint(0, 4),
            "last_review_quality": random.randint(3, 5) if random.random() > 0.5 else None,
            "difficulty_level": "easy",
            "tags": "travel,general",
            "owner_id": users[6].id,
            "document_id": documents[9].id if len(documents) > 9 else None
        })
    
    # Add more flashcards for remaining users - spread across different topics
    for user_idx in range(7, min(15, len(users))):
        doc_idx = min(user_idx, len(documents) - 1) if documents else None
        vocab_sets = [business_vocab[5:], academic_vocab[:5], toeic_vocab, general_vocab]
        vocab_set = random.choice(vocab_sets)
        
        for word, defn, example, pron in vocab_set[:3]:  # 3 cards per user
            flashcards_data.append({
                "front_text": word,
                "back_text": defn,
                "example_sentence": example,
                "pronunciation": pron,
                "word_type": "noun" if random.random() > 0.5 else "adjective",
                "ease_factor": round(2.0 + random.random() * 0.6, 2),
                "interval": random.randint(1, 5),
                "repetitions": random.randint(0, 5),
                "next_review_date": datetime.utcnow() + timedelta(days=random.randint(0, 5)),
                "times_reviewed": random.randint(0, 7),
                "times_correct": random.randint(0, 7),
                "last_review_quality": random.randint(2, 5) if random.random() > 0.4 else None,
                "difficulty_level": random.choice(["easy", "medium", "hard"]),
                "tags": random.choice(["business", "ielts", "toeic", "general"]),
                "owner_id": users[user_idx].id,
                "document_id": documents[doc_idx].id if doc_idx is not None else None
            })
    
    for card_data in flashcards_data:
        flashcard = Flashcard(**card_data)
        db.add(flashcard)
    
    db.commit()


def create_sample_learning_profiles(db: Session, users: list[User]):
    """Create learning profiles for users"""
    import random
    
    # Profile templates with variations
    profile_templates = [
        {
            "learning_style": "balanced",
            "preferred_difficulty": "medium",
            "optimal_study_times": {"morning": 0.6, "afternoon": 0.7, "evening": 0.9, "night": 0.4},
            "preferred_study_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "break_preference": 5,
            "streak_range": (5, 20),
            "retention_range": (70, 80),
            "accuracy_range": (73, 82),
        },
        {
            "learning_style": "visual",
            "preferred_difficulty": "easy",
            "optimal_study_times": {"morning": 0.8, "afternoon": 0.6, "evening": 0.5, "night": 0.3},
            "preferred_study_days": ["monday", "wednesday", "friday"],
            "break_preference": 10,
            "streak_range": (2, 12),
            "retention_range": (60, 75),
            "accuracy_range": (65, 75),
        },
        {
            "learning_style": "reading_writing",
            "preferred_difficulty": "hard",
            "optimal_study_times": {"morning": 0.7, "afternoon": 0.8, "evening": 0.9, "night": 0.6},
            "preferred_study_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
            "break_preference": 5,
            "streak_range": (10, 30),
            "retention_range": (80, 90),
            "accuracy_range": (82, 92),
        },
        {
            "learning_style": "auditory",
            "preferred_difficulty": "medium",
            "optimal_study_times": {"morning": 0.5, "afternoon": 0.7, "evening": 0.8, "night": 0.6},
            "preferred_study_days": ["monday", "tuesday", "thursday", "friday"],
            "break_preference": 8,
            "streak_range": (4, 18),
            "retention_range": (68, 78),
            "accuracy_range": (70, 80),
        },
        {
            "learning_style": "kinesthetic",
            "preferred_difficulty": "medium",
            "optimal_study_times": {"morning": 0.6, "afternoon": 0.9, "evening": 0.7, "night": 0.4},
            "preferred_study_days": ["tuesday", "wednesday", "thursday", "saturday"],
            "break_preference": 12,
            "streak_range": (3, 15),
            "retention_range": (65, 75),
            "accuracy_range": (68, 78),
        },
    ]
    
    profiles_data = []
    
    # Create profiles for all users
    for i, user in enumerate(users):
        template = profile_templates[i % len(profile_templates)]
        daily_time = user.daily_study_time or 30
        
        current_streak = random.randint(*template["streak_range"])
        longest_streak = random.randint(current_streak, current_streak + random.randint(5, 15))
        
        retention = random.uniform(*template["retention_range"])
        quiz_acc = random.uniform(*template["accuracy_range"])
        flashcard_acc = quiz_acc - random.uniform(3, 8)
        
        # Weak and strong topics
        weak_topics = [
            {"topic": random.choice(["Grammar", "Reading", "Writing", "Listening"]), 
             "score": random.randint(50, 70), "priority": "high"}
        ] if random.random() > 0.3 else []
        
        strong_topics = [
            {"topic": random.choice(["Vocabulary", "Speaking", "Business English", "Conversation"]), 
             "score": random.randint(80, 95), "attempts": random.randint(15, 50)}
        ] if random.random() > 0.2 else []
        
        profiles_data.append({
            "user_id": user.id,
            "learning_style": template["learning_style"],
            "preferred_difficulty": template["preferred_difficulty"],
            "optimal_study_times": template["optimal_study_times"],
            "avg_session_duration": daily_time,
            "avg_daily_study_time": daily_time,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "overall_retention_rate": Decimal(f"{retention:.2f}"),
            "quiz_accuracy_rate": Decimal(f"{quiz_acc:.2f}"),
            "flashcard_success_rate": Decimal(f"{flashcard_acc:.2f}"),
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "learning_velocity": Decimal(f"{random.uniform(0.85, 1.35):.2f}"),
            "recommended_daily_load": daily_time,
            "preferred_study_days": template["preferred_study_days"],
            "break_preference": template["break_preference"]
        })
    
    for profile_data in profiles_data:
        profile = LearningProfile(**profile_data)
        db.add(profile)
    
    db.commit()


def create_sample_learning_goals(db: Session, users: list[User]) -> list[LearningGoal]:
    """Create learning goals for users"""
    import random
    today = date.today()
    
    # Goal templates
    goal_templates = [
        # IELTS goals
        {"goal_type": "exam_preparation", "title_prefix": "IELTS", "scores": [6.0, 6.5, 7.0, 7.5]},
        # TOEIC goals
        {"goal_type": "exam_preparation", "title_prefix": "TOEIC", "scores": [600, 700, 800, 850]},
        # Vocabulary goals
        {"goal_type": "vocabulary_count", "title_prefix": "Learn", "counts": [300, 500, 700, 1000]},
        # Time-based goals
        {"goal_type": "time_based", "title_prefix": "Study", "hours": [20, 30, 50, 100]},
        # Topic mastery
        {"goal_type": "topic_mastery", "topics": ["Business English", "Grammar", "Academic Writing", "Conversation"]},
    ]
    
    goals_data = []
    
    # Create 1-2 goals per user
    for user_idx, user in enumerate(users):
        num_goals = random.randint(1, 2)
        
        for _ in range(num_goals):
            template = random.choice(goal_templates)
            days_started = random.randint(10, 60)
            days_remaining = random.randint(30, 90)
            
            if template["goal_type"] == "exam_preparation":
                score = random.choice(template["scores"])
                exam_type = template["title_prefix"]
                current_progress_val = random.randint(int(score * 50), int(score * 80))
                percentage = min(100, int((current_progress_val / (score * 100)) * 100))
                
                goals_data.append({
                    "user_id": user.id,
            "goal_type": "exam_preparation",
                    "goal_title": f"{exam_type} {score}" if isinstance(score, float) else f"{exam_type} {score}",
                    "description": f"Prepare for {exam_type} exam and achieve score of {score}",
            "target_metrics": {
                        "exam": exam_type,
                        "target_score": score,
                        "sections": ["reading", "writing", "listening", "speaking"] if exam_type == "IELTS" else ["listening", "reading"]
            },
            "current_progress": {
                        "vocabulary": current_progress_val,
                        "percentage": float(percentage),
                        "on_track": percentage >= 30,
                        "days_active": days_started
                    },
                    "start_date": today - timedelta(days=days_started),
                    "target_date": today + timedelta(days=days_remaining),
            "status": "active",
                    "priority": random.choice(["high", "medium", "high"]),
                    "is_on_track": percentage >= 30,
                    "completion_percentage": percentage
                })
            
            elif template["goal_type"] == "vocabulary_count":
                count = random.choice(template["counts"])
                current = random.randint(count // 3, int(count * 0.8))
                percentage = int((current / count) * 100)
                
                goals_data.append({
                    "user_id": user.id,
            "goal_type": "vocabulary_count",
                    "goal_title": f"Learn {count} Words",
                    "description": f"Master {count} essential English vocabulary words",
                    "target_metrics": {"vocabulary": count, "unit": "words"},
            "current_progress": {
                        "vocabulary": current,
                        "percentage": float(percentage),
                        "on_track": percentage >= 25,
                        "days_active": days_started
                    },
                    "start_date": today - timedelta(days=days_started),
                    "target_date": today + timedelta(days=days_remaining),
            "status": "active",
                    "priority": random.choice(["medium", "high", "medium"]),
                    "is_on_track": percentage >= 25,
                    "completion_percentage": percentage
                })
            
            elif template["goal_type"] == "time_based":
                hours = random.choice(template["hours"])
                current_hours = random.randint(hours // 3, int(hours * 0.7))
                percentage = int((current_hours / hours) * 100)
                
                goals_data.append({
                    "user_id": user.id,
            "goal_type": "time_based",
                    "goal_title": f"Study {hours} Hours",
                    "description": f"Complete {hours} hours of study time",
                    "target_metrics": {"study_time": hours, "unit": "hours"},
            "current_progress": {
                        "study_time": current_hours,
                        "percentage": float(percentage),
                        "on_track": percentage >= 30,
                        "days_active": days_started
                    },
                    "start_date": today - timedelta(days=days_started),
                    "target_date": today + timedelta(days=days_remaining),
            "status": "active",
                    "priority": random.choice(["medium", "low", "medium"]),
                    "is_on_track": percentage >= 30,
                    "completion_percentage": percentage
                })
            
            elif template["goal_type"] == "topic_mastery":
                topic = random.choice(template["topics"])
                target_acc = random.choice([85, 90, 95])
                current_acc = random.randint(target_acc - 15, target_acc - 2)
                percentage = int((current_acc / target_acc) * 100)
                
                goals_data.append({
                    "user_id": user.id,
            "goal_type": "topic_mastery",
                    "goal_title": f"Master {topic}",
                    "description": f"Achieve {target_acc}% accuracy in {topic} topics",
                    "target_metrics": {"topic": topic, "target_accuracy": target_acc},
            "current_progress": {
                        "accuracy": current_acc,
                        "percentage": float(percentage),
                        "on_track": percentage >= 70,
                        "days_active": days_started
                    },
                    "start_date": today - timedelta(days=days_started),
                    "target_date": today + timedelta(days=days_remaining),
            "status": "active",
                    "priority": random.choice(["high", "medium", "high"]),
                    "is_on_track": percentage >= 70,
                    "completion_percentage": percentage
                })
    
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
    import random
    
    # Map goals by user
    goals_by_user = {}
    for goal in goals:
        if goal.user_id not in goals_by_user:
            goals_by_user[goal.user_id] = []
        goals_by_user[goal.user_id].append(goal)
    
    schedules_data = []
    
    # Create 1-2 schedules per user for first 10 users
    for user in users[:10]:
        user_goals = goals_by_user.get(user.id, [])
        goal = user_goals[0] if user_goals else None
        
        num_schedules = random.randint(1, 2)
        for sched_idx in range(num_schedules):
            # Determine schedule type based on goals or random
            if goal:
                if goal.goal_type == "exam_preparation":
                    sched_type = "exam_prep"
                    sched_name = f"{goal.goal_title} Preparation"
                elif goal.goal_type == "time_based":
                    sched_type = "time_based"
                    sched_name = f"{goal.goal_title} Schedule"
                else:
                    sched_type = random.choice(["goal_based", "custom"])
                    sched_name = f"{goal.goal_title} Practice"
            else:
                sched_type = random.choice(["time_based", "custom", "maintenance"])
                sched_name = random.choice([
                    "Daily Practice Routine",
                    "Weekly Study Plan",
                    "Learning Schedule",
                    "Study Routine"
                ])
            
            daily_minutes = user.daily_study_time or random.randint(20, 60)
            days_per_week = random.randint(3, 7)
            
            # Different activity distributions
            distributions = [
                {"flashcards": 0.4, "quizzes": 0.3, "reading": 0.3},
                {"flashcards": 0.5, "quizzes": 0.3, "reading": 0.2},
                {"flashcards": 0.6, "quizzes": 0.2, "reading": 0.2},
                {"flashcards": 0.3, "quizzes": 0.4, "reading": 0.3},
            ]
            
            preferred_times = random.choice([
                ["09:00-11:00"],
                ["18:00-20:00"],
                ["07:00-08:00", "19:00-21:00"],
                ["14:00-16:00"],
            ])
            
            focus_areas = random.sample(
                ["Grammar", "Vocabulary", "Reading", "Writing", "Speaking", "Business English", "IELTS", "TOEIC"],
                k=random.randint(2, 4)
            )
            
            total_days = random.randint(15, 45)
            days_completed = random.randint(int(total_days * 0.5), int(total_days * 0.9))
            days_missed = random.randint(0, total_days - days_completed)
            adherence = Decimal(f"{random.uniform(65, 95):.2f}")
            
            schedules_data.append({
                "user_id": user.id,
                "goal_id": goal.id if goal else None,
                "schedule_name": sched_name if sched_idx == 0 else f"{sched_name} {sched_idx + 1}",
                "schedule_type": sched_type,
            "schedule_config": {
                    "daily_minutes": daily_minutes,
                    "days_per_week": days_per_week,
                    "preferred_times": preferred_times,
                    "activity_distribution": random.choice(distributions),
                    "difficulty_curve": random.choice(["gradual", "adaptive", "steep"]),
                    "focus_areas": focus_areas
                },
                "adaptation_mode": random.choice(["strict", "moderate", "flexible", "highly_adaptive"]),
                "max_daily_load": daily_minutes + random.randint(10, 30),
                "min_daily_load": max(15, daily_minutes - random.randint(10, 20)),
                "catch_up_strategy": random.choice(["skip", "gradual", "intensive"]),
                "is_active": random.random() > 0.1,  # 90% active
                "total_days_scheduled": total_days,
                "days_completed": days_completed,
                "days_missed": days_missed,
                "days_partially_completed": random.randint(0, 5),
                "avg_adherence_rate": adherence
            })
    
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
    import random
    today = date.today()
    
    # Create plans for multiple users over the past 7 days and next 7 days
    user_schedules = {}
    for schedule in schedules:
        if schedule.user_id not in user_schedules:
            user_schedules[schedule.user_id] = []
        user_schedules[schedule.user_id].append(schedule)
    
    for user in users[:10]:  # Create plans for first 10 users
        user_scheds = user_schedules.get(user.id, [])
        schedule = user_scheds[0] if user_scheds else None
        
        # Create plans for past 7 days and next 7 days
        for day_offset in range(-7, 8):  # -7 to +7 days
            plan_date = today + timedelta(days=day_offset)
            is_today = (day_offset == 0)
            is_past = (day_offset < 0)
            
            # Decide if plan should be completed (higher chance for past days)
            is_completed = is_past and random.random() > 0.3  # 70% completion for past days
            
            # Create 2-3 tasks
            num_tasks = random.randint(2, 3)
            tasks = []
            total_minutes = 0
            
            for task_idx in range(num_tasks):
                task_type = random.choice(["flashcard_review", "quiz", "reading"])
                
                if task_type == "flashcard_review":
                    count = random.randint(10, 25)
                    minutes = random.randint(8, 15)
                    tasks.append({
                    "type": "flashcard_review",
                        "entity_ids": list(range(1, count + 1)),
                        "count": count,
                        "estimated_minutes": minutes,
                        "priority": random.choice(["high", "medium"]),
                    "reason": "Due for review (SRS)",
                        "topic": random.choice(["Grammar", "Vocabulary", "Business English"])
                    })
                    total_minutes += minutes
                
                elif task_type == "quiz":
                    minutes = random.randint(10, 20)
                    tasks.append({
                    "type": "quiz",
                        "entity_id": random.randint(1, 5),
                        "quiz_title": random.choice(["Business Vocabulary", "IELTS Practice", "Grammar Quiz"]),
                        "estimated_minutes": minutes,
                        "priority": random.choice(["medium", "high"]),
                        "reason": random.choice(["Weak topic", "Regular practice", "Exam preparation"])
                    })
                    total_minutes += minutes
                
                else:  # reading
                    minutes = random.randint(15, 30)
                    tasks.append({
                        "type": "reading",
                        "entity_id": random.randint(1, 20),
                        "estimated_minutes": minutes,
                    "priority": "medium",
                        "reason": "Improve reading comprehension"
                    })
                    total_minutes += minutes
            
            # Completion status
            if is_completed:
                completed_tasks = num_tasks if random.random() > 0.2 else num_tasks - 1  # 80% full completion
                actual_minutes = random.randint(int(total_minutes * 0.7), total_minutes)
                completion_pct = Decimal(f"{(completed_tasks / num_tasks) * 100:.2f}")
                status = "completed" if completed_tasks == num_tasks else "partially_completed"
                
                # Create performance data
                actual_performance = {
                    "flashcards": {
                        "reviewed": random.randint(10, 25),
                        "correct": random.randint(8, 23),
                        "accuracy": round(random.uniform(0.70, 0.90), 2)
                    } if any(t["type"] == "flashcard_review" for t in tasks) else None,
                    "quizzes": {
                        "completed": 1 if any(t["type"] == "quiz" for t in tasks) else 0,
                        "score": random.randint(70, 95)
                    } if any(t["type"] == "quiz" for t in tasks) else None,
                    "overall_accuracy": random.randint(75, 90)
                }
                
                started_at = datetime.utcnow() - timedelta(days=abs(day_offset), hours=random.randint(1, 12))
                completed_at = started_at + timedelta(minutes=actual_minutes)
            else:
                completed_tasks = 0
                actual_minutes = 0
                completion_pct = Decimal("0.00")
                status = "pending"
                actual_performance = None
                started_at = None
                completed_at = None
            
            plan_summary = f"Day {abs(day_offset)+1}: " + ", ".join([t["type"].replace("_", " ") for t in tasks])
            
            plan = DailyStudyPlan(
                user_id=user.id,
                schedule_id=schedule.id if schedule else None,
                plan_date=plan_date,
                plan_summary=plan_summary,
                recommended_tasks=tasks,
                total_estimated_minutes=total_minutes,
                actual_minutes_spent=actual_minutes,
                priority_level=random.choice(["low", "normal", "high"]),
                difficulty_level=random.choice(["easy", "medium", "hard"]),
                is_completed=is_completed,
                completion_percentage=completion_pct,
                completed_tasks_count=completed_tasks,
                total_tasks_count=num_tasks,
                status=status,
                actual_performance=actual_performance,
                started_at=started_at,
                completed_at=completed_at
        )
        db.add(plan)
    
    db.commit()


def create_sample_study_sessions(db: Session, users: list[User], daily_plans: list[DailyStudyPlan]):
    """Create sample study sessions"""
    import random
    
    # Get plans by date
    plans_by_date = {}
    for plan in daily_plans:
        if plan.plan_date not in plans_by_date:
            plans_by_date[plan.plan_date] = []
        plans_by_date[plan.plan_date].append(plan)
    
    sessions_data = []
    
    # Create sessions for the past 14 days for multiple users
    today = date.today()
    for day_offset in range(14):  # Past 14 days
        session_date = today - timedelta(days=day_offset)
        day_plans = plans_by_date.get(session_date, [])
        
        # Create 1-3 sessions per day for random users
        num_sessions = random.randint(1, 3)
        for _ in range(num_sessions):
            user = random.choice(users)
            plan = random.choice(day_plans) if day_plans else None
            
            # Random session type
            session_type = random.choice(["flashcard_review", "quiz_taking", "document_reading", "vocabulary_practice"])
            
            # Random time of day
            time_of_day = random.choice(["morning", "afternoon", "evening", "night"])
            
            # Random duration (5-45 minutes)
            duration_minutes = random.randint(5, 45)
            duration_seconds = duration_minutes * 60
            
            # Random start time within the day
            hours_ago = random.randint(1, 23) if day_offset == 0 else (day_offset * 24 + random.randint(1, 23))
            started_at = datetime.utcnow() - timedelta(hours=hours_ago)
            ended_at = started_at + timedelta(seconds=duration_seconds)
            
            if session_type == "flashcard_review":
                cards_reviewed = random.randint(10, 30)
                accuracy = random.uniform(0.65, 0.95)
                correct = int(cards_reviewed * accuracy)
                
                sessions_data.append({
                    "user_id": user.id,
                    "daily_plan_id": plan.id if plan else None,
            "session_type": "flashcard_review",
            "entity_type": "flashcard",
                    "entity_id": random.randint(1, 100),
                    "duration_seconds": duration_seconds,
                    "started_at": started_at,
                    "ended_at": ended_at,
            "performance_data": {
                        "cards_reviewed": cards_reviewed,
                        "correct": correct,
                        "incorrect": cards_reviewed - correct,
                        "accuracy": round(accuracy, 2)
                    },
                    "accuracy_rate": Decimal(f"{accuracy * 100:.2f}"),
                    "items_completed": cards_reviewed,
                    "items_correct": correct,
                    "device_type": random.choice(["desktop", "mobile", "tablet"]),
                    "time_of_day": time_of_day,
                    "is_planned": plan is not None,
                    "primary_topic": random.choice(["Vocabulary", "Grammar", "Business English", "IELTS"]),
                    "difficulty_attempted": random.choice(["easy", "medium", "hard"]),
                })
            
            elif session_type == "quiz_taking":
                questions = random.randint(5, 15)
                accuracy = random.uniform(0.70, 0.95)
                correct = int(questions * accuracy)
                
                sessions_data.append({
                    "user_id": user.id,
                    "daily_plan_id": plan.id if plan else None,
            "session_type": "quiz_taking",
            "entity_type": "quiz",
                    "entity_id": random.randint(1, 10),
                    "duration_seconds": duration_seconds,
                    "started_at": started_at,
                    "ended_at": ended_at,
            "performance_data": {
                        "quiz_id": random.randint(1, 10),
                        "score": correct * 10,
                        "max_score": questions * 10,
                        "questions_answered": questions
                    },
                    "accuracy_rate": Decimal(f"{accuracy * 100:.2f}"),
                    "items_completed": questions,
                    "items_correct": correct,
                    "device_type": random.choice(["desktop", "mobile"]),
                    "time_of_day": time_of_day,
                    "is_planned": plan is not None,
                    "primary_topic": random.choice(["Vocabulary", "Reading", "Business English"]),
                    "difficulty_attempted": random.choice(["easy", "medium", "hard"]),
                })
            
            else:  # document_reading or vocabulary_practice
                items = random.randint(5, 20)
                accuracy = random.uniform(0.75, 0.95) if session_type == "vocabulary_practice" else None
                
                sessions_data.append({
                    "user_id": user.id,
                    "daily_plan_id": plan.id if plan else None,
                    "session_type": session_type,
                    "entity_type": "document" if session_type == "document_reading" else "vocabulary",
                    "entity_id": random.randint(1, 20),
                    "duration_seconds": duration_seconds,
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "performance_data": {
                        "items_read": items,
                        "words_learned": random.randint(0, 5) if session_type == "document_reading" else None,
                    },
                    "accuracy_rate": Decimal(f"{accuracy * 100:.2f}") if accuracy else None,
                    "items_completed": items,
                    "items_correct": int(items * accuracy) if accuracy else None,
                    "device_type": random.choice(["desktop", "mobile", "tablet"]),
                    "time_of_day": time_of_day,
                    "is_planned": plan is not None,
                    "primary_topic": random.choice(["Reading", "Vocabulary", "General"]),
                    "difficulty_attempted": random.choice(["easy", "medium", "hard"]),
                })
    
    for session_data in sessions_data:
        session = StudySession(**session_data)
        db.add(session)
    
    db.commit()


def create_sample_quizzes(db: Session, users: list[User], documents: list[Document]):
    """Create sample quizzes and questions"""
    import random
    
    quizzes_data = [
        # Business English Quiz
        {
            "title": "Business English Vocabulary Quiz",
            "description": "Test your knowledge of essential business English terms",
            "quiz_type": "vocabulary",
            "difficulty_level": "medium",
            "time_limit": 15,
            "document_id": documents[0].id if len(documents) > 0 else None,
            "created_by": users[2].id if len(users) > 2 else users[0].id,
            "questions": [
        {
            "question_text": "What does ROI stand for?",
            "question_type": "multiple_choice",
            "options": ["Return on Investment", "Rate of Interest", "Revenue of Income", "Risk of Investment"],
            "correct_answer": "Return on Investment",
            "explanation": "ROI (Return on Investment) measures the efficiency of an investment.",
            "difficulty_level": "medium",
            "points": 2,
        },
        {
            "question_text": "A _______ is someone who has an interest in a business or project.",
            "question_type": "fill_blank",
            "correct_answer": "stakeholder",
            "blank_position": 2,
            "explanation": "A stakeholder is a person with an interest or concern in something, especially a business.",
            "difficulty_level": "medium",
            "points": 1,
                },
                {
                    "question_text": "What does KPI stand for?",
                    "question_type": "multiple_choice",
                    "options": ["Key Performance Indicator", "Key Process Improvement", "Key Personal Initiative", "Key Profit Index"],
                    "correct_answer": "Key Performance Indicator",
                    "explanation": "KPI stands for Key Performance Indicator, a measurable value showing how effectively objectives are achieved.",
                    "difficulty_level": "medium",
                    "points": 2,
                },
                {
                    "question_text": "A _______ is the latest time or date by which something should be completed.",
                    "question_type": "fill_blank",
                    "correct_answer": "deadline",
                    "blank_position": 2,
                    "explanation": "A deadline is the latest time or date by which something should be completed.",
                    "difficulty_level": "easy",
                    "points": 1,
                },
            ]
        },
        # IELTS Reading Quiz
        {
            "title": "IELTS Academic Vocabulary Quiz",
            "description": "Test your knowledge of academic English vocabulary",
            "quiz_type": "vocabulary",
            "difficulty_level": "hard",
            "time_limit": 20,
            "document_id": documents[2].id if len(documents) > 2 else None,
            "created_by": users[2].id if len(users) > 2 else users[0].id,
            "questions": [
                {
                    "question_text": "What does 'biodiversity' mean?",
                    "question_type": "multiple_choice",
                    "options": [
                        "The variety of plant and animal life",
                        "The study of biology",
                        "A type of ecosystem",
                        "Environmental pollution"
                    ],
                    "correct_answer": "The variety of plant and animal life",
                    "explanation": "Biodiversity refers to the variety of plant and animal life in the world or in a particular habitat.",
                    "difficulty_level": "hard",
                    "points": 3,
                },
                {
                    "question_text": "Something that can be maintained at a certain rate is called _______.",
                    "question_type": "fill_blank",
                    "correct_answer": "sustainable",
                    "blank_position": 6,
                    "explanation": "Sustainable means able to be maintained at a certain rate or level.",
                    "difficulty_level": "hard",
                    "points": 2,
                },
                {
                    "question_text": "What does 'innovative' mean?",
                    "question_type": "multiple_choice",
                    "options": [
                        "Featuring new methods; advanced and original",
                        "Very expensive",
                        "Old-fashioned",
                        "Complicated"
                    ],
                    "correct_answer": "Featuring new methods; advanced and original",
                    "explanation": "Innovative means featuring new methods; advanced and original.",
                    "difficulty_level": "hard",
                    "points": 2,
                },
            ]
        },
        # TOEIC Quiz
        {
            "title": "TOEIC Business Vocabulary Quiz",
            "description": "Practice TOEIC business vocabulary",
            "quiz_type": "vocabulary",
            "difficulty_level": "medium",
            "time_limit": 15,
            "document_id": documents[3].id if len(documents) > 3 else None,
            "created_by": users[2].id if len(users) > 2 else users[0].id,
            "questions": [
                {
                    "question_text": "To travel regularly between home and work is called _______.",
                    "question_type": "fill_blank",
                    "correct_answer": "commute",
                    "blank_position": 5,
                    "explanation": "Commute means to travel regularly between one's home and place of work.",
                    "difficulty_level": "medium",
                    "points": 2,
                },
                {
                    "question_text": "A written list of goods sent or services provided is called an _______.",
                    "question_type": "fill_blank",
                    "correct_answer": "invoice",
                    "blank_position": 8,
                    "explanation": "An invoice is a list of goods sent or services provided, with a statement of the sum due.",
                    "difficulty_level": "medium",
                    "points": 2,
                },
                {
                    "question_text": "A company controlled by a holding company is called a _______.",
                    "question_type": "fill_blank",
                    "correct_answer": "subsidiary",
                    "blank_position": 6,
                    "explanation": "A subsidiary is a company controlled by a holding company.",
                    "difficulty_level": "medium",
                    "points": 2,
                },
            ]
        },
        # General English Quiz
        {
            "title": "Everyday English Phrases Quiz",
            "description": "Test your knowledge of everyday English phrases",
            "quiz_type": "vocabulary",
            "difficulty_level": "easy",
            "time_limit": 10,
            "document_id": documents[1].id if len(documents) > 1 else None,
            "created_by": users[2].id if len(users) > 2 else users[0].id,
            "questions": [
                {
                    "question_text": "What does 'I'd like to' mean?",
                    "question_type": "multiple_choice",
                    "options": [
                        "Used to politely express a wish or preference",
                        "I don't want to",
                        "I need to",
                        "I have to"
                    ],
                    "correct_answer": "Used to politely express a wish or preference",
                    "explanation": "'I'd like to' is used to politely express a wish or preference.",
                    "difficulty_level": "easy",
                    "points": 1,
                },
                {
                    "question_text": "A casual way to say goodbye is _______.",
                    "question_type": "fill_blank",
                    "correct_answer": "See you later",
                    "blank_position": 4,
                    "explanation": "'See you later' is a casual way to say goodbye.",
                    "difficulty_level": "easy",
                    "points": 1,
                },
            ]
        },
    ]
    
    all_quizzes = []
    
    for quiz_data in quizzes_data:
        questions_data = quiz_data.pop("questions")
        
        quiz = Quiz(**quiz_data)
        db.add(quiz)
        db.flush()
        
        # Add questions
        for idx, q_data in enumerate(questions_data, 1):
            q_data["order_index"] = idx
            q_data["quiz_id"] = quiz.id
        question = QuizQuestion(**q_data)
        db.add(question)
    
        all_quizzes.append(quiz)
    
    db.commit()
    
    # Refresh quizzes to get IDs
    for quiz in all_quizzes:
        db.refresh(quiz)
    
    # Create quiz attempts for various users
    for quiz in all_quizzes:
        # Get questions for this quiz
        questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
        
        # Create 2-4 attempts per quiz from different users
        num_attempts = random.randint(2, 4)
        for _ in range(num_attempts):
            user = random.choice(users)
            max_score = sum(q.points for q in questions)
            score = random.randint(int(max_score * 0.6), max_score)
            percentage = int((score / max_score) * 100)
            
            # Generate answers (some correct, some wrong)
            answers = {}
            for q in questions:
                if random.random() > 0.2:  # 80% chance of correct answer
                    answers[str(q.id)] = q.correct_answer
                else:
                    if q.question_type == "multiple_choice" and q.options:
                        wrong_answers = [opt for opt in q.options if opt != q.correct_answer]
                        answers[str(q.id)] = random.choice(wrong_answers) if wrong_answers else q.correct_answer
                    else:
                        answers[str(q.id)] = q.correct_answer
            
            attempt = QuizAttempt(
                answers=answers,
                score=score,
                max_score=max_score,
                percentage=percentage,
                time_taken=random.randint(180, 600),  # 3-10 minutes
        is_completed=True,
                completed_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                user_id=user.id,
                quiz_id=quiz.id
            )
            db.add(attempt)
    
    db.commit()

def seed_database(force=False):
    """Main seeding function"""
    print("Starting database seeding...")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if not force:
            try:
                if db.query(User).count() > 0:
                    print("Database already contains data. Skipping seed.")
                    print("Use --force flag to force seed anyway (will create duplicate data).")
                    return
            except Exception:
                # Table doesn't exist yet or other error - rollback and continue with seeding
                db.rollback()
                pass
        else:
            print("Force mode: Clearing existing data...")
            # Delete in reverse dependency order (skip if tables don't exist)
            try:
                # Check if users table exists first
                from sqlalchemy import inspect
                inspector = inspect(db.bind)
                tables = inspector.get_table_names()
                
                if "users" in tables:
                    # Tables exist, proceed with deletion
                    if "quiz_attempts" in tables:
                        db.query(QuizAttempt).delete()
                    if "quiz_questions" in tables:
                        db.query(QuizQuestion).delete()
                    if "quizzes" in tables:
                        db.query(Quiz).delete()
                    if "flashcards" in tables:
                        db.query(Flashcard).delete()
                    if "study_sessions" in tables:
                        db.query(StudySession).delete()
                    if "learning_analytics" in tables:
                        db.query(LearningAnalytics).delete()
                    if "adaptive_recommendations" in tables:
                        db.query(AdaptiveRecommendation).delete()
                    if "daily_study_plans" in tables:
                        db.query(DailyStudyPlan).delete()
                    if "study_schedules" in tables:
                        db.query(StudySchedule).delete()
                    if "learning_goals" in tables:
                        db.query(LearningGoal).delete()
                    if "learning_profiles" in tables:
                        db.query(LearningProfile).delete()
                    if "documents" in tables:
                        db.query(Document).delete()
                    if "users" in tables:
                        db.query(User).delete()
                    db.commit()
                    print("Existing data cleared.")
                else:
                    print("Tables don't exist yet, skipping data deletion.")
            except Exception as e:
                print(f"Warning: Could not clear existing data: {e}")
                db.rollback()
                # Continue anyway - tables might not exist yet

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

        print("\nLogin credentials (all users use 'password123' except admin):")
        for user in users:
            if user.is_superuser:
                print(f"  {user.email} / admin123 (Admin)")
            else:
                print(f"  {user.email} / password123")

    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed database with sample data')
    parser.add_argument('--force', action='store_true', 
                       help='Force seed even if data already exists (will create duplicates)')
    
    args = parser.parse_args()
    seed_database(force=args.force)
