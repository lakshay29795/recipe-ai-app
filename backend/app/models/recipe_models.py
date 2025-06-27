"""
Recipe-related models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .common_models import Difficulty, NutritionInfo, TimestampMixin


class RecipeIngredient(BaseModel):
    name: str
    amount: float
    unit: str
    notes: Optional[str] = None


class RecipeStep(BaseModel):
    step_number: int
    instruction: str
    duration: Optional[int] = None  # in minutes
    temperature: Optional[int] = None  # in celsius


class Recipe(TimestampMixin):
    id: Optional[str] = None
    title: str
    description: str
    ingredients: List[RecipeIngredient]
    instructions: List[RecipeStep]
    cooking_time: int  # in minutes
    prep_time: int  # in minutes
    servings: int
    difficulty: Difficulty
    cuisine: str
    tags: List[str] = []
    nutrition_info: Optional[NutritionInfo] = None
    image_url: Optional[str] = None
    user_id: Optional[str] = None
    
    @validator('ingredients')
    def validate_ingredients(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Recipe must have at least one ingredient')
        return v
    
    @validator('instructions')
    def validate_instructions(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Recipe must have at least one instruction')
        return v


class IngredientSubstitution(BaseModel):
    original: str
    substitute: str
    ratio: str
    notes: Optional[str] = None


# Request models
class RecipeGenerationRequest(BaseModel):
    ingredients: List[str]
    additional_notes: Optional[str] = None
    user_id: Optional[str] = None
    preferred_cuisine: Optional[str] = None
    max_cooking_time: Optional[int] = None
    servings: int = 4
    difficulty: Optional[Difficulty] = None


class RecipeUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class RecipeRatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None


# Simple recipe suggestion model for variations
class RecipeSuggestion(BaseModel):
    title: str
    description: str
    key_changes: str


# Response models
class RecipeResponse(BaseModel):
    recipe: Recipe
    suggestions: List[RecipeSuggestion] = []
    substitutions: List[IngredientSubstitution] = []


class RecipeListResponse(BaseModel):
    recipes: List[Recipe]
    total: int
    page: int
    limit: int


class RecipeSummary(BaseModel):
    id: str
    title: str
    description: str
    cooking_time: int
    prep_time: int
    difficulty: Difficulty
    cuisine: str
    tags: List[str]
    image_url: Optional[str] = None
    rating: Optional[float] = None
    created_at: Optional[datetime] = None 