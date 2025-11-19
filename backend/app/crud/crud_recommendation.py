from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta

from app.models.recommendation import AdaptiveRecommendation, RecommendationType, RecommendationPriority
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate, RecommendationInteraction


class CRUDRecommendation:
    
    def create(
        self,
        db: Session,
        *,
        recommendation: RecommendationCreate,
        user_id: int
    ) -> AdaptiveRecommendation:
        """Create a new recommendation for a user"""
        db_recommendation = AdaptiveRecommendation(
            user_id=user_id,
            type=recommendation.type.value if hasattr(recommendation.type, 'value') else recommendation.type,
            priority=recommendation.priority.value if hasattr(recommendation.priority, 'value') else recommendation.priority,
            title=recommendation.title,
            description=recommendation.description,
            reason=recommendation.reason,
            target_resource_type=recommendation.target_resource_type,
            target_resource_id=recommendation.target_resource_id,
            relevance_score=recommendation.relevance_score,
            confidence_score=recommendation.confidence_score,
            expected_impact=recommendation.expected_impact,
            extra_data=recommendation.extra_data,
            expires_at=recommendation.expires_at
        )
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def get(self, db: Session, recommendation_id: int) -> Optional[AdaptiveRecommendation]:
        """Get a recommendation by ID"""
        return db.query(AdaptiveRecommendation).filter(
            AdaptiveRecommendation.id == recommendation_id
        ).first()
    
    def get_user_recommendations(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        type_filter: Optional[RecommendationType] = None,
        priority_filter: Optional[RecommendationPriority] = None
    ) -> List[AdaptiveRecommendation]:
        """Get all recommendations for a user with optional filters"""
        query = db.query(AdaptiveRecommendation).filter(
            AdaptiveRecommendation.user_id == user_id
        )
        
        if active_only:
            query = query.filter(
                and_(
                    AdaptiveRecommendation.is_dismissed == 0,
                    AdaptiveRecommendation.is_accepted == 0,
                    or_(
                        AdaptiveRecommendation.expires_at.is_(None),
                        AdaptiveRecommendation.expires_at > datetime.utcnow()
                    )
                )
            )
        
        if type_filter:
            query = query.filter(AdaptiveRecommendation.type == type_filter)
        
        if priority_filter:
            query = query.filter(AdaptiveRecommendation.priority == priority_filter)
        
        return query.order_by(
            AdaptiveRecommendation.priority.desc(),
            AdaptiveRecommendation.relevance_score.desc(),
            AdaptiveRecommendation.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_active_recommendations(
        self,
        db: Session,
        *,
        user_id: int,
        limit: int = 10
    ) -> List[AdaptiveRecommendation]:
        """Get active (not dismissed/accepted/expired) recommendations for a user"""
        return self.get_user_recommendations(
            db,
            user_id=user_id,
            active_only=True,
            limit=limit
        )
    
    def update(
        self,
        db: Session,
        *,
        recommendation_id: int,
        recommendation_update: RecommendationUpdate
    ) -> Optional[AdaptiveRecommendation]:
        """Update a recommendation"""
        db_recommendation = self.get(db, recommendation_id)
        if not db_recommendation:
            return None
        
        update_data = recommendation_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_recommendation, field, value)
        
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def mark_viewed(
        self,
        db: Session,
        *,
        recommendation_id: int
    ) -> Optional[AdaptiveRecommendation]:
        """Mark a recommendation as viewed"""
        db_recommendation = self.get(db, recommendation_id)
        if not db_recommendation:
            return None
        
        db_recommendation.is_viewed = 1
        db_recommendation.viewed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def mark_included_in_plan(
        self,
        db: Session,
        *,
        recommendation_id: int,
        plan_id: int,
        plan_date: str
    ) -> Optional[AdaptiveRecommendation]:
        """Mark recommendation as included in a daily plan"""
        db_recommendation = self.get(db, recommendation_id)
        if not db_recommendation:
            return None
        
        # Update extra_data to track plan inclusion
        if not db_recommendation.extra_data:
            db_recommendation.extra_data = {}
        
        db_recommendation.extra_data['included_in_plan'] = True
        db_recommendation.extra_data['plan_id'] = plan_id
        db_recommendation.extra_data['plan_date'] = plan_date
        
        # Also mark as viewed since user will see it in plan
        if not db_recommendation.is_viewed:
            db_recommendation.is_viewed = 1
            db_recommendation.viewed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def mark_accepted(
        self,
        db: Session,
        *,
        recommendation_id: int
    ) -> Optional[AdaptiveRecommendation]:
        """Mark a recommendation as accepted (user acted on it)"""
        db_recommendation = self.get(db, recommendation_id)
        if not db_recommendation:
            return None
        
        db_recommendation.is_accepted = 1
        db_recommendation.accepted_at = datetime.utcnow()
        if not db_recommendation.is_viewed:
            db_recommendation.is_viewed = 1
            db_recommendation.viewed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def mark_dismissed(
        self,
        db: Session,
        *,
        recommendation_id: int
    ) -> Optional[AdaptiveRecommendation]:
        """Mark a recommendation as dismissed"""
        db_recommendation = self.get(db, recommendation_id)
        if not db_recommendation:
            return None
        
        db_recommendation.is_dismissed = 1
        db_recommendation.dismissed_at = datetime.utcnow()
        if not db_recommendation.is_viewed:
            db_recommendation.is_viewed = 1
            db_recommendation.viewed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def update_interaction(
        self,
        db: Session,
        *,
        recommendation_id: int,
        interaction: RecommendationInteraction
    ) -> Optional[AdaptiveRecommendation]:
        """Update user interaction with a recommendation"""
        db_recommendation = self.get(db, recommendation_id)
        if not db_recommendation:
            return None
        
        now = datetime.utcnow()
        
        if interaction.is_viewed is not None:
            db_recommendation.is_viewed = 1 if interaction.is_viewed else 0
            if interaction.is_viewed:
                db_recommendation.viewed_at = now
        
        if interaction.is_accepted is not None:
            db_recommendation.is_accepted = 1 if interaction.is_accepted else 0
            if interaction.is_accepted:
                db_recommendation.accepted_at = now
                # Auto-mark as viewed
                if not db_recommendation.is_viewed:
                    db_recommendation.is_viewed = 1
                    db_recommendation.viewed_at = now
        
        if interaction.is_dismissed is not None:
            db_recommendation.is_dismissed = 1 if interaction.is_dismissed else 0
            if interaction.is_dismissed:
                db_recommendation.dismissed_at = now
                # Auto-mark as viewed
                if not db_recommendation.is_viewed:
                    db_recommendation.is_viewed = 1
                    db_recommendation.viewed_at = now
        
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def delete(self, db: Session, *, recommendation_id: int) -> bool:
        """Delete a recommendation"""
        db_recommendation = self.get(db, recommendation_id)
        if not db_recommendation:
            return False
        
        db.delete(db_recommendation)
        db.commit()
        return True
    
    def delete_expired(self, db: Session, *, user_id: Optional[int] = None) -> int:
        """Delete expired recommendations. Returns count of deleted items."""
        query = db.query(AdaptiveRecommendation).filter(
            AdaptiveRecommendation.expires_at < datetime.utcnow()
        )
        
        if user_id:
            query = query.filter(AdaptiveRecommendation.user_id == user_id)
        
        count = query.count()
        query.delete(synchronize_session=False)
        db.commit()
        return count
    
    def get_stats(self, db: Session, *, user_id: int) -> Dict[str, Any]:
        """Get recommendation statistics for a user"""
        total = db.query(func.count(AdaptiveRecommendation.id)).filter(
            AdaptiveRecommendation.user_id == user_id
        ).scalar()
        
        active_count = db.query(func.count(AdaptiveRecommendation.id)).filter(
            and_(
                AdaptiveRecommendation.user_id == user_id,
                AdaptiveRecommendation.is_dismissed == 0,
                AdaptiveRecommendation.is_accepted == 0,
                or_(
                    AdaptiveRecommendation.expires_at.is_(None),
                    AdaptiveRecommendation.expires_at > datetime.utcnow()
                )
            )
        ).scalar()
        
        viewed = db.query(func.count(AdaptiveRecommendation.id)).filter(
            AdaptiveRecommendation.user_id == user_id,
            AdaptiveRecommendation.is_viewed == 1
        ).scalar()
        
        accepted = db.query(func.count(AdaptiveRecommendation.id)).filter(
            AdaptiveRecommendation.user_id == user_id,
            AdaptiveRecommendation.is_accepted == 1
        ).scalar()
        
        dismissed = db.query(func.count(AdaptiveRecommendation.id)).filter(
            AdaptiveRecommendation.user_id == user_id,
            AdaptiveRecommendation.is_dismissed == 1
        ).scalar()
        
        expired = db.query(func.count(AdaptiveRecommendation.id)).filter(
            and_(
                AdaptiveRecommendation.user_id == user_id,
                AdaptiveRecommendation.expires_at < datetime.utcnow()
            )
        ).scalar()
        
        # Get count by type
        by_type = {}
        type_counts = db.query(
            AdaptiveRecommendation.type,
            func.count(AdaptiveRecommendation.id)
        ).filter(
            AdaptiveRecommendation.user_id == user_id
        ).group_by(AdaptiveRecommendation.type).all()
        
        for rec_type, count in type_counts:
            by_type[rec_type.value if hasattr(rec_type, 'value') else str(rec_type)] = count
        
        # Get count by priority
        by_priority = {}
        priority_counts = db.query(
            AdaptiveRecommendation.priority,
            func.count(AdaptiveRecommendation.id)
        ).filter(
            AdaptiveRecommendation.user_id == user_id
        ).group_by(AdaptiveRecommendation.priority).all()
        
        for priority, count in priority_counts:
            by_priority[priority.value if hasattr(priority, 'value') else str(priority)] = count
        
        # Calculate acceptance rate
        acceptance_rate = (accepted / total * 100) if total > 0 else 0.0
        
        return {
            "total_generated": total or 0,
            "active_recommendations": active_count or 0,
            "viewed_count": viewed or 0,
            "accepted_count": accepted or 0,
            "dismissed_count": dismissed or 0,
            "expired_count": expired or 0,
            "acceptance_rate": round(acceptance_rate, 2),
            "by_type": by_type,
            "by_priority": by_priority
        }


crud_recommendation = CRUDRecommendation()

