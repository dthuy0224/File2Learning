from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.models.user import User
from app.crud.crud_recommendation import crud_recommendation
from app.schemas.recommendation import (
    RecommendationCreate, RecommendationUpdate, RecommendationInteraction,
    RecommendationResponse, RecommendationListResponse, RecommendationStats,
    RecommendationType, RecommendationPriority
)
from app.services.recommendation_engine import generate_recommendations_for_user

router = APIRouter()


@router.get("", response_model=RecommendationListResponse)
@router.get("/", response_model=RecommendationListResponse)
def get_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True, description="Show only active recommendations"),
    type_filter: Optional[RecommendationType] = Query(None, description="Filter by type"),
    priority_filter: Optional[RecommendationPriority] = Query(None, description="Filter by priority")
):
    """
    Get all recommendations for the current user
    """
    recommendations = crud_recommendation.get_user_recommendations(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        active_only=active_only,
        type_filter=type_filter,
        priority_filter=priority_filter
    )
    
    total = len(recommendations)
    active_count = sum(1 for rec in recommendations if not rec.is_dismissed and not rec.is_accepted and not rec.is_expired)
    
    # Convert SQLAlchemy models to Pydantic with computed fields
    recommendation_responses = []
    for rec in recommendations:
        rec_dict = {
            "id": rec.id,
            "user_id": rec.user_id,
            "type": rec.type,
            "priority": rec.priority,
            "title": rec.title,
            "description": rec.description,
            "reason": rec.reason,
            "target_resource_type": rec.target_resource_type,
            "target_resource_id": rec.target_resource_id,
            "relevance_score": rec.relevance_score,
            "confidence_score": rec.confidence_score,
            "expected_impact": rec.expected_impact,
            "extra_data": rec.extra_data,
            "expires_at": rec.expires_at,
            "is_viewed": bool(rec.is_viewed),
            "is_accepted": bool(rec.is_accepted),
            "is_dismissed": bool(rec.is_dismissed),
            "viewed_at": rec.viewed_at,
            "accepted_at": rec.accepted_at,
            "dismissed_at": rec.dismissed_at,
            "created_at": rec.created_at,
            "updated_at": rec.updated_at,
            "is_expired": rec.is_expired,
            "is_active": rec.is_active
        }
        recommendation_responses.append(RecommendationResponse(**rec_dict))
    
    return RecommendationListResponse(
        total=total,
        active_count=active_count,
        recommendations=recommendation_responses
    )


@router.get("/active", response_model=List[RecommendationResponse])
def get_active_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations")
):
    """
    Get active (not dismissed/accepted/expired) recommendations for the current user
    """
    recommendations = crud_recommendation.get_active_recommendations(
        db,
        user_id=current_user.id,
        limit=limit
    )
    
    # Convert to response models
    recommendation_responses = []
    for rec in recommendations:
        rec_dict = {
            "id": rec.id,
            "user_id": rec.user_id,
            "type": rec.type,
            "priority": rec.priority,
            "title": rec.title,
            "description": rec.description,
            "reason": rec.reason,
            "target_resource_type": rec.target_resource_type,
            "target_resource_id": rec.target_resource_id,
            "relevance_score": rec.relevance_score,
            "confidence_score": rec.confidence_score,
            "expected_impact": rec.expected_impact,
            "extra_data": rec.extra_data,
            "expires_at": rec.expires_at,
            "is_viewed": bool(rec.is_viewed),
            "is_accepted": bool(rec.is_accepted),
            "is_dismissed": bool(rec.is_dismissed),
            "viewed_at": rec.viewed_at,
            "accepted_at": rec.accepted_at,
            "dismissed_at": rec.dismissed_at,
            "created_at": rec.created_at,
            "updated_at": rec.updated_at,
            "is_expired": rec.is_expired,
            "is_active": rec.is_active
        }
        recommendation_responses.append(RecommendationResponse(**rec_dict))
    
    return recommendation_responses


@router.get("/stats", response_model=RecommendationStats)
def get_recommendation_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get recommendation statistics for the current user
    """
    stats = crud_recommendation.get_stats(db, user_id=current_user.id)
    return RecommendationStats(**stats)


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    max_recommendations: int = Query(10, ge=1, le=50, description="Maximum number of recommendations to generate")
):
    """
    Generate new personalized recommendations for the current user
    This uses AI to analyze learning patterns and create tailored suggestions
    """
    count = generate_recommendations_for_user(db, current_user.id, max_recommendations)
    
    return {
        "message": f"Successfully generated {count} new recommendations",
        "count": count
    }


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    *,
    db: Session = Depends(get_db),
    recommendation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get a specific recommendation by ID
    """
    recommendation = crud_recommendation.get(db, recommendation_id)
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    if recommendation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this recommendation"
        )
    
    rec_dict = {
        "id": recommendation.id,
        "user_id": recommendation.user_id,
        "type": recommendation.type,
        "priority": recommendation.priority,
        "title": recommendation.title,
        "description": recommendation.description,
        "reason": recommendation.reason,
        "target_resource_type": recommendation.target_resource_type,
        "target_resource_id": recommendation.target_resource_id,
        "relevance_score": recommendation.relevance_score,
        "confidence_score": recommendation.confidence_score,
        "expected_impact": recommendation.expected_impact,
        "metadata": recommendation.metadata,
        "expires_at": recommendation.expires_at,
        "is_viewed": bool(recommendation.is_viewed),
        "is_accepted": bool(recommendation.is_accepted),
        "is_dismissed": bool(recommendation.is_dismissed),
        "viewed_at": recommendation.viewed_at,
        "accepted_at": recommendation.accepted_at,
        "dismissed_at": recommendation.dismissed_at,
        "created_at": recommendation.created_at,
        "updated_at": recommendation.updated_at,
        "is_expired": recommendation.is_expired,
        "is_active": recommendation.is_active
    }
    
    return RecommendationResponse(**rec_dict)


