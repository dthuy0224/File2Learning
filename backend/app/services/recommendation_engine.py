from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
from collections import Counter

from app.models.recommendation import RecommendationType, RecommendationPriority
from app.models.flashcard import Flashcard
from app.models.quiz import QuizAttempt
from app.models.document import Document
from app.models.learning_goal import LearningGoal
from app.models.study_session import StudySession, LearningAnalytics
from app.schemas.recommendation import RecommendationCreate
from app.crud.crud_recommendation import crud_recommendation


class RecommendationEngine:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def generate_recommendations(self, max_recommendations: int = 10) -> List[RecommendationCreate]:
        recommendations = []
        
        # 1. Check for due flashcards (high priority)
        flashcard_recs = self._recommend_flashcard_review()
        recommendations.extend(flashcard_recs[:3])  # Max 3 flashcard recommendations
        
        # 2. Identify weak topics that need attention (high priority)
        weak_topic_recs = self._recommend_weak_topics()
        recommendations.extend(weak_topic_recs[:2])  # Max 2 weak topic recommendations
        
        # 3. Suggest quizzes for practice (medium priority)
        quiz_recs = self._recommend_quizzes()
        recommendations.extend(quiz_recs[:2])  # Max 2 quiz recommendations
        
        # 4. Suggest documents to read (low-medium priority)
        document_recs = self._recommend_documents()
        recommendations.extend(document_recs[:2])  # Max 2 document recommendations
        
        # 5. Progress towards learning goals (medium priority)
        goal_recs = self._recommend_for_goals()
        recommendations.extend(goal_recs[:2])  # Max 2 goal recommendations
        
        # 6. Reinforce strengths (low priority)
        strength_recs = self._recommend_reinforcement()
        recommendations.extend(strength_recs[:1])  # Max 1 reinforcement recommendation
        
        # Sort by priority and relevance, limit to max_recommendations
        recommendations = sorted(
            recommendations,
            key=lambda r: (
                self._priority_score(r.priority),
                r.relevance_score,
                r.confidence_score
            ),
            reverse=True
        )[:max_recommendations]
        
        return recommendations
    
    def _priority_score(self, priority: RecommendationPriority) -> int:
        """Convert priority to numeric score for sorting"""
        priority_map = {
            RecommendationPriority.URGENT: 4,
            RecommendationPriority.HIGH: 3,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 1
        }
        return priority_map.get(priority, 1)
    
    def _recommend_flashcard_review(self) -> List[RecommendationCreate]:
        """Recommend flashcard sets that are due for review"""
        recommendations = []
        
        # Get flashcards due for review
        due_flashcards = self.db.query(Flashcard).filter(
            Flashcard.owner_id == self.user_id,
            Flashcard.next_review_date <= datetime.utcnow()
        ).order_by(Flashcard.next_review_date).all()
        
        if not due_flashcards:
            return recommendations
        
        # Group by topic/tag
        topic_counts = Counter()
        for card in due_flashcards:
            # Tags is a comma-separated string, need to split it
            tags_str = card.tags or ""
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            
            if not tags:
                # If no tags, use a default topic
                tags = ["General"]
            
            for tag in tags:
                topic_counts[tag] += 1
        
        # Create recommendations for top topics
        for topic, count in topic_counts.most_common(3):
            priority = RecommendationPriority.URGENT if count >= 10 else RecommendationPriority.HIGH
            
            recommendations.append(RecommendationCreate(
                type=RecommendationType.REVIEW_FLASHCARD,
                priority=priority,
                title=f"Review {count} flashcards on {topic}",
                description=f"You have {count} flashcards about '{topic}' that are due for review. Regular review helps maintain long-term memory.",
                reason=f"Spaced repetition algorithm indicates these cards need review to maintain retention.",
                target_resource_type="topic",
                target_resource_id=None,
                relevance_score=min(count / 20.0, 1.0),  # More cards = more relevant
                confidence_score=0.95,
                expected_impact=0.8,
                extra_data={"topic": topic, "card_count": count},
                expires_at=datetime.utcnow() + timedelta(days=1)
            ))
        
        return recommendations
    
    def _recommend_weak_topics(self) -> List[RecommendationCreate]:
        """Identify weak topics based on quiz performance and analytics"""
        recommendations = []
        
        # Get recent quiz attempts (last 30 days)
        recent_attempts = self.db.query(QuizAttempt).filter(
            QuizAttempt.user_id == self.user_id,
            QuizAttempt.started_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if not recent_attempts:
            return recommendations
        
        # Analyze performance by topic
        topic_performance = {}
        for attempt in recent_attempts:
            if not attempt.quiz:
                continue
            
            topic = attempt.quiz.quiz_type or "General"
            score_pct = (attempt.score / attempt.max_score * 100) if attempt.max_score > 0 else 0
            
            if topic not in topic_performance:
                topic_performance[topic] = []
            topic_performance[topic].append(score_pct)
        
        # Find topics with consistently low scores
        weak_topics = []
        for topic, scores in topic_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 70 and len(scores) >= 2:  # Below 70% average, at least 2 attempts
                weak_topics.append((topic, avg_score, len(scores)))
        
        # Sort by lowest score
        weak_topics.sort(key=lambda x: x[1])
        
        for topic, avg_score, attempt_count in weak_topics[:2]:
            recommendations.append(RecommendationCreate(
                type=RecommendationType.FOCUS_WEAK_AREA,
                priority=RecommendationPriority.HIGH,
                title=f"Strengthen your understanding of {topic}",
                description=f"Your recent performance in '{topic}' shows room for improvement (average: {avg_score:.0f}%). Focus on this area to boost your overall mastery.",
                reason=f"Based on {attempt_count} recent quiz attempts, your average score in this topic is {avg_score:.0f}%, which is below the target threshold of 70%.",
                target_resource_type="topic",
                target_resource_id=None,
                relevance_score=0.9,
                confidence_score=0.85,
                expected_impact=0.9,
                extra_data={"topic": topic, "avg_score": round(avg_score, 2), "attempt_count": attempt_count},
                expires_at=datetime.utcnow() + timedelta(days=7)
            ))
        
        return recommendations
    
    def _recommend_quizzes(self) -> List[RecommendationCreate]:
        """Recommend quizzes based on learning patterns"""
        recommendations = []
        
        # Get topics from recent study sessions
        recent_sessions = self.db.query(StudySession).filter(
            StudySession.user_id == self.user_id,
            StudySession.started_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        studied_topics = set()
        for session in recent_sessions:
            if session.primary_topic:
                studied_topics.add(session.primary_topic)
        
        if not studied_topics:
            # Fallback: recommend any available quiz
            recommendations.append(RecommendationCreate(
                type=RecommendationType.TAKE_QUIZ,
                priority=RecommendationPriority.MEDIUM,
                title="Test your knowledge with a quiz",
                description="Taking quizzes regularly helps reinforce learning and identify areas for improvement.",
                reason="It's been a while since your last quiz. Regular testing improves retention.",
                target_resource_type="quiz",
                target_resource_id=None,
                relevance_score=0.6,
                confidence_score=0.7,
                expected_impact=0.75,
                extra_data={},
                expires_at=datetime.utcnow() + timedelta(days=3)
            ))
        else:
            # Recommend quizzes on recently studied topics
            for topic in list(studied_topics)[:2]:
                recommendations.append(RecommendationCreate(
                    type=RecommendationType.TAKE_QUIZ,
                    priority=RecommendationPriority.MEDIUM,
                    title=f"Test yourself on {topic}",
                    description=f"You've been studying '{topic}' recently. Take a quiz to reinforce your understanding and measure progress.",
                    reason=f"Recent study activity detected in '{topic}'. Testing helps consolidate learning.",
                    target_resource_type="topic",
                    target_resource_id=None,
                    relevance_score=0.75,
                    confidence_score=0.8,
                    expected_impact=0.8,
                    extra_data={"topic": topic},
                    expires_at=datetime.utcnow() + timedelta(days=5)
                ))
        
        return recommendations
    
    def _recommend_documents(self) -> List[RecommendationCreate]:
        """Recommend documents to read based on learning goals and weak areas"""
        recommendations = []
        
        # Get user's documents
        documents = self.db.query(Document).filter(
            Document.owner_id == self.user_id
        ).order_by(desc(Document.created_at)).limit(10).all()
        
        if not documents:
            return recommendations
        
        # Get topics from weak areas
        weak_topics = self._get_weak_topics()
        
        # Recommend documents for weak topics
        for doc in documents[:2]:
            doc_type = doc.document_type or "document"
            doc_title = doc.title or doc.original_filename
            recommendations.append(RecommendationCreate(
                type=RecommendationType.READ_DOCUMENT,
                priority=RecommendationPriority.LOW,
                title=f"Review: {doc_title}",
                description=f"Revisit this {doc_type} to strengthen your understanding of key concepts.",
                reason="Regular review of learning materials helps with long-term retention.",
                target_resource_type="document",
                target_resource_id=doc.id,
                relevance_score=0.65,
                confidence_score=0.7,
                expected_impact=0.7,
                extra_data={"document_id": doc.id, "document_title": doc_title},
                expires_at=datetime.utcnow() + timedelta(days=14)
            ))
        
        return recommendations
    
    def _recommend_for_goals(self) -> List[RecommendationCreate]:
        """Generate recommendations to help achieve learning goals"""
        recommendations = []
        
        # Get active learning goals
        active_goals = self.db.query(LearningGoal).filter(
            LearningGoal.user_id == self.user_id,
            LearningGoal.status == "active"
        ).all()
        
        for goal in active_goals[:2]:
            today = date.today()
            if goal.target_date and goal.target_date < today:
                # Goal is overdue
                priority = RecommendationPriority.HIGH
                title_prefix = "Urgent:"
            else:
                priority = RecommendationPriority.MEDIUM
                title_prefix = "Continue working on"
            
            # Extract progress percentage from current_progress JSON
            progress_pct = 0.0
            if goal.current_progress and isinstance(goal.current_progress, dict):
                progress_pct = float(goal.current_progress.get('percentage', 0))
            
            # Convert date to datetime for expires_at
            expires_at = datetime.combine(goal.target_date, datetime.min.time()) if goal.target_date else datetime.utcnow() + timedelta(days=7)
            
            recommendations.append(RecommendationCreate(
                type=RecommendationType.STUDY_TOPIC,
                priority=priority,
                title=f"{title_prefix} {goal.goal_title}",
                description=f"You're {progress_pct:.0f}% towards your goal. Keep up the momentum!",
                reason=f"This learning goal is part of your active objectives. Current progress: {progress_pct:.0f}%.",
                target_resource_type="learning_goal",
                target_resource_id=goal.id,
                relevance_score=0.85,
                confidence_score=0.9,
                expected_impact=0.85,
                extra_data={"goal_id": goal.id, "progress": progress_pct},
                expires_at=expires_at
            ))
        
        return recommendations
    
    def _recommend_reinforcement(self) -> List[RecommendationCreate]:
        """Recommend activities to reinforce strong areas"""
        recommendations = []
        
        # Get learning analytics
        analytics = self.db.query(LearningAnalytics).filter(
            LearningAnalytics.user_id == self.user_id
        ).order_by(desc(LearningAnalytics.analytics_date)).first()
        
        if not analytics:
            return recommendations
        
        # If user is doing well overall, encourage continued practice
        overall_score = float(analytics.overall_accuracy) if analytics.overall_accuracy else 0
        if overall_score >= 85:
            recommendations.append(RecommendationCreate(
                type=RecommendationType.REINFORCE_STRENGTH,
                priority=RecommendationPriority.LOW,
                title="Great progress! Keep the momentum going",
                description=f"Your average performance is excellent ({overall_score:.0f}%). Continue practicing to maintain this level of mastery.",
                reason="Strong performance detected across multiple areas. Consistent practice maintains excellence.",
                target_resource_type=None,
                target_resource_id=None,
                relevance_score=0.7,
                confidence_score=0.75,
                expected_impact=0.65,
                extra_data={"overall_accuracy": overall_score},
                expires_at=datetime.utcnow() + timedelta(days=5)
            ))
        
        return recommendations
    
    def _get_weak_topics(self) -> List[str]:
        """Helper: Get list of topics where user is weak"""
        recent_attempts = self.db.query(QuizAttempt).filter(
            QuizAttempt.user_id == self.user_id,
            QuizAttempt.started_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        topic_performance = {}
        for attempt in recent_attempts:
            if not attempt.quiz:
                continue
            
            topic = attempt.quiz.quiz_type or "General"
            score_pct = (attempt.score / attempt.max_score * 100) if attempt.max_score > 0 else 0
            
            if topic not in topic_performance:
                topic_performance[topic] = []
            topic_performance[topic].append(score_pct)
        
        weak_topics = []
        for topic, scores in topic_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 70:
                weak_topics.append(topic)
        
        return weak_topics


def generate_recommendations_for_user(db: Session, user_id: int, max_recommendations: int = 10) -> int:
    """
    Main entry point to generate and save recommendations for a user
    Returns the number of recommendations created
    """
    # Clear old active recommendations (optional, but prevents clutter)
    crud_recommendation.delete_expired(db, user_id=user_id)
    
    # Generate new recommendations
    engine = RecommendationEngine(db, user_id)
    recommendations = engine.generate_recommendations(max_recommendations=max_recommendations)
    
    # Save to database
    count = 0
    for rec in recommendations:
        try:
            crud_recommendation.create(db, recommendation=rec, user_id=user_id)
            count += 1
        except Exception as e:
            print(f"Error saving recommendation: {e}")
            continue
    
    return count

