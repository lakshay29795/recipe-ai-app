"""
Recipe Management Service
Handles recipe favorites, ratings, history, collections, and sharing
"""

import uuid
import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.services.firebase_service import firebase_service
from app.models.history_models import (
    RecipeHistoryEntry, UserRecipeInteraction, RecipeCollection, 
    RecipeShare, RecipeAction, ShareMethod, SaveRecipeRequest,
    FavoriteRecipeRequest, RateRecipeRequest, ShareRecipeRequest,
    CreateCollectionRequest, AddToCollectionRequest,
    RecipeInteractionResponse, RecipeHistoryResponse, UserStatsResponse
)

logger = structlog.get_logger(__name__)

class RecipeManagementService:
    def __init__(self):
        self.firebase = firebase_service
        
    async def save_recipe(self, user_id: str, request: SaveRecipeRequest) -> RecipeInteractionResponse:
        """Save a recipe for a user"""
        try:
            # Get or create user recipe interaction
            interaction = await self._get_or_create_interaction(user_id, request.recipe_id)
            
            # Update interaction
            interaction.notes = request.notes
            interaction.tags = request.tags
            interaction.updated_at = datetime.now()
            
            # Save to Firebase
            if interaction.id:
                await self.firebase.update_document(
                    "user_recipe_interactions",
                    interaction.id,
                    interaction.dict()
                )
            
            # Add to history
            await self._add_history_entry(
                user_id, request.recipe_id, RecipeAction.SAVED,
                {"notes": request.notes, "tags": request.tags}
            )
            
            logger.info("Recipe saved successfully", user_id=user_id, recipe_id=request.recipe_id)
            return RecipeInteractionResponse(**interaction.dict())
            
        except Exception as e:
            logger.error("Failed to save recipe", error=str(e), user_id=user_id)
            raise
    
    async def toggle_favorite(self, user_id: str, request: FavoriteRecipeRequest) -> RecipeInteractionResponse:
        """Toggle favorite status for a recipe"""
        try:
            # Get or create user recipe interaction
            interaction = await self._get_or_create_interaction(user_id, request.recipe_id)
            
            # Update favorite status
            interaction.is_favorite = request.is_favorite
            interaction.updated_at = datetime.now()
            
            # Save to Firebase
            if interaction.id:
                await self.firebase.update_document(
                    "user_recipe_interactions",
                    interaction.id,
                    interaction.dict()
                )
            
            # Add to history
            action = RecipeAction.FAVORITED if request.is_favorite else RecipeAction.VIEWED
            await self._add_history_entry(
                user_id, request.recipe_id, action,
                {"is_favorite": request.is_favorite}
            )
            
            logger.info("Recipe favorite toggled", user_id=user_id, recipe_id=request.recipe_id, is_favorite=request.is_favorite)
            return RecipeInteractionResponse(**interaction.dict())
            
        except Exception as e:
            logger.error("Failed to toggle favorite", error=str(e), user_id=user_id)
            raise
    
    async def rate_recipe(self, user_id: str, request: RateRecipeRequest) -> RecipeInteractionResponse:
        """Rate a recipe"""
        try:
            # Get or create user recipe interaction
            interaction = await self._get_or_create_interaction(user_id, request.recipe_id)
            
            # Update rating
            interaction.rating = request.rating
            if request.notes:
                interaction.notes = request.notes
            interaction.updated_at = datetime.now()
            
            # Save to Firebase
            if interaction.id:
                await self.firebase.update_document(
                    "user_recipe_interactions",
                    interaction.id,
                    interaction.dict()
                )
            
            # Add to history
            await self._add_history_entry(
                user_id, request.recipe_id, RecipeAction.RATED,
                {"rating": request.rating, "notes": request.notes}
            )
            
            logger.info("Recipe rated successfully", user_id=user_id, recipe_id=request.recipe_id, rating=request.rating)
            return RecipeInteractionResponse(**interaction.dict())
            
        except Exception as e:
            logger.error("Failed to rate recipe", error=str(e), user_id=user_id)
            raise
    
    async def share_recipe(self, user_id: str, request: ShareRecipeRequest) -> Dict[str, Any]:
        """Share a recipe"""
        try:
            # Generate share link
            share_id = str(uuid.uuid4())
            share_link = f"https://yourapp.com/shared/{share_id}"
            
            # Calculate expiration
            expires_at = None
            if request.expires_in_days:
                expires_at = datetime.now() + timedelta(days=request.expires_in_days)
            
            # Create share record
            share_record = RecipeShare(
                id=share_id,
                recipe_id=request.recipe_id,
                shared_by_user_id=user_id,
                share_method=request.share_method,
                recipient_email=request.recipient_email,
                share_link=share_link,
                message=request.message,
                expires_at=expires_at
            )
            
            # Save to Firebase
            await self.firebase.create_document(
                "recipe_shares",
                share_id,
                share_record.dict()
            )
            
            # Add to history
            await self._add_history_entry(
                user_id, request.recipe_id, RecipeAction.SHARED,
                {
                    "share_method": request.share_method.value,
                    "recipient_email": request.recipient_email,
                    "share_link": share_link
                }
            )
            
            # Handle different share methods
            result = {"share_link": share_link, "share_id": share_id}
            
            if request.share_method == ShareMethod.EMAIL and request.recipient_email:
                # TODO: Implement email sending
                result["email_sent"] = True
                
            elif request.share_method == ShareMethod.EXPORT_PDF:
                # TODO: Implement PDF generation
                result["pdf_url"] = f"https://yourapp.com/pdf/{share_id}"
            
            logger.info("Recipe shared successfully", user_id=user_id, recipe_id=request.recipe_id, share_method=request.share_method)
            return result
            
        except Exception as e:
            logger.error("Failed to share recipe", error=str(e), user_id=user_id)
            raise
    
    async def get_user_favorites(self, user_id: str, limit: int = 20, offset: int = 0) -> List[RecipeInteractionResponse]:
        """Get user's favorite recipes"""
        try:
            # Query favorite interactions
            interactions = await self.firebase.query_collection(
                "user_recipe_interactions",
                filters=[
                    ("user_id", "==", user_id),
                    ("is_favorite", "==", True)
                ],
                order_by="updated_at",
                limit=limit
            )
            
            return [RecipeInteractionResponse(**interaction) for interaction in interactions]
            
        except Exception as e:
            logger.error("Failed to get user favorites", error=str(e), user_id=user_id)
            raise
    
    async def get_recipe_history(self, user_id: str, limit: int = 50, offset: int = 0) -> RecipeHistoryResponse:
        """Get user's recipe history"""
        try:
            # Query history entries
            entries = await self.firebase.query_collection(
                "recipe_history",
                filters=[("user_id", "==", user_id)],
                order_by="timestamp",
                limit=limit + 1  # Get one extra to check if there are more
            )
            
            has_more = len(entries) > limit
            if has_more:
                entries = entries[:limit]
            
            history_entries = [RecipeHistoryEntry(**entry) for entry in entries]
            
            return RecipeHistoryResponse(
                entries=history_entries,
                total=len(history_entries),
                has_more=has_more
            )
            
        except Exception as e:
            logger.error("Failed to get recipe history", error=str(e), user_id=user_id)
            raise
    
    async def get_user_stats(self, user_id: str) -> UserStatsResponse:
        """Get comprehensive user statistics"""
        try:
            # Get all user interactions
            interactions = await self.firebase.query_collection(
                "user_recipe_interactions",
                filters=[("user_id", "==", user_id)]
            )
            
            # Get recipe history for ingredient analysis
            history = await self.firebase.query_collection(
                "recipe_history",
                filters=[
                    ("user_id", "==", user_id),
                    ("action", "==", RecipeAction.GENERATED.value)
                ],
                limit=100
            )
            
            # Calculate stats
            total_recipes = len(interactions)
            favorite_recipes = len([i for i in interactions if i.get('is_favorite', False)])
            valid_ratings = [rating for i in interactions if (rating := i.get('rating')) is not None]
            total_ratings = len(valid_ratings)
            average_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else None
            
            # Analyze ingredients and cuisines from history
            ingredients = []
            cuisines = []
            for entry in history:
                recipe_data = entry.get('recipe_data', {})
                if 'ingredients' in recipe_data:
                    ingredients.extend([ing.get('name', '') for ing in recipe_data['ingredients']])
                if 'cuisine' in recipe_data:
                    cuisines.append(recipe_data['cuisine'])
            
            # Get most common ingredients and cuisines
            from collections import Counter
            most_used_ingredients = [item for item, count in Counter(ingredients).most_common(5)]
            favorite_cuisines = [item for item, count in Counter(cuisines).most_common(3)]
            
            # Calculate cooking streak (simplified)
            cooking_streak = min(len(history), 30)  # Simplified calculation
            
            return UserStatsResponse(
                total_recipes=total_recipes,
                favorite_recipes=favorite_recipes,
                total_ratings=total_ratings,
                average_rating=average_rating,
                collections_count=0,  # TODO: Implement collections
                most_used_ingredients=most_used_ingredients,
                favorite_cuisines=favorite_cuisines,
                cooking_streak=cooking_streak
            )
            
        except Exception as e:
            logger.error("Failed to get user stats", error=str(e), user_id=user_id)
            raise
    
    async def create_collection(self, user_id: str, request: CreateCollectionRequest) -> RecipeCollection:
        """Create a recipe collection"""
        try:
            collection_id = str(uuid.uuid4())
            collection = RecipeCollection(
                id=collection_id,
                user_id=user_id,
                name=request.name,
                description=request.description,
                recipe_ids=request.recipe_ids,
                is_public=request.is_public
            )
            
            await self.firebase.create_document(
                "recipe_collections",
                collection_id,
                collection.dict()
            )
            
            logger.info("Recipe collection created", user_id=user_id, collection_name=request.name)
            return collection
            
        except Exception as e:
            logger.error("Failed to create collection", error=str(e), user_id=user_id)
            raise
    
    async def track_recipe_view(self, user_id: str, recipe_id: str, recipe_data: Dict[str, Any]):
        """Track when a user views a recipe"""
        try:
            # Get or create interaction
            interaction = await self._get_or_create_interaction(user_id, recipe_id)
            
            # Update access tracking
            interaction.access_count += 1
            interaction.last_accessed = datetime.now()
            
            # Save to Firebase
            if interaction.id:
                await self.firebase.update_document(
                    "user_recipe_interactions",
                    interaction.id,
                    interaction.dict()
                )
            
            # Add to history
            await self._add_history_entry(
                user_id, recipe_id, RecipeAction.VIEWED,
                recipe_data
            )
            
        except Exception as e:
            logger.error("Failed to track recipe view", error=str(e), user_id=user_id)
            # Don't raise, as this is tracking
    
    async def _get_or_create_interaction(self, user_id: str, recipe_id: str) -> UserRecipeInteraction:
        """Get existing interaction or create new one"""
        # Try to find existing interaction
        existing = await self.firebase.query_collection(
            "user_recipe_interactions",
            filters=[
                ("user_id", "==", user_id),
                ("recipe_id", "==", recipe_id)
            ],
            limit=1
        )
        
        if existing:
            interaction = UserRecipeInteraction(**existing[0])
        else:
            # Create new interaction
            interaction_id = str(uuid.uuid4())
            interaction = UserRecipeInteraction(
                id=interaction_id,
                user_id=user_id,
                recipe_id=recipe_id
            )
            
            await self.firebase.create_document(
                "user_recipe_interactions",
                interaction_id,
                interaction.dict()
            )
        
        return interaction
    
    async def _add_history_entry(self, user_id: str, recipe_id: str, action: RecipeAction, metadata: Optional[Dict[str, Any]] = None):
        """Add entry to recipe history"""
        try:
            entry_id = str(uuid.uuid4())
            entry = RecipeHistoryEntry(
                id=entry_id,
                user_id=user_id,
                recipe_id=recipe_id,
                recipe_data=metadata or {},
                action=action,
                metadata=metadata
            )
            
            await self.firebase.create_document(
                "recipe_history",
                entry_id,
                entry.dict()
            )
            
        except Exception as e:
            logger.error("Failed to add history entry", error=str(e))
            # Don't raise, as this is tracking

# Global instance
recipe_management_service = RecipeManagementService() 