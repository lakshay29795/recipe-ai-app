"""
Smart Ingredient Service
Handles ingredient autocomplete, suggestions, nutritional analysis, and shopping lists
"""

import uuid
import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.firebase_service import firebase_service
from app.models.ingredient_models import (
    IngredientItem, IngredientValidation, IngredientSearchRequest,
    IngredientValidationRequest, IngredientSearchResponse, IngredientValidationResponse,
    PopularIngredientsResponse, IngredientCategoriesResponse
)
from app.models.common_models import IngredientCategory
import json
from collections import Counter

logger = structlog.get_logger(__name__)

class IngredientService:
    """Service for ingredient-related operations"""
    
    def __init__(self):
        self.collection = "ingredients"
    
    async def search_ingredients(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search ingredients by name"""
        try:
            # For now, return a simple static list
            # TODO: Implement proper ingredient search
            common_ingredients = [
                {"id": "1", "name": "chicken", "category": "protein", "common_units": ["lb", "kg", "piece"]},
                {"id": "2", "name": "rice", "category": "grain", "common_units": ["cup", "kg", "lb"]},
                {"id": "3", "name": "tomato", "category": "vegetable", "common_units": ["piece", "cup", "kg"]},
                {"id": "4", "name": "onion", "category": "vegetable", "common_units": ["piece", "cup", "kg"]},
                {"id": "5", "name": "garlic", "category": "vegetable", "common_units": ["clove", "head", "tsp"]},
                {"id": "6", "name": "olive oil", "category": "oil", "common_units": ["tbsp", "cup", "ml"]},
                {"id": "7", "name": "salt", "category": "spice", "common_units": ["tsp", "tbsp", "pinch"]},
                {"id": "8", "name": "pepper", "category": "spice", "common_units": ["tsp", "tbsp", "pinch"]},
            ]
            
            # Simple search filter
            query_lower = query.lower()
            filtered_ingredients = [
                ingredient for ingredient in common_ingredients
                if query_lower in ingredient["name"].lower()
            ]
            
            return filtered_ingredients[:limit]
        except Exception as e:
            logger.error("Failed to search ingredients", error=str(e), query=query)
            return []
    
    async def get_ingredient_categories(self) -> List[str]:
        """Get all ingredient categories"""
        try:
            return [
                "protein", "vegetable", "fruit", "grain", "dairy", 
                "spice", "herb", "oil", "condiment", "other"
            ]
        except Exception as e:
            logger.error("Failed to get ingredient categories", error=str(e))
            return []
    
    async def get_popular_ingredients(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular ingredients"""
        try:
            # Return common ingredients for now
            popular_ingredients = [
                {"name": "chicken", "category": "protein"},
                {"name": "rice", "category": "grain"},
                {"name": "tomato", "category": "vegetable"},
                {"name": "onion", "category": "vegetable"},
                {"name": "garlic", "category": "vegetable"},
                {"name": "olive oil", "category": "oil"},
                {"name": "salt", "category": "spice"},
                {"name": "pepper", "category": "spice"},
                {"name": "cheese", "category": "dairy"},
                {"name": "pasta", "category": "grain"},
            ]
            
            return popular_ingredients[:limit]
        except Exception as e:
            logger.error("Failed to get popular ingredients", error=str(e))
            return []
    
    async def validate_ingredients(self, ingredients: List[str]) -> Dict[str, Any]:
        """Validate ingredient list"""
        try:
            # For now, assume all ingredients are valid
            # TODO: Implement proper ingredient validation
            return {
                "valid": ingredients,
                "invalid": [],
                "suggestions": []
            }
        except Exception as e:
            logger.error("Failed to validate ingredients", error=str(e))
            return {"valid": [], "invalid": ingredients, "suggestions": []}
    
    async def get_ingredient_suggestions(self, existing_ingredients: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Get smart ingredient suggestions based on existing ingredients"""
        try:
            # Common ingredient pairings
            pairings = {
                "chicken": ["garlic", "onion", "herbs", "lemon"],
                "tomato": ["basil", "garlic", "onion", "olive oil"],
                "pasta": ["garlic", "olive oil", "parmesan", "herbs"],
                "rice": ["soy sauce", "ginger", "garlic", "vegetables"],
                "beef": ["onion", "garlic", "herbs", "wine"],
                "fish": ["lemon", "herbs", "garlic", "butter"]
            }
            
            suggestions = []
            for ingredient in existing_ingredients:
                if ingredient.lower() in pairings:
                    for suggested in pairings[ingredient.lower()]:
                        if suggested not in [ing.lower() for ing in existing_ingredients]:
                            suggestions.append({
                                "name": suggested,
                                "reason": f"Pairs well with {ingredient}",
                                "category": "complementary"
                            })
            
            # Remove duplicates and limit
            unique_suggestions = []
            seen = set()
            for suggestion in suggestions:
                if suggestion["name"] not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(suggestion["name"])
                    if len(unique_suggestions) >= limit:
                        break
            
            return unique_suggestions
            
        except Exception as e:
            logger.error("Failed to get ingredient suggestions", error=str(e))
            return []
    
    async def create_shopping_list_from_recipes(self, user_id: str, recipe_ids: List[str], list_name: str) -> Dict[str, Any]:
        """Create a shopping list from multiple recipes"""
        try:
            shopping_list_id = str(uuid.uuid4())
            all_ingredients = {}
            
            # Collect ingredients from all recipes
            for recipe_id in recipe_ids:
                recipe = await firebase_service.get_document("recipes", recipe_id)
                if recipe and "ingredients" in recipe:
                    for ingredient in recipe["ingredients"]:
                        name = ingredient.get("name", "").lower()
                        quantity = ingredient.get("quantity", 1)
                        unit = ingredient.get("unit", "piece")
                        
                        if name in all_ingredients:
                            # Simple quantity addition (in production, handle unit conversions)
                            if all_ingredients[name]["unit"] == unit:
                                all_ingredients[name]["quantity"] += quantity
                        else:
                            all_ingredients[name] = {
                                "name": ingredient.get("name", ""),
                                "quantity": quantity,
                                "unit": unit,
                                "category": ingredient.get("category", "other")
                            }
            
            # Create shopping list document
            shopping_list = {
                "id": shopping_list_id,
                "user_id": user_id,
                "name": list_name,
                "items": list(all_ingredients.values()),
                "created_from_recipes": recipe_ids,
                "created_at": datetime.now().isoformat(),
                "is_completed": False
            }
            
            # Save to Firebase
            await firebase_service.create_document(
                "shopping_lists",
                shopping_list_id,
                shopping_list
            )
            
            logger.info("Shopping list created from recipes", 
                       user_id=user_id, recipe_count=len(recipe_ids))
            return shopping_list
            
        except Exception as e:
            logger.error("Failed to create shopping list from recipes", error=str(e))
            raise
    
    async def get_seasonal_ingredients(self, month: str) -> List[Dict[str, Any]]:
        """Get ingredients that are in season for the specified month"""
        try:
            # Seasonal ingredient data (simplified)
            seasonal_data = {
                "january": ["citrus", "winter squash", "cabbage", "kale"],
                "february": ["citrus", "winter squash", "cabbage", "kale"],
                "march": ["asparagus", "artichokes", "spring onions", "peas"],
                "april": ["asparagus", "artichokes", "spring onions", "peas"],
                "may": ["strawberries", "asparagus", "spring greens", "radishes"],
                "june": ["berries", "tomatoes", "zucchini", "corn"],
                "july": ["berries", "tomatoes", "zucchini", "corn", "stone fruits"],
                "august": ["tomatoes", "corn", "stone fruits", "melons"],
                "september": ["apples", "pears", "winter squash", "root vegetables"],
                "october": ["apples", "pears", "winter squash", "root vegetables"],
                "november": ["winter squash", "root vegetables", "cranberries", "pomegranates"],
                "december": ["winter squash", "root vegetables", "citrus", "pomegranates"]
            }
            
            month_lower = month.lower()
            if month_lower in seasonal_data:
                ingredients = []
                for ingredient_name in seasonal_data[month_lower]:
                    ingredients.append({
                        "name": ingredient_name,
                        "category": "seasonal",
                        "month": month,
                        "peak_season": True
                    })
                return ingredients
            
            return []
            
        except Exception as e:
            logger.error("Failed to get seasonal ingredients", error=str(e))
            return []
    
    async def calculate_recipe_nutrition(self, ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic nutritional information for a recipe"""
        try:
            # Simplified nutritional calculation
            # In production, this would use a comprehensive nutritional database
            
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            # Basic nutritional values per 100g for common ingredients
            nutrition_db = {
                "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
                "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
                "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
                "onion": {"calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1},
                "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100}
            }
            
            for ingredient in ingredients:
                name = ingredient.get("name", "").lower()
                quantity = ingredient.get("quantity", 1)
                
                if name in nutrition_db:
                    # Simplified calculation assuming 100g per "piece" or "cup"
                    nutrition = nutrition_db[name]
                    factor = quantity * 0.5  # Rough estimate
                    
                    total_calories += nutrition["calories"] * factor
                    total_protein += nutrition["protein"] * factor
                    total_carbs += nutrition["carbs"] * factor
                    total_fat += nutrition["fat"] * factor
            
            return {
                "total_calories": round(total_calories),
                "total_protein": round(total_protein, 1),
                "total_carbohydrates": round(total_carbs, 1),
                "total_fat": round(total_fat, 1),
                "servings": 4,  # Default assumption
                "calories_per_serving": round(total_calories / 4) if total_calories > 0 else 0
            }
            
        except Exception as e:
            logger.error("Failed to calculate recipe nutrition", error=str(e))
            return {
                "total_calories": 0,
                "total_protein": 0,
                "total_carbohydrates": 0,
                "total_fat": 0,
                "servings": 4,
                "calories_per_serving": 0
            }


# Global ingredient service instance
ingredient_service = IngredientService() 