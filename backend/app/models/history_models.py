"""
Recipe history and favorites models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from .common_models import TimestampMixin
from .recipe_models import Recipe


class RecipeAction(str, Enum):
    GENERATED = "generated"
    SAVED = "saved"
    FAVORITED = "favorited"
    SHARED = "shared"
    RATED = "rated"
    VIEWED = "viewed"


class ShareMethod(str, Enum):
    LINK = "link"
    EMAIL = "email"
    SOCIAL = "social"
    EXPORT_PDF = "export_pdf"
    PRINT = "print"


class RecipeHistoryEntry(BaseModel):
    id: Optional[str] = None
    user_id: str
    recipe_id: str
    recipe_data: Dict[str, Any]  # Full recipe object
    action: RecipeAction
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None  # Additional context


class UserRecipeInteraction(BaseModel):
    id: Optional[str] = None
    user_id: str
    recipe_id: str
    is_favorite: bool = False
    rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 stars
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class RecipeCollection(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str
    description: Optional[str] = None
    recipe_ids: List[str] = Field(default_factory=list)
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class RecipeShare(BaseModel):
    id: Optional[str] = None
    recipe_id: str
    shared_by_user_id: str
    share_method: ShareMethod
    recipient_email: Optional[str] = None
    share_link: Optional[str] = None
    message: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)


# Request models
class SaveRecipeRequest(BaseModel):
    recipe_id: str
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class FavoriteRecipeRequest(BaseModel):
    recipe_id: str
    is_favorite: bool = True


class RateRecipeRequest(BaseModel):
    recipe_id: str
    rating: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None


class ShareRecipeRequest(BaseModel):
    recipe_id: str
    share_method: ShareMethod
    recipient_email: Optional[str] = None
    message: Optional[str] = None
    expires_in_days: Optional[int] = 7


class CreateCollectionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    recipe_ids: List[str] = Field(default_factory=list)
    is_public: bool = False


class AddToCollectionRequest(BaseModel):
    collection_id: str
    recipe_id: str


# Response models
class RecipeInteractionResponse(BaseModel):
    recipe_id: str
    is_favorite: bool
    rating: Optional[int]
    notes: Optional[str]
    tags: List[str]
    access_count: int
    last_accessed: datetime


class RecipeHistoryResponse(BaseModel):
    entries: List[RecipeHistoryEntry]
    total: int
    has_more: bool


class UserStatsResponse(BaseModel):
    total_recipes: int
    favorite_recipes: int
    total_ratings: int
    average_rating: Optional[float]
    collections_count: int
    most_used_ingredients: List[str]
    favorite_cuisines: List[str]
    cooking_streak: int


class UserHistory(TimestampMixin):
    id: str
    user_id: str
    recipe_id: str
    recipe: Optional[Recipe] = None  # Can be populated when needed
    generated_at: datetime
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    is_favorite: bool = False
    cooking_attempts: int = 0
    last_cooked: Optional[datetime] = None


class HistoryEntry(BaseModel):
    id: str
    user_id: str
    recipe_id: str
    recipe_title: str
    recipe_description: str
    recipe_image_url: Optional[str] = None
    generated_at: datetime
    rating: Optional[int] = None
    notes: Optional[str] = None
    is_favorite: bool = False
    cooking_attempts: int = 0
    difficulty: str
    cooking_time: int
    cuisine: str
    tags: List[str] = []


# Request models
class HistoryFilterRequest(BaseModel):
    user_id: str
    favorites_only: bool = False
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    rating_min: Optional[int] = Field(None, ge=1, le=5)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    limit: int = 20


class HistoryUpdateRequest(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None
    cooking_attempts: Optional[int] = None


class FavoriteToggleRequest(BaseModel):
    recipe_id: str
    is_favorite: bool


# Response models
class HistoryResponse(BaseModel):
    items: List[HistoryEntry]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class HistoryStatsResponse(BaseModel):
    total_recipes: int
    favorite_recipes: int
    average_rating: Optional[float] = None
    most_common_cuisine: Optional[str] = None
    cooking_streak: int
    recipes_this_month: int
    total_cooking_time: int  # in minutes 