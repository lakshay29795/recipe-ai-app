"""
Common models and enums
"""

from datetime import datetime
from typing import Optional, List, Any, Dict, TypeVar, Generic
from pydantic import BaseModel, Field
from enum import Enum


# Enums
class DietaryRestriction(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten-free"
    DAIRY_FREE = "dairy-free"
    KETO = "keto"
    PALEO = "paleo"
    LOW_CARB = "low-carb"
    LOW_FAT = "low-fat"
    HALAL = "halal"
    KOSHER = "kosher"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SpiceLevel(str, Enum):
    NONE = "none"
    MILD = "mild"
    MEDIUM = "medium"
    HOT = "hot"
    EXTRA_HOT = "extra-hot"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class IngredientCategory(str, Enum):
    PROTEIN = "protein"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    GRAIN = "grain"
    DAIRY = "dairy"
    SPICE = "spice"
    HERB = "herb"
    OIL = "oil"
    CONDIMENT = "condiment"
    OTHER = "other"


# Common response models
T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None


# Nutrition model
class NutritionInfo(BaseModel):
    calories: int
    protein: float
    carbohydrates: float
    fat: float
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None


# Base timestamp model
class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Health check response
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow) 