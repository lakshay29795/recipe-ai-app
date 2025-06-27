"""
Cache Service for Performance Optimization
Implements in-memory and Redis caching strategies
"""

import json
import hashlib
import structlog
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from functools import wraps
import asyncio

logger = structlog.get_logger(__name__)

class CacheService:
    def __init__(self):
        # In-memory cache for development
        self._memory_cache = {}
        self._cache_timestamps = {}
        self._default_ttl = 300  # 5 minutes
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Check if key exists and is not expired
            if key in self._memory_cache:
                timestamp = self._cache_timestamps.get(key)
                if timestamp and datetime.now() < timestamp:
                    logger.debug("Cache hit", key=key)
                    return self._memory_cache[key]
                else:
                    # Expired, remove from cache
                    await self.delete(key)
            
            logger.debug("Cache miss", key=key)
            return None
            
        except Exception as e:
            logger.error("Failed to get from cache", error=str(e), key=key)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            if ttl is None:
                ttl = self._default_ttl
            
            # Store value and expiration time
            self._memory_cache[key] = value
            self._cache_timestamps[key] = datetime.now() + timedelta(seconds=ttl)
            
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
            
        except Exception as e:
            logger.error("Failed to set cache", error=str(e), key=key)
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self._memory_cache:
                del self._memory_cache[key]
            if key in self._cache_timestamps:
                del self._cache_timestamps[key]
            
            logger.debug("Cache deleted", key=key)
            return True
            
        except Exception as e:
            logger.error("Failed to delete from cache", error=str(e), key=key)
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            self._memory_cache.clear()
            self._cache_timestamps.clear()
            logger.info("Cache cleared")
            return True
            
        except Exception as e:
            logger.error("Failed to clear cache", error=str(e))
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            current_time = datetime.now()
            active_keys = 0
            expired_keys = 0
            
            for key, timestamp in self._cache_timestamps.items():
                if current_time < timestamp:
                    active_keys += 1
                else:
                    expired_keys += 1
            
            return {
                "total_keys": len(self._memory_cache),
                "active_keys": active_keys,
                "expired_keys": expired_keys,
                "cache_type": "memory"
            }
            
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {}
    
    def generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Create a consistent key from parameters
        key_parts = [prefix]
        
        # Sort kwargs for consistent key generation
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (dict, list)):
                v = json.dumps(v, sort_keys=True)
            key_parts.append(f"{k}:{v}")
        
        key_string = "|".join(key_parts)
        
        # Hash long keys to keep them manageable
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_string

