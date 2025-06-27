"""
Enhanced Ingredients API routes with smart features
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.core.auth import get_current_user
from app.services.ingredient_service import ingredient_service

router = APIRouter()


class IngredientItem(BaseModel):
    id: str
    name: str
    category: str
    common_units: List[str]


class IngredientSearchResponse(BaseModel):
    items: List[IngredientItem]
    total: int


@router.get("/search", response_model=IngredientSearchResponse)
async def search_ingredients(q: str, limit: int = 20):
    """Search ingredients by name with smart fuzzy matching"""
    try:
        results = await ingredient_service.search_ingredients(q, limit)
        items = [
            IngredientItem(
                id=str(i),
                name=result["name"],
                category=result["category"],
                common_units=result.get("common_units", [])
            )
            for i, result in enumerate(results)
        ]
        return IngredientSearchResponse(items=items, total=len(items))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/categories")
async def get_ingredient_categories():
    """Get all ingredient categories - placeholder"""
    # TODO: Implement category retrieval
    return {
        "categories": [
            "protein", "vegetable", "fruit", "grain", "dairy", 
            "spice", "herb", "oil", "condiment", "other"
        ]
    }


@router.get("/popular")
async def get_popular_ingredients():
    """Get popular ingredients - placeholder"""
    # TODO: Implement popular ingredients retrieval
    return {
        "ingredients": [
            {"name": "chicken", "category": "protein"},
            {"name": "rice", "category": "grain"},
            {"name": "tomato", "category": "vegetable"}
        ]
    }


@router.post("/validate")
async def validate_ingredients(ingredients: List[str]):
    """Validate ingredient list"""
    try:
        return await ingredient_service.validate_ingredients(ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/suggestions")
async def get_ingredient_suggestions(
    existing_ingredients: List[str],
    limit: int = 5
):
    """Get smart ingredient suggestions based on existing ingredients"""
    try:
        return await ingredient_service.get_ingredient_suggestions(existing_ingredients, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/seasonal/{month}")
async def get_seasonal_ingredients(month: str):
    """Get ingredients that are in season for the specified month"""
    try:
        return await ingredient_service.get_seasonal_ingredients(month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get seasonal ingredients: {str(e)}")

@router.post("/shopping-list")
async def create_shopping_list(
    recipe_ids: List[str],
    list_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Create a shopping list from multiple recipes"""
    try:
        return await ingredient_service.create_shopping_list_from_recipes(
            current_user["uid"], recipe_ids, list_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create shopping list: {str(e)}")

@router.post("/nutrition-analysis")
async def calculate_recipe_nutrition(ingredients: List[Dict[str, Any]]):
    """Calculate nutritional information for a list of ingredients"""
    try:
        return await ingredient_service.calculate_recipe_nutrition(ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate nutrition: {str(e)}") 