"""
User service for user-related operations
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
from app.services.firebase_service import firebase_service
from app.models.user_models import User, UserProfile, UserPreferences, UserStats

logger = structlog.get_logger(__name__)


class UserService:
    """Service for user-related operations"""
    
    def __init__(self):
        self.collection = "users"
        self.profiles_collection = "user_profiles"
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """Create a new user"""
        try:
            user_id = user_data.get('id')
            if not user_id:
                logger.error("User ID is required")
                return None
            
            # Create user document
            success = await firebase_service.create_document(
                self.collection, 
                user_id, 
                user_data
            )
            
            if success:
                # Create default user profile
                default_profile = {
                    "user_id": user_id,
                    "preferences": {
                        "dietary_restrictions": [],
                        "allergies": [],
                        "preferred_cuisines": [],
                        "cooking_skill_level": "beginner",
                        "available_equipment": [],
                        "spice_level": "mild"
                    },
                    "stats": {
                        "recipes_generated": 0,
                        "favorite_recipes": 0,
                        "cooking_streak": 0,
                        "last_activity": None
                    }
                }
                
                await firebase_service.create_document(
                    self.profiles_collection,
                    user_id,
                    default_profile
                )
                
                logger.info("User created successfully", user_id=user_id)
                return User(**user_data)
            
            return None
        except Exception as e:
            logger.error("Failed to create user", error=str(e), user_id=user_data.get('id'))
            return None
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user_data = await firebase_service.get_document(self.collection, user_id)
            if user_data:
                return User(**user_data)
            return None
        except Exception as e:
            logger.error("Failed to get user", error=str(e), user_id=user_id)
            return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            success = await firebase_service.update_document(
                self.collection,
                user_id,
                update_data
            )
            if success:
                logger.info("User updated successfully", user_id=user_id)
            return success
        except Exception as e:
            logger.error("Failed to update user", error=str(e), user_id=user_id)
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user and related data"""
        try:
            # Delete user profile first
            await firebase_service.delete_document(self.profiles_collection, user_id)
            
            # Delete user document
            success = await firebase_service.delete_document(self.collection, user_id)
            
            if success:
                logger.info("User deleted successfully", user_id=user_id)
            return success
        except Exception as e:
            logger.error("Failed to delete user", error=str(e), user_id=user_id)
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile with preferences and stats"""
        try:
            profile_data = await firebase_service.get_document(
                self.profiles_collection, 
                user_id
            )
            if profile_data:
                return UserProfile(**profile_data)
            return None
        except Exception as e:
            logger.error("Failed to get user profile", error=str(e), user_id=user_id)
            return None
    
    async def update_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences"""
        try:
            update_data = {
                "preferences": preferences,
                "updated_at": datetime.utcnow()
            }
            
            success = await firebase_service.update_document(
                self.profiles_collection,
                user_id,
                update_data
            )
            
            if success:
                logger.info("User preferences updated", user_id=user_id)
            return success
        except Exception as e:
            logger.error("Failed to update preferences", error=str(e), user_id=user_id)
            return False
    
    async def update_user_stats(self, user_id: str, stats_update: Dict[str, Any]) -> bool:
        """Update user statistics"""
        try:
            # Get current profile to merge stats
            profile = await self.get_user_profile(user_id)
            if not profile:
                return False
            
            # Merge stats
            current_stats = profile.stats.dict()
            current_stats.update(stats_update)
            current_stats["last_activity"] = datetime.utcnow()
            
            update_data = {
                "stats": current_stats,
                "updated_at": datetime.utcnow()
            }
            
            success = await firebase_service.update_document(
                self.profiles_collection,
                user_id,
                update_data
            )
            
            if success:
                logger.info("User stats updated", user_id=user_id)
            return success
        except Exception as e:
            logger.error("Failed to update user stats", error=str(e), user_id=user_id)
            return False
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            results = await firebase_service.query_collection(
                self.collection,
                filters=[("email", "==", email)],
                limit=1
            )
            
            if results:
                return User(**results[0])
            return None
        except Exception as e:
            logger.error("Failed to get user by email", error=str(e), email=email)
            return None


# Global user service instance
user_service = UserService() 