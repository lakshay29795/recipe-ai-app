"""
User-related models
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .common_models import (
    DietaryRestriction, SkillLevel, SpiceLevel, TimestampMixin
)


class User(TimestampMixin):
    id: str
    email: EmailStr
    display_name: str
    photo_url: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False


class UserPreferences(BaseModel):
    dietary_restrictions: List[DietaryRestriction] = []
    allergies: List[str] = []
    preferred_cuisines: List[str] = []
    cooking_skill_level: SkillLevel = SkillLevel.BEGINNER
    available_equipment: List[str] = []
    spice_level: SpiceLevel = SpiceLevel.MILD


class UserStats(BaseModel):
    recipes_generated: int = 0
    favorite_recipes: int = 0
    cooking_streak: int = 0
    last_activity: Optional[datetime] = None


# Updated UserProfile model to match frontend expectations
class UserProfile(BaseModel):
    uid: str
    email: str
    displayName: str
    photoURL: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    stats: Optional[UserStats] = None
    createdAt: str
    updatedAt: str


# Request models for API
class UserProfileCreate(BaseModel):
    displayName: str
    photoURL: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    createdAt: str
    updatedAt: str


class UserProfileUpdate(BaseModel):
    displayName: Optional[str] = None
    photoURL: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    updatedAt: Optional[str] = None


# Legacy models (keeping for backward compatibility)
class UserProfileLegacy(TimestampMixin):
    user_id: str
    preferences: UserPreferences
    stats: UserStats


# Request/Response models
class UserRegistrationRequest(BaseModel):
    email: EmailStr
    display_name: str
    photo_url: Optional[str] = None


class UserPreferencesUpdateRequest(BaseModel):
    dietary_restrictions: Optional[List[DietaryRestriction]] = None
    allergies: Optional[List[str]] = None
    preferred_cuisines: Optional[List[str]] = None
    cooking_skill_level: Optional[SkillLevel] = None
    available_equipment: Optional[List[str]] = None
    spice_level: Optional[SpiceLevel] = None


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    photo_url: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


class UserProfileResponse(BaseModel):
    user: UserResponse
    preferences: UserPreferences
    stats: UserStats 