"""
Recipe Management API Routes
Handles recipe favorites, ratings, history, collections, and sharing
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.core.auth import get_current_user
from app.services.recipe_management_service import recipe_management_service
from app.models.history_models import (
    SaveRecipeRequest, FavoriteRecipeRequest, RateRecipeRequest,
    ShareRecipeRequest, CreateCollectionRequest, AddToCollectionRequest,
    RecipeInteractionResponse, RecipeHistoryResponse, UserStatsResponse,
    RecipeCollection
)

router = APIRouter(prefix="/recipe-management", tags=["Recipe Management"])

@router.post("/save", response_model=RecipeInteractionResponse)
async def save_recipe(
    request: SaveRecipeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save a recipe for the current user"""
    try:
        return await recipe_management_service.save_recipe(
            current_user["uid"], request
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recipe: {str(e)}"
        )

@router.post("/favorite", response_model=RecipeInteractionResponse)
async def toggle_favorite(
    request: FavoriteRecipeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Toggle favorite status for a recipe"""
    try:
        return await recipe_management_service.toggle_favorite(
            current_user["uid"], request
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle favorite: {str(e)}"
        )

@router.post("/rate", response_model=RecipeInteractionResponse)
async def rate_recipe(
    request: RateRecipeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Rate a recipe"""
    try:
        return await recipe_management_service.rate_recipe(
            current_user["uid"], request
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rate recipe: {str(e)}"
        )

@router.post("/share", response_model=Dict[str, Any])
async def share_recipe(
    request: ShareRecipeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Share a recipe"""
    try:
        return await recipe_management_service.share_recipe(
            current_user["uid"], request
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to share recipe: {str(e)}"
        )

@router.get("/favorites", response_model=List[RecipeInteractionResponse])
async def get_favorites(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get user's favorite recipes"""
    try:
        return await recipe_management_service.get_user_favorites(
            current_user["uid"], limit, offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get favorites: {str(e)}"
        )

@router.get("/history", response_model=RecipeHistoryResponse)
async def get_recipe_history(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get user's recipe history"""
    try:
        return await recipe_management_service.get_recipe_history(
            current_user["uid"], limit, offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recipe history: {str(e)}"
        )

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive user statistics"""
    try:
        return await recipe_management_service.get_user_stats(
            current_user["uid"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )

@router.post("/collections", response_model=RecipeCollection)
async def create_collection(
    request: CreateCollectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a recipe collection"""
    try:
        return await recipe_management_service.create_collection(
            current_user["uid"], request
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create collection: {str(e)}"
        )

@router.post("/track-view")
async def track_recipe_view(
    recipe_id: str,
    recipe_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Track when a user views a recipe"""
    try:
        await recipe_management_service.track_recipe_view(
            current_user["uid"], recipe_id, recipe_data
        )
        return {"success": True}
    except Exception as e:
        # Don't raise error for tracking, just log it
        return {"success": False, "error": str(e)} 