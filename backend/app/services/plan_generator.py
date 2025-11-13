
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizAttempt
from app.models.learning_goal import LearningGoal
from app.models.learning_profile import LearningProfile
from app.schemas.daily_plan import RecommendedTask, DailyStudyPlanCreate
import logging

logger = logging.getLogger(__name__)


class DailyPlanGenerator:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.profile = self._get_or_create_profile()
        
    def _get_or_create_profile(self) -> LearningProfile:
        """Get user's learning profile or create default"""
        profile = self.db.query(LearningProfile).filter(
            LearningProfile.user_id == self.user_id
        ).first()
        
        if not profile:
            # Create default profile
            profile = LearningProfile(
                user_id=self.user_id,
                learning_style='balanced',
                preferred_difficulty='medium',
                recommended_daily_load=30  # 30 minutes default
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        
        return profile
    
    def generate_plan(self, plan_date: date = None) -> DailyStudyPlanCreate:
        if not plan_date:
            plan_date = date.today()
        
        logger.info(f"Generating plan for user {self.user_id} on {plan_date}")
        
        # Step 1: Get due flashcards (HIGHEST PRIORITY)
        due_flashcards = self._get_due_flashcards(plan_date)
        
        # Step 2: Identify weak topics
        weak_topics = self._identify_weak_topics()
        
        # Step 3: Get active goals
        active_goals = self._get_active_goals()
        
        # Step 4: Calculate time budget
        time_budget = int(self.profile.recommended_daily_load)
        
        # Step 5: Generate tasks
        tasks = self._generate_tasks(
            due_flashcards=due_flashcards,
            weak_topics=weak_topics,
            active_goals=active_goals,
            time_budget=time_budget
        )
        
        # Step 6: Generate summary
        summary = self._generate_summary(tasks, due_flashcards, weak_topics)
        
        # Step 7: Determine priority & difficulty
        priority = self._calculate_priority(due_flashcards, active_goals)
        difficulty = self._calculate_difficulty(tasks)
        
        return DailyStudyPlanCreate(
            plan_date=plan_date,
            plan_summary=summary,
            recommended_tasks=tasks,
            total_estimated_minutes=sum(t.estimated_minutes for t in tasks),
            priority_level=priority,
            difficulty_level=difficulty
        )
    
    def _get_due_flashcards(self, plan_date: date) -> List[Flashcard]:
        """Get flashcards due for review (SRS)"""
        return self.db.query(Flashcard).filter(
            and_(
                Flashcard.owner_id == self.user_id,
                Flashcard.next_review_date <= plan_date
            )
        ).order_by(Flashcard.next_review_date.asc()).limit(50).all()  # Max 50 per day
    
    def _identify_weak_topics(self, days_back: int = 14) -> List[Dict[str, Any]]:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get recent quiz attempts
        recent_attempts = self.db.query(QuizAttempt).join(Quiz).filter(
            and_(
                QuizAttempt.user_id == self.user_id,
                QuizAttempt.completed_at >= cutoff_date
            )
        ).all()
        
        if not recent_attempts:
            return []
        
        # Group by quiz_type and calculate average scores
        topic_scores = {}
        for attempt in recent_attempts:
            quiz = attempt.quiz
            topic = quiz.quiz_type  # Using quiz_type as topic proxy
            
            if topic not in topic_scores:
                topic_scores[topic] = []
            
            topic_scores[topic].append(attempt.score)
        
        # Identify weak topics (avg score < 70%)
        weak_topics = []
        for topic, scores in topic_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 70:
                weak_topics.append({
                    "topic": topic,
                    "avg_score": avg_score,
                    "attempts": len(scores),
                    "priority": "high" if avg_score < 50 else "medium"
                })
        
        # Sort by score (lowest first)
        weak_topics.sort(key=lambda x: x["avg_score"])
        
        return weak_topics[:3]  # Top 3 weak topics
    
    def _get_active_goals(self) -> List[LearningGoal]:
        """Get user's active learning goals"""
        return self.db.query(LearningGoal).filter(
            and_(
                LearningGoal.user_id == self.user_id,
                LearningGoal.status == 'active'
            )
        ).order_by(LearningGoal.priority.desc()).all()
    
    def _generate_tasks(
        self,
        due_flashcards: List[Flashcard],
        weak_topics: List[Dict],
        active_goals: List[LearningGoal],
        time_budget: int
    ) -> List[RecommendedTask]:
        """
        Generate balanced task list
        
        Task Distribution Strategy:
        - 40% SRS (flashcard review) - CRITICAL
        - 30% Weak topics (quizzes)
        - 30% Goal progress (new material/practice)
        """
        tasks = []
        time_used = 0
        
        # Task 1: Flashcard Review (Priority 1)
        if due_flashcards and time_used < time_budget:
            num_cards = min(len(due_flashcards), 20)  # Max 20 cards per session
            flashcard_time = num_cards * 0.5  # ~30 seconds per card
            flashcard_time = int(min(flashcard_time, time_budget * 0.4))  # Max 40% of budget
            
            if flashcard_time >= 5:  # Minimum 5 minutes
                tasks.append(RecommendedTask(
                    type="flashcard_review",
                    entity_ids=[fc.id for fc in due_flashcards[:num_cards]],
                    count=num_cards,
                    estimated_minutes=flashcard_time,
                    priority="high",
                    reason=f"Due for review (SRS) - {num_cards} cards ready",
                    topic="Mixed"
                ))
                time_used += flashcard_time
        
        # Task 2: Weak Topic Practice (Priority 2)
        if weak_topics and time_used < time_budget:
            for weak_topic in weak_topics[:2]:  # Max 2 weak topics per day
                if time_used >= time_budget * 0.7:  # Stop at 70% budget
                    break
                
                # Find quiz for this topic
                quiz = self.db.query(Quiz).filter(
                    Quiz.quiz_type == weak_topic["topic"]
                ).first()
                
                if quiz:
                    quiz_time = 15  # 15 minutes per quiz
                    if time_used + quiz_time <= time_budget:
                        tasks.append(RecommendedTask(
                            type="quiz",
                            entity_id=quiz.id,
                            title=quiz.title,
                            estimated_minutes=quiz_time,
                            priority="medium" if weak_topic["priority"] == "medium" else "high",
                            reason=f"Weak topic: {weak_topic['topic']} (avg {weak_topic['avg_score']:.0f}%)",
                            topic=weak_topic["topic"]
                        ))
                        time_used += quiz_time
        
        # Task 3: Goal Progress (Priority 3)
        if active_goals and time_used < time_budget:
            # Find quizzes or documents related to goals
            remaining_time = time_budget - time_used
            
            if remaining_time >= 10:  # Minimum 10 minutes
                # Try to add one more quiz for general practice
                general_quiz = self.db.query(Quiz).filter(
                    Quiz.created_by == self.user_id
                ).order_by(func.random()).first()
                
                if general_quiz:
                    quiz_time = min(15, remaining_time)
                    tasks.append(RecommendedTask(
                        type="quiz",
                        entity_id=general_quiz.id,
                        title=general_quiz.title,
                        estimated_minutes=quiz_time,
                        priority="normal",
                        reason="Continue your learning journey",
                        topic=general_quiz.quiz_type
                    ))
                    time_used += quiz_time
        
        # If no tasks generated (new user), add a default suggestion
        if not tasks:
            tasks.append(RecommendedTask(
                type="free_practice",
                estimated_minutes=min(15, time_budget),
                priority="normal",
                reason="Get started! Upload a document or create flashcards",
                topic="General"
            ))
        
        return tasks
    
    def _generate_summary(
        self,
        tasks: List[RecommendedTask],
        due_flashcards: List[Flashcard],
        weak_topics: List[Dict]
    ) -> str:
        """Generate AI-like summary text"""
        parts = []
        
        # Greeting based on time of day
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning! ☀️"
        elif hour < 18:
            greeting = "Good afternoon! 🌤️"
        else:
            greeting = "Good evening! 🌙"
        
        parts.append(greeting)
        
        # Task summary
        task_descriptions = []
        for task in tasks:
            if task.type == "flashcard_review":
                task_descriptions.append(f"review {task.count} flashcards")
            elif task.type == "quiz":
                task_descriptions.append(f"take '{task.title}' quiz")
            else:
                task_descriptions.append("practice")
        
        if task_descriptions:
            parts.append(f"Today: {', '.join(task_descriptions)}.")
        
        # Weak topics alert
        if weak_topics:
            topic_names = [t['topic'] for t in weak_topics[:2]]
            parts.append(f"Focus on: {', '.join(topic_names)}.")
        
        # Encouragement
        if due_flashcards:
            parts.append("Great job keeping up with your reviews! 🎯")
        else:
            parts.append("Keep up the excellent work! 💪")
        
        return " ".join(parts)
    
    def _calculate_priority(
        self,
        due_flashcards: List[Flashcard],
        active_goals: List[LearningGoal]
    ) -> str:
        """Calculate overall plan priority"""
        if len(due_flashcards) > 30:
            return "critical"
        elif len(due_flashcards) > 15:
            return "high"
        
        # Check goal deadlines
        urgent_goals = [g for g in active_goals if (g.target_date - date.today()).days <= 7]
        if urgent_goals:
            return "high"
        
        return "normal"
    
    def _calculate_difficulty(self, tasks: List[RecommendedTask]) -> str:
        """Calculate overall plan difficulty"""
        high_priority_count = len([t for t in tasks if t.priority == "high"])
        
        if high_priority_count >= 2:
            return "hard"
        elif high_priority_count == 1:
            return "medium"
        else:
            return "easy"


# Helper function for easy access
def generate_daily_plan(db: Session, user_id: int, plan_date: date = None) -> DailyStudyPlanCreate:
    """
    Generate daily study plan for a user
    
    Usage:
        plan = generate_daily_plan(db, user_id=123)
    """
    generator = DailyPlanGenerator(db, user_id)
    return generator.generate_plan(plan_date)

