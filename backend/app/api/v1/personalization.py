"""
Personalization API Routes
Handles user behavior tracking and personalized recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.services.personalization_service import personalization_service

router = APIRouter(prefix="/personalization", tags=["Personalization"])

class BehaviorTrackingRequest(BaseModel):
    event_type: str
    event_data: Dict[str, Any]

class RecommendationRequest(BaseModel):
    limit: int = 10
    mood: Optional[str] = None

@router.post("/track-behavior")
async def track_user_behavior(
    request: BehaviorTrackingRequest,
    current_user: dict = Depends(get_current_user)
):
    """Track user behavior for personalization"""
    try:
        await personalization_service.track_user_behavior(
            current_user["uid"], 
            request.event_type, 
            request.event_data
        )
        return {"success": True, "message": "Behavior tracked successfully"}
    except Exception as e:
        # Don't raise error for tracking, just log it
        return {"success": False, "error": str(e)}

@router.get("/recommendations")
async def get_personalized_recommendations(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get personalized recipe recommendations"""
    try:
        recommendations = await personalization_service.get_personalized_recommendations(
            current_user["uid"], limit
        )
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "user_id": current_user["uid"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.get("/trending")
async def get_trending_recipes(
    time_period: str = "week",
    limit: int = 20
):
    """Get trending recipes"""
    try:
        trending_recipes = await personalization_service.get_trending_recipes(
            time_period, limit
        )
        return {
            "trending_recipes": trending_recipes,
            "total": len(trending_recipes),
            "time_period": time_period
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending recipes: {str(e)}"
        )

@router.get("/recommendations/mood/{mood}")
async def get_mood_based_recommendations(
    mood: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get recipe recommendations based on user's mood"""
    try:
        # Validate mood
        valid_moods = ["comfort", "healthy", "adventurous", "quick", "indulgent", "light"]
        if mood not in valid_moods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid mood. Valid moods are: {', '.join(valid_moods)}"
            )
        
        recommendations = await personalization_service.get_user_recommendations_by_mood(
            current_user["uid"], mood, limit
        )
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "mood": mood,
            "user_id": current_user["uid"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mood-based recommendations: {str(e)}"
        )

@router.get("/seasonal-ingredients")
async def get_seasonal_ingredient_suggestions(
    current_user: dict = Depends(get_current_user)
):
    """Get seasonal ingredient suggestions"""
    try:
        suggestions = await personalization_service.get_seasonal_ingredient_suggestions(
            current_user["uid"]
        )
        return {
            "suggestions": suggestions,
            "total": len(suggestions),
            "user_id": current_user["uid"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get seasonal suggestions: {str(e)}"
        ) 