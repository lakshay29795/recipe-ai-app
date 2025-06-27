"""
Personalization Engine Service
Tracks user behavior and provides intelligent recommendations
"""

import uuid
import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from app.services.firebase_service import firebase_service

logger = structlog.get_logger(__name__)

class PersonalizationService:
    def __init__(self):
        self.firebase = firebase_service
        
    async def track_user_behavior(self, user_id: str, event_type: str, event_data: Dict[str, Any]):
        """Track user behavior for personalization"""
        try:
            behavior_id = str(uuid.uuid4())
            behavior_event = {
                "id": behavior_id,
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.now().isoformat(),
                "session_id": event_data.get("session_id", ""),
                "device_type": event_data.get("device_type", "web")
            }
            
            await self.firebase.create_document(
                "user_behavior",
                behavior_id,
                behavior_event
            )
            
            # Update user preferences asynchronously
            await self._update_user_preferences(user_id, event_type, event_data)
            
        except Exception as e:
            logger.error("Failed to track user behavior", error=str(e), user_id=user_id)
    
    async def get_personalized_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recipe recommendations for a user"""
        try:
            # Get user preferences and behavior
            user_behavior = await self._get_user_behavior_summary(user_id)
            
            # Generate recommendations based on multiple factors
            recommendations = []
            
            # 1. Cuisine preferences
            cuisine_recommendations = await self._get_cuisine_based_recommendations(
                user_id, user_behavior.get("favorite_cuisines", []), limit // 3
            )
            recommendations.extend(cuisine_recommendations)
            
            # 2. Trending recipes
            trending_recommendations = await self._get_trending_recommendations(limit // 2)
            recommendations.extend(trending_recommendations)
            
            # Remove duplicates and score
            unique_recommendations = self._deduplicate_and_score_recommendations(
                recommendations, user_behavior
            )
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            logger.error("Failed to get personalized recommendations", error=str(e), user_id=user_id)
            return []
    
    async def get_trending_recipes(self, time_period: str = "week", limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending recipes based on user activity"""
        try:
            # Calculate date range
            now = datetime.now()
            if time_period == "day":
                start_date = now - timedelta(days=1)
            elif time_period == "week":
                start_date = now - timedelta(weeks=1)
            elif time_period == "month":
                start_date = now - timedelta(days=30)
            else:
                start_date = now - timedelta(weeks=1)
            
            # Get recent user behavior
            recent_behavior = await self.firebase.query_collection(
                "user_behavior",
                filters=[
                    ("event_type", "in", ["recipe_generated", "recipe_viewed", "recipe_favorited"]),
                    ("timestamp", ">=", start_date.isoformat())
                ]
            )
            
            # Count recipe interactions
            recipe_scores = Counter()
            for behavior in recent_behavior:
                event_data = behavior.get("event_data", {})
                recipe_id = event_data.get("recipe_id")
                if recipe_id:
                    # Weight different actions
                    if behavior.get("event_type") == "recipe_favorited":
                        recipe_scores[recipe_id] += 3
                    elif behavior.get("event_type") == "recipe_generated":
                        recipe_scores[recipe_id] += 2
                    else:  # recipe_viewed
                        recipe_scores[recipe_id] += 1
            
            # Get recipe details for top trending
            trending_recipes = []
            for recipe_id, score in recipe_scores.most_common(limit):
                recipe = await self.firebase.get_document("recipes", recipe_id)
                if recipe:
                    recipe["trending_score"] = score
                    recipe["trend_period"] = time_period
                    trending_recipes.append(recipe)
            
            return trending_recipes
            
        except Exception as e:
            logger.error("Failed to get trending recipes", error=str(e))
            return []
    
    async def _get_user_behavior_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summarized user behavior data"""
        try:
            # Get recent behavior (last 30 days)
            recent_date = (datetime.now() - timedelta(days=30)).isoformat()
            behaviors = await self.firebase.query_collection(
                "user_behavior",
                filters=[
                    ("user_id", "==", user_id),
                    ("timestamp", ">=", recent_date)
                ]
            )
            
            # Analyze behavior patterns
            cuisines = []
            ingredients = []
            difficulties = []
            
            for behavior in behaviors:
                event_data = behavior.get("event_data", {})
                
                if "cuisine" in event_data:
                    cuisines.append(event_data["cuisine"])
                
                if "ingredients" in event_data:
                    ingredients.extend(event_data["ingredients"])
                
                if "difficulty" in event_data:
                    difficulties.append(event_data["difficulty"])
            
            # Get most common preferences
            favorite_cuisines = [item for item, count in Counter(cuisines).most_common(5)]
            frequent_ingredients = [item for item, count in Counter(ingredients).most_common(10)]
            preferred_difficulties = [item for item, count in Counter(difficulties).most_common(3)]
            
            return {
                "favorite_cuisines": favorite_cuisines,
                "frequent_ingredients": frequent_ingredients,
                "preferred_difficulties": preferred_difficulties,
                "total_activities": len(behaviors)
            }
            
        except Exception as e:
            logger.error("Failed to get user behavior summary", error=str(e))
            return {}
    
    async def _get_cuisine_based_recommendations(self, user_id: str, favorite_cuisines: List[str], limit: int) -> List[Dict[str, Any]]:
        """Get recommendations based on user's favorite cuisines"""
        recommendations = []
        
        for cuisine in favorite_cuisines[:3]:  # Top 3 cuisines
            recipes = await self.firebase.query_collection(
                "recipes",
                filters=[("cuisine", "==", cuisine)],
                limit=limit // len(favorite_cuisines[:3]) + 1
            )
            
            for recipe in recipes:
                recipe["recommendation_reason"] = f"Based on your love for {cuisine} cuisine"
                recipe["recommendation_type"] = "cuisine_preference"
                recommendations.append(recipe)
        
        return recommendations
    
    async def _get_trending_recommendations(self, limit: int) -> List[Dict[str, Any]]:
        """Get trending recipe recommendations"""
        trending = await self.get_trending_recipes("week", limit)
        
        for recipe in trending:
            recipe["recommendation_reason"] = "Trending this week"
            recipe["recommendation_type"] = "trending"
        
        return trending
    
    def _deduplicate_and_score_recommendations(self, recommendations: List[Dict[str, Any]], user_behavior: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Remove duplicates and score recommendations"""
        seen_recipes = set()
        unique_recommendations = []
        
        for recipe in recommendations:
            recipe_id = recipe.get("id")
            if recipe_id and recipe_id not in seen_recipes:
                seen_recipes.add(recipe_id)
                
                # Calculate recommendation score
                score = self._calculate_recommendation_score(recipe, user_behavior)
                recipe["recommendation_score"] = score
                
                unique_recommendations.append(recipe)
        
        # Sort by score
        unique_recommendations.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
        
        return unique_recommendations
    
    def _calculate_recommendation_score(self, recipe: Dict[str, Any], user_behavior: Dict[str, Any]) -> float:
        """Calculate recommendation score for a recipe"""
        score = 0.0
        
        # Base score
        score += 1.0
        
        # Cuisine preference boost
        recipe_cuisine = recipe.get("cuisine", "")
        if recipe_cuisine in user_behavior.get("favorite_cuisines", []):
            score += 2.0
        
        # Difficulty preference boost
        recipe_difficulty = recipe.get("difficulty", "")
        if recipe_difficulty in user_behavior.get("preferred_difficulties", []):
            score += 1.0
        
        # Trending boost
        if recipe.get("recommendation_type") == "trending":
            score += 1.5
        
        return score
    
    async def _update_user_preferences(self, user_id: str, event_type: str, event_data: Dict[str, Any]):
        """Update user preferences based on behavior"""
        try:
            # Get current preferences
            user_doc = await self.firebase.get_document("users", user_id)
            if not user_doc:
                return
            
            preferences = user_doc.get("preferences", {})
            
            # Update based on event type
            if event_type == "recipe_generated" and "cuisine" in event_data:
                cuisine_prefs = preferences.get("cuisine_preferences", {})
                cuisine = event_data["cuisine"]
                cuisine_prefs[cuisine] = cuisine_prefs.get(cuisine, 0) + 1
                preferences["cuisine_preferences"] = cuisine_prefs
            
            # Save updated preferences
            await self.firebase.update_document(
                "users",
                user_id,
                {"preferences": preferences}
            )
            
        except Exception as e:
            logger.error("Failed to update user preferences", error=str(e))

# Global instance
personalization_service = PersonalizationService()