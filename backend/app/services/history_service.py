"""
History service for user history operations
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
from app.services.firebase_service import firebase_service

logger = structlog.get_logger(__name__)


class HistoryService:
    """Service for user history operations"""
    
    def __init__(self):
        self.collection = "user_history"
    
    async def add_history_entry(self, user_id: str, recipe_id: str, recipe_data: Dict[str, Any]) -> bool:
        """Add a new history entry"""
        try:
            history_id = f"{user_id}_{recipe_id}_{int(datetime.utcnow().timestamp())}"
            
            history_data = {
                "user_id": user_id,
                "recipe_id": recipe_id,
                "recipe_title": recipe_data.get("title", ""),
                "recipe_description": recipe_data.get("description", ""),
                "recipe_image_url": recipe_data.get("image_url"),
                "generated_at": datetime.utcnow(),
                "rating": None,
                "notes": None,
                "is_favorite": False,
                "cooking_attempts": 0,
                "difficulty": recipe_data.get("difficulty", "medium"),
                "cooking_time": recipe_data.get("cooking_time", 0),
                "cuisine": recipe_data.get("cuisine", ""),
                "tags": recipe_data.get("tags", [])
            }
            
            success = await firebase_service.create_document(
                self.collection,
                history_id,
                history_data
            )
            
            if success:
                logger.info("History entry added", user_id=user_id, recipe_id=recipe_id)
            return success
        except Exception as e:
            logger.error("Failed to add history entry", error=str(e), user_id=user_id)
            return False
    
    async def get_user_history(self, user_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get user's recipe history with pagination"""
        try:
            results = await firebase_service.query_collection(
                self.collection,
                filters=[("user_id", "==", user_id)],
                order_by="generated_at",
                limit=limit
            )
            
            total = await firebase_service.get_collection_count(
                self.collection,
                filters=[("user_id", "==", user_id)]
            )
            
            return {
                "items": results,
                "total": total,
                "page": page,
                "limit": limit,
                "has_next": len(results) == limit,
                "has_prev": page > 1
            }
        except Exception as e:
            logger.error("Failed to get user history", error=str(e), user_id=user_id)
            return {"items": [], "total": 0, "page": page, "limit": limit, "has_next": False, "has_prev": False}


# Global history service instance
history_service = HistoryService() 