# Cache decorators
def cache_result(ttl: int = 300, key_prefix: str = "default"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service.generate_key(
                f"{key_prefix}:{func.__name__}",
                args=str(args),
                kwargs=kwargs
            )
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def cache_user_data(ttl: int = 600):  # 10 minutes for user data
    """Decorator specifically for user data caching"""
    return cache_result(ttl=ttl, key_prefix="user_data")

def cache_recipe_data(ttl: int = 1800):  # 30 minutes for recipe data
    """Decorator specifically for recipe data caching"""
    return cache_result(ttl=ttl, key_prefix="recipe_data")

def cache_ingredient_data(ttl: int = 3600):  # 1 hour for ingredient data
    """Decorator specifically for ingredient data caching"""
    return cache_result(ttl=ttl, key_prefix="ingredient_data")

# Advanced caching strategies
class SmartCacheService(CacheService):
    def __init__(self):
        super().__init__()
        self._access_counts = {}
        self._max_memory_items = 1000
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Enhanced set with LRU eviction"""
        try:
            # Check if we need to evict items
            if len(self._memory_cache) >= self._max_memory_items:
                await self._evict_lru_items()
            
            # Set the value
            result = await super().set(key, value, ttl)
            
            # Track access
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            
            return result
            
        except Exception as e:
            logger.error("Failed to set cache with LRU", error=str(e), key=key)
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Enhanced get with access tracking"""
        result = await super().get(key)
        
        if result is not None:
            # Track access for LRU
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
        
        return result
    
    async def _evict_lru_items(self, evict_count: int = 100):
        """Evict least recently used items"""
        try:
            # Sort by access count (ascending) to get LRU items
            sorted_items = sorted(
                self._access_counts.items(),
                key=lambda x: x[1]
            )
            
            # Evict the least used items
            for key, _ in sorted_items[:evict_count]:
                await self.delete(key)
                if key in self._access_counts:
                    del self._access_counts[key]
            
            logger.info("Evicted LRU cache items", count=evict_count)
            
        except Exception as e:
            logger.error("Failed to evict LRU items", error=str(e))

# Cache warming strategies
class CacheWarmer:
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        
    async def warm_popular_recipes(self):
        """Pre-cache popular recipes"""
        try:
            from app.services.firebase_service import firebase_service
            
            # Get popular recipes (this would be based on user behavior)
            popular_recipes = await firebase_service.query_collection(
                "recipes",
                limit=50  # Cache top 50 recipes
            )
            
            # Cache each recipe
            for recipe in popular_recipes:
                cache_key = self.cache.generate_key("recipe", id=recipe.get("id"))
                await self.cache.set(cache_key, recipe, ttl=1800)  # 30 minutes
            
            logger.info("Warmed popular recipes cache", count=len(popular_recipes))
            
        except Exception as e:
            logger.error("Failed to warm popular recipes cache", error=str(e))
    
    async def warm_ingredient_data(self):
        """Pre-cache ingredient data"""
        try:
            from app.services.firebase_service import firebase_service
            
            # Get all ingredients
            ingredients = await firebase_service.query_collection("ingredients")
            
            # Cache ingredients
            cache_key = self.cache.generate_key("all_ingredients")
            await self.cache.set(cache_key, ingredients, ttl=3600)  # 1 hour
            
            logger.info("Warmed ingredients cache", count=len(ingredients))
            
        except Exception as e:
            logger.error("Failed to warm ingredients cache", error=str(e))
    
    async def warm_user_preferences(self, user_id: str):
        """Pre-cache user preferences and behavior"""
        try:
            from app.services.personalization_service import personalization_service
            
            # Get user behavior summary
            behavior_summary = await personalization_service._get_user_behavior_summary(user_id)
            
            # Cache user behavior
            cache_key = self.cache.generate_key("user_behavior", user_id=user_id)
            await self.cache.set(cache_key, behavior_summary, ttl=600)  # 10 minutes
            
            logger.info("Warmed user preferences cache", user_id=user_id)
            
        except Exception as e:
            logger.error("Failed to warm user preferences cache", error=str(e))

# Response compression
class ResponseCompressor:
    @staticmethod
    def should_compress(data: Any, min_size: int = 1024) -> bool:
        """Check if data should be compressed"""
        try:
            data_size = len(json.dumps(data))
            return data_size > min_size
        except:
            return False
    
    @staticmethod
    def compress_response(data: Any) -> Dict[str, Any]:
        """Compress response data (simplified)"""
        try:
            # In production, you'd use actual compression like gzip
            # For now, we'll just optimize the data structure
            
            if isinstance(data, dict):
                # Remove null values
                compressed = {k: v for k, v in data.items() if v is not None}
                
                # Optimize recipe data
                if "ingredients" in compressed:
                    ingredients = compressed["ingredients"]
                    if isinstance(ingredients, list):
                        # Remove unnecessary fields from ingredients
                        optimized_ingredients = []
                        for ing in ingredients:
                            if isinstance(ing, dict):
                                optimized_ing = {
                                    "name": ing.get("name"),
                                    "quantity": ing.get("quantity"),
                                    "unit": ing.get("unit")
                                }
                                optimized_ingredients.append(optimized_ing)
                        compressed["ingredients"] = optimized_ingredients
                
                return compressed
            
            return data
            
        except Exception as e:
            logger.error("Failed to compress response", error=str(e))
            return data

# Global instances
cache_service = SmartCacheService()
cache_warmer = CacheWarmer(cache_service)
response_compressor = ResponseCompressor() 