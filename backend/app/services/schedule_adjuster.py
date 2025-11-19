"""
Schedule Adjustment Service
Handles automatic schedule adjustments based on user performance and missed days
"""
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from decimal import Decimal

from app.models.study_schedule import StudySchedule, DailyStudyPlan
from app.models.learning_goal import LearningGoal
from app.models.quiz import QuizAttempt
from app.models.flashcard import Flashcard
import logging

logger = logging.getLogger(__name__)


class ScheduleAdjuster:
    """Adjust study schedules based on performance and adherence"""
    
    def __init__(self, db: Session, schedule: StudySchedule):
        self.db = db
        self.schedule = schedule
        self.user_id = schedule.user_id
    
    def analyze_and_adjust(self) -> Dict[str, Any]:
        """
        Analyze schedule performance and make adjustments if needed
        
        Returns:
            Dict with adjustment details
        """
        analysis = self._analyze_performance()
        
        # Check if adjustment is needed
        if not self._should_adjust(analysis):
            return {
                "adjusted": False,
                "reason": "Schedule is performing well, no adjustment needed",
                "analysis": analysis
            }
        
        # Determine adjustment strategy based on adaptation_mode
        if self.schedule.adaptation_mode == 'strict':
            return {
                "adjusted": False,
                "reason": "Schedule is in strict mode, no auto-adjustments",
                "analysis": analysis
            }
        
        adjustment = self._calculate_adjustment(analysis)
        
        if adjustment["adjustment_needed"]:
            self._apply_adjustment(adjustment)
            return {
                "adjusted": True,
                "adjustment": adjustment,
                "analysis": analysis
            }
        
        return {
            "adjusted": False,
            "reason": "No significant adjustment needed",
            "analysis": analysis
        }
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze schedule performance metrics"""
        today = date.today()
        
        # Get all plans for this schedule
        plans = self.db.query(DailyStudyPlan).filter(
            DailyStudyPlan.schedule_id == self.schedule.id
        ).order_by(DailyStudyPlan.plan_date).all()
        
        # Calculate missed days
        missed_days = []
        completed_days = []
        partially_completed = []
        
        for plan in plans:
            if plan.plan_date < today:
                if plan.status == 'skipped':
                    missed_days.append(plan)
                elif plan.is_completed:
                    completed_days.append(plan)
                elif plan.status == 'partially_completed':
                    partially_completed.append(plan)
        
        # Calculate adherence rate
        total_past_days = len([p for p in plans if p.plan_date < today])
        adherence_rate = (len(completed_days) / total_past_days * 100) if total_past_days > 0 else 0
        
        # Detect burnout (consecutive missed days)
        consecutive_missed = self._count_consecutive_missed(plans, today)
        
        # Calculate average performance
        avg_performance = self._calculate_avg_performance(completed_days)
        
        # Check if overloaded (too many tasks completed but low accuracy)
        is_overloaded = self._detect_overload(completed_days)
        
        # Calculate catch-up needed
        catch_up_needed = self._calculate_catch_up_needed(missed_days, partially_completed)
        
        return {
            "total_plans": len(plans),
            "completed_days": len(completed_days),
            "missed_days": len(missed_days),
            "partially_completed": len(partially_completed),
            "adherence_rate": adherence_rate,
            "consecutive_missed": consecutive_missed,
            "avg_performance": avg_performance,
            "is_overloaded": is_overloaded,
            "catch_up_needed": catch_up_needed,
            "total_past_days": total_past_days
        }
    
    def _should_adjust(self, analysis: Dict[str, Any]) -> bool:
        """Determine if schedule should be adjusted"""
        # Adjust if adherence is too low
        if analysis["adherence_rate"] < 50:
            return True
        
        # Adjust if too many consecutive missed days (burnout)
        if analysis["consecutive_missed"] >= 3:
            return True
        
        # Adjust if overloaded
        if analysis["is_overloaded"]:
            return True
        
        # Adjust if significant catch-up needed
        if analysis["catch_up_needed"]["days"] >= 5:
            return True
        
        return False
    
    def _calculate_adjustment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate what adjustments to make"""
        config = self.schedule.schedule_config or {}
        current_daily_minutes = config.get('daily_minutes', 30)
        
        adjustment = {
            "adjustment_needed": False,
            "new_daily_minutes": current_daily_minutes,
            "reason": "",
            "strategy": self.schedule.catch_up_strategy
        }
        
        # Strategy 1: Reduce load if overloaded or burnout
        if analysis["is_overloaded"] or analysis["consecutive_missed"] >= 3:
            # Reduce by 20-30%
            reduction = int(current_daily_minutes * 0.25)
            new_minutes = max(
                self.schedule.min_daily_load,
                current_daily_minutes - reduction
            )
            adjustment["adjustment_needed"] = True
            adjustment["new_daily_minutes"] = new_minutes
            adjustment["reason"] = "Reducing load due to overload/burnout detection"
            return adjustment
        
        # Strategy 2: Catch-up strategy
        if analysis["catch_up_needed"]["days"] > 0:
            if self.schedule.catch_up_strategy == 'skip':
                # Skip missed days, continue as normal
                adjustment["adjustment_needed"] = False
                adjustment["reason"] = "Skipping missed days (skip strategy)"
                return adjustment
            
            elif self.schedule.catch_up_strategy == 'gradual':
                # Gradually increase load to catch up
                catch_up_days = analysis["catch_up_needed"]["days"]
                increase = min(15, catch_up_days * 2)  # Max 15 min increase
                new_minutes = min(
                    self.schedule.max_daily_load,
                    current_daily_minutes + increase
                )
                adjustment["adjustment_needed"] = True
                adjustment["new_daily_minutes"] = new_minutes
                adjustment["reason"] = f"Gradually catching up {catch_up_days} missed days"
                return adjustment
            
            elif self.schedule.catch_up_strategy == 'intensive':
                # More intensive catch-up
                catch_up_days = analysis["catch_up_needed"]["days"]
                increase = min(30, catch_up_days * 5)  # Max 30 min increase
                new_minutes = min(
                    self.schedule.max_daily_load,
                    current_daily_minutes + increase
                )
                adjustment["adjustment_needed"] = True
                adjustment["new_daily_minutes"] = new_minutes
                adjustment["reason"] = f"Intensive catch-up for {catch_up_days} missed days"
                return adjustment
        
        # Strategy 3: Increase load if doing very well
        if (analysis["adherence_rate"] >= 90 and 
            analysis["avg_performance"] >= 85 and
            current_daily_minutes < self.schedule.max_daily_load):
            # Can increase slightly
            increase = min(10, int(current_daily_minutes * 0.1))
            new_minutes = min(
                self.schedule.max_daily_load,
                current_daily_minutes + increase
            )
            adjustment["adjustment_needed"] = True
            adjustment["new_daily_minutes"] = new_minutes
            adjustment["reason"] = "Increasing load due to excellent performance"
            return adjustment
        
        return adjustment
    
    def _apply_adjustment(self, adjustment: Dict[str, Any]):
        """Apply the adjustment to the schedule"""
        config = self.schedule.schedule_config or {}
        config["daily_minutes"] = adjustment["new_daily_minutes"]
        
        self.schedule.schedule_config = config
        self.schedule.last_adjusted_at = datetime.utcnow()
        self.schedule.adjustment_reason = adjustment["reason"]
        self.schedule.adjustment_count += 1
        
        self.db.commit()
        self.db.refresh(self.schedule)
        
        logger.info(
            f"Adjusted schedule {self.schedule.id}: "
            f"{adjustment['new_daily_minutes']} min/day - {adjustment['reason']}"
        )
    
    def _count_consecutive_missed(self, plans: List[DailyStudyPlan], today: date) -> int:
        """Count consecutive missed days (burnout indicator)"""
        missed_recent = [
            p for p in plans 
            if p.plan_date < today and p.status == 'skipped'
        ]
        
        if not missed_recent:
            return 0
        
        # Sort by date descending
        missed_recent.sort(key=lambda x: x.plan_date, reverse=True)
        
        # Count consecutive from today backwards
        consecutive = 0
        current_date = today - timedelta(days=1)
        
        for plan in missed_recent:
            if plan.plan_date == current_date:
                consecutive += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return consecutive
    
    def _calculate_avg_performance(self, completed_plans: List[DailyStudyPlan]) -> float:
        """Calculate average performance from completed plans"""
        if not completed_plans:
            return 0.0
        
        total_accuracy = 0.0
        count = 0
        
        for plan in completed_plans:
            if plan.actual_performance:
                perf = plan.actual_performance
                if isinstance(perf, dict):
                    overall = perf.get('overall_accuracy', 0)
                    if overall:
                        total_accuracy += float(overall)
                        count += 1
        
        return (total_accuracy / count) if count > 0 else 0.0
    
    def _detect_overload(self, completed_plans: List[DailyStudyPlan]) -> bool:
        """Detect if user is overloaded (completing tasks but low accuracy)"""
        if len(completed_plans) < 3:
            return False
        
        # Check last 5 completed plans
        recent_plans = sorted(
            [p for p in completed_plans if p.actual_performance],
            key=lambda x: x.plan_date,
            reverse=True
        )[:5]
        
        if len(recent_plans) < 3:
            return False
        
        low_accuracy_count = 0
        for plan in recent_plans:
            perf = plan.actual_performance
            if isinstance(perf, dict):
                accuracy = perf.get('overall_accuracy', 100)
                if accuracy < 60:  # Low accuracy
                    low_accuracy_count += 1
        
        # If 60%+ of recent plans have low accuracy, likely overloaded
        return (low_accuracy_count / len(recent_plans)) >= 0.6
    
    def _calculate_catch_up_needed(
        self, 
        missed_days: List[DailyStudyPlan],
        partially_completed: List[DailyStudyPlan]
    ) -> Dict[str, Any]:
        """Calculate how much catch-up is needed"""
        total_missed = len(missed_days) + len(partially_completed)
        
        # Calculate total time missed
        total_time_missed = 0
        for plan in missed_days + partially_completed:
            total_time_missed += plan.total_estimated_minutes
        
        return {
            "days": total_missed,
            "total_minutes": total_time_missed,
            "estimated_catch_up_days": max(1, int(total_missed / 2))  # Spread over half the days
        }


def adjust_schedule(db: Session, schedule_id: int, user_id: int) -> Dict[str, Any]:
    """
    Main function to adjust a schedule
    
    Args:
        db: Database session
        schedule_id: Schedule ID
        user_id: User ID
        
    Returns:
        Adjustment result dictionary
    """
    from app.crud import crud_study_schedule
    
    schedule = crud_study_schedule.get_schedule(db, schedule_id, user_id)
    if not schedule:
        return {
            "adjusted": False,
            "error": "Schedule not found"
        }
    
    adjuster = ScheduleAdjuster(db, schedule)
    return adjuster.analyze_and_adjust()