@router.put("/{recommendation_id}/viewed", response_model=RecommendationResponse)
def mark_recommendation_viewed(
    *,
    db: Session = Depends(get_db),
    recommendation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Mark a recommendation as viewed
    """
    recommendation = crud_recommendation.get(db, recommendation_id)
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    if recommendation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this recommendation"
        )
    
    updated_rec = crud_recommendation.mark_viewed(db, recommendation_id=recommendation_id)
    
    rec_dict = {
        "id": updated_rec.id,
        "user_id": updated_rec.user_id,
        "type": updated_rec.type,
        "priority": updated_rec.priority,
        "title": updated_rec.title,
        "description": updated_rec.description,
        "reason": updated_rec.reason,
        "target_resource_type": updated_rec.target_resource_type,
        "target_resource_id": updated_rec.target_resource_id,
        "relevance_score": updated_rec.relevance_score,
        "confidence_score": updated_rec.confidence_score,
        "expected_impact": updated_rec.expected_impact,
        "metadata": updated_rec.metadata,
        "expires_at": updated_rec.expires_at,
        "is_viewed": bool(updated_rec.is_viewed),
        "is_accepted": bool(updated_rec.is_accepted),
        "is_dismissed": bool(updated_rec.is_dismissed),
        "viewed_at": updated_rec.viewed_at,
        "accepted_at": updated_rec.accepted_at,
        "dismissed_at": updated_rec.dismissed_at,
        "created_at": updated_rec.created_at,
        "updated_at": updated_rec.updated_at,
        "is_expired": updated_rec.is_expired,
        "is_active": updated_rec.is_active
    }
    
    return RecommendationResponse(**rec_dict)


@router.put("/{recommendation_id}/accepted", response_model=RecommendationResponse)
def mark_recommendation_accepted(
    *,
    db: Session = Depends(get_db),
    recommendation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Mark a recommendation as accepted (user acted on it)
    """
    recommendation = crud_recommendation.get(db, recommendation_id)
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    if recommendation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this recommendation"
        )
    
    updated_rec = crud_recommendation.mark_accepted(db, recommendation_id=recommendation_id)
    
    rec_dict = {
        "id": updated_rec.id,
        "user_id": updated_rec.user_id,
        "type": updated_rec.type,
        "priority": updated_rec.priority,
        "title": updated_rec.title,
        "description": updated_rec.description,
        "reason": updated_rec.reason,
        "target_resource_type": updated_rec.target_resource_type,
        "target_resource_id": updated_rec.target_resource_id,
        "relevance_score": updated_rec.relevance_score,
        "confidence_score": updated_rec.confidence_score,
        "expected_impact": updated_rec.expected_impact,
        "metadata": updated_rec.metadata,
        "expires_at": updated_rec.expires_at,
        "is_viewed": bool(updated_rec.is_viewed),
        "is_accepted": bool(updated_rec.is_accepted),
        "is_dismissed": bool(updated_rec.is_dismissed),
        "viewed_at": updated_rec.viewed_at,
        "accepted_at": updated_rec.accepted_at,
        "dismissed_at": updated_rec.dismissed_at,
        "created_at": updated_rec.created_at,
        "updated_at": updated_rec.updated_at,
        "is_expired": updated_rec.is_expired,
        "is_active": updated_rec.is_active
    }
    
    return RecommendationResponse(**rec_dict)


@router.put("/{recommendation_id}/dismissed", response_model=RecommendationResponse)
def mark_recommendation_dismissed(
    *,
    db: Session = Depends(get_db),
    recommendation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Mark a recommendation as dismissed
    """
    recommendation = crud_recommendation.get(db, recommendation_id)
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    if recommendation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this recommendation"
        )
    
    updated_rec = crud_recommendation.mark_dismissed(db, recommendation_id=recommendation_id)
    
    rec_dict = {
        "id": updated_rec.id,
        "user_id": updated_rec.user_id,
        "type": updated_rec.type,
        "priority": updated_rec.priority,
        "title": updated_rec.title,
        "description": updated_rec.description,
        "reason": updated_rec.reason,
        "target_resource_type": updated_rec.target_resource_type,
        "target_resource_id": updated_rec.target_resource_id,
        "relevance_score": updated_rec.relevance_score,
        "confidence_score": updated_rec.confidence_score,
        "expected_impact": updated_rec.expected_impact,
        "metadata": updated_rec.metadata,
        "expires_at": updated_rec.expires_at,
        "is_viewed": bool(updated_rec.is_viewed),
        "is_accepted": bool(updated_rec.is_accepted),
        "is_dismissed": bool(updated_rec.is_dismissed),
        "viewed_at": updated_rec.viewed_at,
        "accepted_at": updated_rec.accepted_at,
        "dismissed_at": updated_rec.dismissed_at,
        "created_at": updated_rec.created_at,
        "updated_at": updated_rec.updated_at,
        "is_expired": updated_rec.is_expired,
        "is_active": updated_rec.is_active
    }
    
    return RecommendationResponse(**rec_dict)


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recommendation(
    *,
    db: Session = Depends(get_db),
    recommendation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a recommendation
    """
    recommendation = crud_recommendation.get(db, recommendation_id)
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    if recommendation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this recommendation"
        )
    
    crud_recommendation.delete(db, recommendation_id=recommendation_id)
    return None

