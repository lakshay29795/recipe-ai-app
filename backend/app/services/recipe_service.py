"""
Recipe service for recipe-related operations
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
from app.services.firebase_service import firebase_service
from app.services.ai_service import ai_service
from app.models.recipe_models import Recipe, RecipeGenerationRequest
from app.models.common_models import DietaryRestriction, Difficulty

logger = structlog.get_logger(__name__)


class RecipeService:
    """Service for recipe-related operations"""
    
    def __init__(self):
        self.collection = "recipes"
    
    async def create_recipe(self, recipe_data: Dict[str, Any]) -> Optional[Recipe]:
        """Create a new recipe"""
        try:
            recipe_id = recipe_data.get('id')
            if not recipe_id:
                # Generate a unique ID
                recipe_id = f"recipe_{int(datetime.utcnow().timestamp())}"
                recipe_data['id'] = recipe_id
            
            success = await firebase_service.create_document(
                self.collection,
                recipe_id,
                recipe_data
            )
            
            if success:
                logger.info("Recipe created successfully", recipe_id=recipe_id)
                return Recipe(**recipe_data)
            return None
        except Exception as e:
            logger.error("Failed to create recipe", error=str(e))
            return None
    
    async def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get recipe by ID"""
        try:
            recipe_data = await firebase_service.get_document(self.collection, recipe_id)
            if recipe_data:
                return Recipe(**recipe_data)
            return None
        except Exception as e:
            logger.error("Failed to get recipe", error=str(e), recipe_id=recipe_id)
            return None
    
    async def update_recipe(self, recipe_id: str, update_data: Dict[str, Any]) -> bool:
        """Update recipe data"""
        try:
            success = await firebase_service.update_document(
                self.collection,
                recipe_id,
                update_data
            )
            if success:
                logger.info("Recipe updated successfully", recipe_id=recipe_id)
            return success
        except Exception as e:
            logger.error("Failed to update recipe", error=str(e), recipe_id=recipe_id)
            return False
    
    async def delete_recipe(self, recipe_id: str) -> bool:
        """Delete recipe"""
        try:
            success = await firebase_service.delete_document(self.collection, recipe_id)
            if success:
                logger.info("Recipe deleted successfully", recipe_id=recipe_id)
            return success
        except Exception as e:
            logger.error("Failed to delete recipe", error=str(e), recipe_id=recipe_id)
            return False
    
    async def get_user_recipes(self, user_id: str, limit: int = 20) -> List[Recipe]:
        """Get recipes created by a user"""
        try:
            results = await firebase_service.query_collection(
                self.collection,
                filters=[("user_id", "==", user_id)],
                order_by="created_at",
                limit=limit
            )
            
            recipes = []
            for result in results:
                try:
                    recipes.append(Recipe(**result))
                except Exception as e:
                    logger.warning("Invalid recipe data", error=str(e), recipe_id=result.get('id'))
            
            return recipes
        except Exception as e:
            logger.error("Failed to get user recipes", error=str(e), user_id=user_id)
            return []
    
    async def generate_ai_recipe(
        self,
        ingredients: List[str],
        user_id: Optional[str] = None,
        dietary_restrictions: Optional[List[str]] = None,
        cuisine_preference: Optional[str] = None,
        difficulty: Optional[str] = None,
        max_cooking_time: Optional[int] = None,
        servings: int = 4,
        additional_notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate recipe using AI and save to database"""
        try:
            # Convert string restrictions to enum
            restrictions = []
            if dietary_restrictions:
                for restriction in dietary_restrictions:
                    try:
                        restrictions.append(DietaryRestriction(restriction))
                    except ValueError:
                        logger.warning(f"Invalid dietary restriction: {restriction}")
            
            # Convert difficulty to enum
            difficulty_enum = None
            if difficulty:
                try:
                    difficulty_enum = Difficulty(difficulty)
                except ValueError:
                    logger.warning(f"Invalid difficulty: {difficulty}")
            
            # Generate recipe using AI
            recipe_data = await ai_service.generate_recipe(
                ingredients=ingredients,
                dietary_restrictions=restrictions,
                cuisine_preference=cuisine_preference,
                difficulty=difficulty_enum,
                max_cooking_time=max_cooking_time,
                servings=servings,
                additional_notes=additional_notes
            )
            
            if not recipe_data:
                logger.error("AI recipe generation failed")
                return None
            
            # Add user info if provided
            if user_id:
                recipe_data['user_id'] = user_id
                recipe_data['is_public'] = False
            else:
                recipe_data['is_public'] = True
            
            # Generate recipe image
            image_url = await ai_service.generate_recipe_image(
                recipe_title=recipe_data['title'],
                cuisine=recipe_data.get('cuisine'),
                ingredients=ingredients[:3]  # Use first 3 ingredients
            )
            
            if image_url:
                recipe_data['image_url'] = image_url
            
            # Save to database
            saved_recipe = await self.create_recipe(recipe_data)
            
            if saved_recipe:
                logger.info("AI recipe generated and saved", recipe_id=saved_recipe.id, user_id=user_id)
                
                # Convert to dict for response
                result = recipe_data.copy()
                result['suggestions'] = await ai_service.get_recipe_variations(recipe_data)
                result['substitutions'] = recipe_data.get('substitutions', [])
                
                return result
            
            return None
            
        except Exception as e:
            logger.error("Failed to generate AI recipe", error=str(e))
            return None
    
    async def get_ingredient_suggestions(self, partial_ingredient: str) -> List[str]:
        """Get ingredient suggestions for autocomplete"""
        try:
            return await ai_service.get_ingredient_suggestions(partial_ingredient)
        except Exception as e:
            logger.error("Failed to get ingredient suggestions", error=str(e))
            return []
    
    async def search_recipes(
        self,
        query: Optional[str] = None,
        cuisine: Optional[str] = None,
        difficulty: Optional[str] = None,
        max_cooking_time: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Recipe]:
        """Search recipes with filters"""
        try:
            filters = []
            
            if cuisine:
                filters.append(("cuisine", "==", cuisine))
            
            if difficulty:
                filters.append(("difficulty", "==", difficulty))
            
            if max_cooking_time:
                filters.append(("cooking_time", "<=", max_cooking_time))
            
            results = await firebase_service.query_collection(
                self.collection,
                filters=filters if filters else None,
                order_by="created_at",
                limit=limit
            )
            
            recipes = []
            for result in results:
                try:
                    recipe = Recipe(**result)
                    
                    # Filter by tags if provided
                    if tags:
                        recipe_tags = set(recipe.tags)
                        search_tags = set(tags)
                        if not recipe_tags.intersection(search_tags):
                            continue
                    
                    # Simple text search in title and description
                    if query:
                        query_lower = query.lower()
                        if (query_lower not in recipe.title.lower() and 
                            query_lower not in recipe.description.lower()):
                            continue
                    
                    recipes.append(recipe)
                except Exception as e:
                    logger.warning("Invalid recipe data", error=str(e), recipe_id=result.get('id'))
            
            return recipes
        except Exception as e:
            logger.error("Failed to search recipes", error=str(e))
            return []


# Global recipe service instance
recipe_service = RecipeService() 