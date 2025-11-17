"""
Milestone Generator Service
Auto-generates milestones from learning goals based on goal type and timeline
"""
from typing import List, Dict, Any
from datetime import date, timedelta
from app.models.learning_goal import LearningGoal
import logging

logger = logging.getLogger(__name__)


class MilestoneGenerator:
    """Generate milestones for learning goals"""
    
    @staticmethod
    def generate_milestones(goal: LearningGoal) -> List[Dict[str, Any]]:
        """
        Generate milestones based on goal type and timeline
        
        Args:
            goal: LearningGoal object
            
        Returns:
            List of milestone dictionaries
        """
        total_days = (goal.target_date - goal.start_date).days
        
        if total_days <= 0:
            return []
        
        # Determine number of milestones based on duration
        if total_days <= 7:
            num_milestones = 2  # 2 milestones for 1 week
        elif total_days <= 30:
            num_milestones = 4  # 4 milestones for 1 month
        elif total_days <= 90:
            num_milestones = 6  # 6 milestones for 3 months
        else:
            num_milestones = 8  # 8 milestones for longer goals
        
        milestones = []
        
        # Generate milestones based on goal type
        if goal.goal_type == 'vocabulary_count':
            milestones = MilestoneGenerator._generate_vocabulary_milestones(
                goal, num_milestones, total_days
            )
        elif goal.goal_type == 'exam_preparation':
            milestones = MilestoneGenerator._generate_exam_milestones(
                goal, num_milestones, total_days
            )
        elif goal.goal_type == 'quiz_score':
            milestones = MilestoneGenerator._generate_quiz_score_milestones(
                goal, num_milestones, total_days
            )
        elif goal.goal_type == 'time_based':
            milestones = MilestoneGenerator._generate_time_based_milestones(
                goal, num_milestones, total_days
            )
        elif goal.goal_type == 'topic_mastery':
            milestones = MilestoneGenerator._generate_topic_mastery_milestones(
                goal, num_milestones, total_days
            )
        else:
            # Generic milestones
            milestones = MilestoneGenerator._generate_generic_milestones(
                goal, num_milestones, total_days
            )
        
        return milestones
    
    @staticmethod
    def _generate_vocabulary_milestones(
        goal: LearningGoal, 
        num_milestones: int, 
        total_days: int
    ) -> List[Dict[str, Any]]:
        """Generate milestones for vocabulary count goals"""
        target_vocab = goal.target_metrics.get('vocabulary', 0)
        if target_vocab == 0:
            return []
        
        milestones = []
        days_per_milestone = total_days / num_milestones
        vocab_per_milestone = target_vocab / num_milestones
        
        for i in range(1, num_milestones + 1):
            week_num = int((i * days_per_milestone) / 7) + 1
            target_vocab_count = int(i * vocab_per_milestone)
            milestone_date = goal.start_date + timedelta(days=int(i * days_per_milestone))
            
            milestones.append({
                "week": week_num,
                "target": f"{target_vocab_count} words",
                "status": "pending",
                "description": f"Learn {target_vocab_count} vocabulary words",
                "target_value": target_vocab_count,
                "unit": "words",
                "estimated_date": milestone_date.isoformat()
            })
        
        return milestones
    
    @staticmethod
    def _generate_exam_milestones(
        goal: LearningGoal,
        num_milestones: int,
        total_days: int
    ) -> List[Dict[str, Any]]:
        """Generate milestones for exam preparation goals"""
        exam_name = goal.target_metrics.get('exam', 'Exam')
        target_score = goal.target_metrics.get('target_score', 0)
        
        milestones = []
        days_per_milestone = total_days / num_milestones
        
        # Exam preparation milestones
        milestone_templates = [
            "Complete diagnostic test",
            "Master Reading section",
            "Master Writing section",
            "Master Listening section",
            "Master Speaking section",
            "Complete practice test 1",
            "Complete practice test 2",
            "Final review and preparation"
        ]
        
        for i in range(1, min(num_milestones + 1, len(milestone_templates) + 1)):
            week_num = int((i * days_per_milestone) / 7) + 1
            milestone_date = goal.start_date + timedelta(days=int(i * days_per_milestone))
            
            template_idx = min(i - 1, len(milestone_templates) - 1)
            description = milestone_templates[template_idx]
            
            milestones.append({
                "week": week_num,
                "target": f"{description}",
                "status": "pending",
                "description": f"{exam_name}: {description}",
                "target_value": target_score,
                "unit": "score",
                "estimated_date": milestone_date.isoformat()
            })
        
        return milestones
    
    @staticmethod
    def _generate_quiz_score_milestones(
        goal: LearningGoal,
        num_milestones: int,
        total_days: int
    ) -> List[Dict[str, Any]]:
        """Generate milestones for quiz score goals"""
        target_score = goal.target_metrics.get('target_score', 0)
        if target_score == 0:
            return []
        
        milestones = []
        days_per_milestone = total_days / num_milestones
        score_increment = target_score / num_milestones
        
        for i in range(1, num_milestones + 1):
            week_num = int((i * days_per_milestone) / 7) + 1
            milestone_score = int(i * score_increment)
            milestone_date = goal.start_date + timedelta(days=int(i * days_per_milestone))
            
            milestones.append({
                "week": week_num,
                "target": f"{milestone_score}% average",
                "status": "pending",
                "description": f"Achieve {milestone_score}% average quiz score",
                "target_value": milestone_score,
                "unit": "percentage",
                "estimated_date": milestone_date.isoformat()
            })
        
        return milestones
    
    @staticmethod
    def _generate_time_based_milestones(
        goal: LearningGoal,
        num_milestones: int,
        total_days: int
    ) -> List[Dict[str, Any]]:
        """Generate milestones for time-based goals"""
        target_hours = goal.target_metrics.get('study_time', 0)
        if target_hours == 0:
            return []
        
        milestones = []
        days_per_milestone = total_days / num_milestones
        hours_per_milestone = target_hours / num_milestones
        
        for i in range(1, num_milestones + 1):
            week_num = int((i * days_per_milestone) / 7) + 1
            milestone_hours = int(i * hours_per_milestone)
            milestone_date = goal.start_date + timedelta(days=int(i * days_per_milestone))
            
            milestones.append({
                "week": week_num,
                "target": f"{milestone_hours} hours",
                "status": "pending",
                "description": f"Complete {milestone_hours} hours of study",
                "target_value": milestone_hours,
                "unit": "hours",
                "estimated_date": milestone_date.isoformat()
            })
        
        return milestones
    
    @staticmethod
    def _generate_topic_mastery_milestones(
        goal: LearningGoal,
        num_milestones: int,
        total_days: int
    ) -> List[Dict[str, Any]]:
        """Generate milestones for topic mastery goals"""
        topic = goal.target_metrics.get('topic', 'Topic')
        target_accuracy = goal.target_metrics.get('target_accuracy', 85)
        
        milestones = []
        days_per_milestone = total_days / num_milestones
        
        milestone_stages = [
            "Introduction and basics",
            "Practice exercises",
            "Intermediate concepts",
            "Advanced practice",
            "Review and reinforcement",
            "Mastery assessment"
        ]
        
        for i in range(1, min(num_milestones + 1, len(milestone_stages) + 1)):
            week_num = int((i * days_per_milestone) / 7) + 1
            milestone_date = goal.start_date + timedelta(days=int(i * days_per_milestone))
            
            stage_idx = min(i - 1, len(milestone_stages) - 1)
            stage = milestone_stages[stage_idx]
            
            milestones.append({
                "week": week_num,
                "target": f"{stage}",
                "status": "pending",
                "description": f"{topic}: {stage}",
                "target_value": target_accuracy,
                "unit": "accuracy",
                "estimated_date": milestone_date.isoformat()
            })
        
        return milestones
    
    @staticmethod
    def _generate_generic_milestones(
        goal: LearningGoal,
        num_milestones: int,
        total_days: int
    ) -> List[Dict[str, Any]]:
        """Generate generic milestones for any goal type"""
        milestones = []
        days_per_milestone = total_days / num_milestones
        
        for i in range(1, num_milestones + 1):
            week_num = int((i * days_per_milestone) / 7) + 1
            progress_pct = int((i / num_milestones) * 100)
            milestone_date = goal.start_date + timedelta(days=int(i * days_per_milestone))
            
            milestones.append({
                "week": week_num,
                "target": f"{progress_pct}% progress",
                "status": "pending",
                "description": f"Reach {progress_pct}% of goal",
                "target_value": progress_pct,
                "unit": "percentage",
                "estimated_date": milestone_date.isoformat()
            })
        
        return milestones


def generate_milestones_for_goal(goal: LearningGoal) -> List[Dict[str, Any]]:
    """Helper function to generate milestones for a goal"""
    return MilestoneGenerator.generate_milestones(goal)

