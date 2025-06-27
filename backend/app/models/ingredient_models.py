"""
Enhanced Ingredient Models
Ingredient-related models
"""

from typing import Optional, List
from pydantic import BaseModel
from .common_models import IngredientCategory, NutritionInfo, TimestampMixin


class IngredientItem(TimestampMixin):
    id: str
    name: str
    category: IngredientCategory
    common_units: List[str]
    nutrition_per_100g: Optional[NutritionInfo] = None
    aliases: List[str] = []  # Alternative names
    season: Optional[str] = None  # Best season for ingredient
    storage_tips: Optional[str] = None


class IngredientValidation(BaseModel):
    name: str
    is_valid: bool
    suggestions: List[str] = []
    category: Optional[IngredientCategory] = None


# Request models
class IngredientSearchRequest(BaseModel):
    query: str
    category: Optional[IngredientCategory] = None
    limit: int = 20


class IngredientValidationRequest(BaseModel):
    ingredients: List[str]


# Response models
class IngredientSearchResponse(BaseModel):
    items: List[IngredientItem]
    total: int
    query: str


class IngredientValidationResponse(BaseModel):
    validations: List[IngredientValidation]
    valid_count: int
    invalid_count: int


class PopularIngredientsResponse(BaseModel):
    ingredients: List[IngredientItem]
    categories: List[str]


class IngredientCategoriesResponse(BaseModel):
    categories: List[str]
    counts: dict  # category -> count mapping 