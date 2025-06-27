"""
Recipes API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import structlog
from app.core.auth import get_optional_user
from app.services.recipe_service import recipe_service
from app.models.recipe_models import RecipeGenerationRequest, RecipeResponse, Recipe

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/generate", response_model=RecipeResponse)
async def generate_recipe(request: RecipeGenerationRequest, current_user: Optional[dict] = Depends(get_optional_user)):
    """Generate recipe from ingredients using AI"""
    try:
        # Extract user ID if authenticated
        user_id = current_user.get('uid') if current_user else None
        
        # Generate recipe using AI
        result = await recipe_service.generate_ai_recipe(
            ingredients=request.ingredients,
            user_id=user_id,
            dietary_restrictions=None,  # Not in current model
            cuisine_preference=request.preferred_cuisine,
            difficulty=request.difficulty.value if request.difficulty else None,
            max_cooking_time=request.max_cooking_time,
            servings=request.servings,
            additional_notes=request.additional_notes
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate recipe. Please try again."
            )
        
        return {
            "recipe": result,
            "suggestions": result.get('suggestions', []),
            "substitutions": result.get('substitutions', [])
        }
        
    except Exception as e:
        logger.error("Recipe generation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Recipe generation failed. Please try again."
        )


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    """Get recipe by ID - placeholder"""
    # TODO: Implement recipe retrieval
    return {
        "id": recipe_id,
        "title": "Sample Recipe",
        "description": "A sample recipe",
        "ingredients": [],
        "instructions": [],
        "cooking_time": 30,
        "prep_time": 15,
        "servings": 4,
        "difficulty": "easy",
        "cuisine": "international",
        "tags": []
    }


@router.post("/{recipe_id}/save")
async def save_recipe(recipe_id: str, user_id: str):
    """Save recipe to user favorites - placeholder"""
    # TODO: Implement recipe saving
    return {"message": "Recipe saved successfully"}


@router.post("/{recipe_id}/rate")
async def rate_recipe(recipe_id: str, rating: int, user_id: str):
    """Rate a recipe - placeholder"""
    # TODO: Implement recipe rating
    return {"message": "Recipe rated successfully"}


@router.get("/ingredients/suggestions")
async def get_ingredient_suggestions(q: str):
    """Get ingredient suggestions for autocomplete"""
    try:
        suggestions = await recipe_service.get_ingredient_suggestions(q)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error("Failed to get ingredient suggestions", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get ingredient suggestions"
        ) 