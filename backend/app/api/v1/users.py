"""
Users API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import structlog
from app.core.auth import get_current_user, require_user_access
from app.services.user_service import user_service
from app.models.user_models import (
    UserResponse, 
    UserProfileResponse, 
    UserPreferencesUpdateRequest,
    UserProfile,
    UserProfileCreate,
    UserProfileUpdate
)
from app.services.firebase_service import FirebaseService
from app.models.common_models import ApiResponse

logger = structlog.get_logger(__name__)
router = APIRouter()

firebase_service = FirebaseService()


class UserUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    photo_url: Optional[str] = None


class MessageResponse(BaseModel):
    message: str


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user profile with preferences and stats"""
    try:
        # Check permissions
        await require_user_access(current_user, user_id)
        
        # Get user profile
        profile = await user_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Get user basic info
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfileResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                photo_url=user.photo_url,
                is_active=user.is_active,
                created_at=user.created_at
            ),
            preferences=profile.preferences,
            stats=profile.stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user profile", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.put("/profile/{user_id}", response_model=MessageResponse)
async def update_user_profile(
    user_id: str,
    update_data: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user basic profile information"""
    try:
        # Check permissions
        await require_user_access(current_user, user_id)
        
        # Prepare update data
        update_dict = {}
        if update_data.display_name is not None:
            update_dict["display_name"] = update_data.display_name
        if update_data.photo_url is not None:
            update_dict["photo_url"] = update_data.photo_url
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        # Update user
        success = await user_service.update_user(user_id, update_dict)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
        
        logger.info("User profile updated", user_id=user_id)
        return MessageResponse(message="Profile updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update user profile", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.get("/preferences/{user_id}")
async def get_user_preferences(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user preferences"""
    try:
        # Check permissions
        await require_user_access(current_user, user_id)
        
        # Get user profile
        profile = await user_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return profile.preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user preferences", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user preferences"
        )


@router.put("/preferences/{user_id}", response_model=MessageResponse)
async def update_user_preferences(
    user_id: str,
    preferences: UserPreferencesUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        # Check permissions
        await require_user_access(current_user, user_id)
        
        # Prepare preferences update
        preferences_dict = {}
        if preferences.dietary_restrictions is not None:
            preferences_dict["dietary_restrictions"] = preferences.dietary_restrictions
        if preferences.allergies is not None:
            preferences_dict["allergies"] = preferences.allergies
        if preferences.preferred_cuisines is not None:
            preferences_dict["preferred_cuisines"] = preferences.preferred_cuisines
        if preferences.cooking_skill_level is not None:
            preferences_dict["cooking_skill_level"] = preferences.cooking_skill_level
        if preferences.available_equipment is not None:
            preferences_dict["available_equipment"] = preferences.available_equipment
        if preferences.spice_level is not None:
            preferences_dict["spice_level"] = preferences.spice_level
        
        if not preferences_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No preferences data provided"
            )
        
        # Update preferences
        success = await user_service.update_user_preferences(user_id, preferences_dict)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences"
            )
        
        logger.info("User preferences updated", user_id=user_id)
        return MessageResponse(message="Preferences updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update user preferences", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences"
        )


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user statistics"""
    try:
        # Check permissions
        await require_user_access(current_user, user_id)
        
        # Get user profile
        profile = await user_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return profile.stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user stats", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user stats"
        )


@router.delete("/account/{user_id}", response_model=MessageResponse)
async def delete_user_account(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete user account and all associated data"""
    try:
        # Check permissions
        await require_user_access(current_user, user_id)
        
        # Delete user account
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user account"
            )
        
        logger.info("User account deleted", user_id=user_id)
        return MessageResponse(message="Account deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete user account", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )


@router.post("/profile")
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new user profile"""
    try:
        logger.info("Creating user profile", uid=current_user["uid"])
        
        # Prepare profile data
        profile_dict = {
            "uid": current_user["uid"],
            "email": current_user.get("email", ""),
            "displayName": profile_data.displayName,
            "photoURL": profile_data.photoURL,
            "preferences": profile_data.preferences.dict() if profile_data.preferences else None,
            "stats": {
                "recipesGenerated": 0,
                "favoriteRecipes": 0,
                "cookingStreak": 0
            },
            "createdAt": profile_data.createdAt,
            "updatedAt": profile_data.updatedAt
        }
        
        # Save to Firebase
        doc_ref = firebase_service.create_document("users", current_user["uid"], profile_dict)
        
        # Return the created profile
        created_profile = UserProfile(**profile_dict)
        
        logger.info("User profile created successfully", uid=current_user["uid"])
        return ApiResponse(
            success=True,
            data=created_profile,
            message="User profile created successfully"
        )
        
    except Exception as e:
        logger.error("Failed to create user profile", uid=current_user["uid"], error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create user profile: {str(e)}")


@router.get("/profile/{uid}")
async def get_user_profile_by_uid(
    uid: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user profile by UID"""
    try:
        logger.info("Getting user profile", uid=uid)
        
        # Check if user is requesting their own profile or has permission
        if current_user["uid"] != uid:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get profile from Firebase
        profile_data = firebase_service.get_document("users", uid)
        
        if not profile_data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile = UserProfile(**profile_data)
        
        logger.info("User profile retrieved successfully", uid=uid)
        return ApiResponse(
            success=True,
            data=profile,
            message="User profile retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user profile", uid=uid, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")


@router.put("/profile/{uid}")
async def update_user_profile_by_uid(
    uid: str,
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        logger.info("Updating user profile", uid=uid)
        
        # Check if user is updating their own profile
        if current_user["uid"] != uid:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get existing profile
        existing_profile = firebase_service.get_document("users", uid)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Prepare update data
        update_data = profile_update.dict(exclude_unset=True)
        
        # Update in Firebase
        firebase_service.update_document("users", uid, update_data)
        
        # Get updated profile
        updated_profile_data = firebase_service.get_document("users", uid)
        updated_profile = UserProfile(**updated_profile_data)
        
        logger.info("User profile updated successfully", uid=uid)
        return ApiResponse(
            success=True,
            data=updated_profile,
            message="User profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update user profile", uid=uid, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")


@router.delete("/profile/{uid}")
async def delete_user_profile_by_uid(
    uid: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete user profile"""
    try:
        logger.info("Deleting user profile", uid=uid)
        
        # Check if user is deleting their own profile
        if current_user["uid"] != uid:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete from Firebase
        firebase_service.delete_document("users", uid)
        
        logger.info("User profile deleted successfully", uid=uid)
        return ApiResponse(
            success=True,
            data={"deleted": True},
            message="User profile deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete user profile", uid=uid, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete user profile: {str(e)}")


@router.get("/{uid}/stats")
async def get_user_stats_by_uid(
    uid: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user statistics"""
    try:
        logger.info("Getting user stats", uid=uid)
        
        # Check permissions
        if current_user["uid"] != uid:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get profile to access stats
        profile_data = firebase_service.get_document("users", uid)
        if not profile_data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        stats = profile_data.get("stats", {
            "recipesGenerated": 0,
            "favoriteRecipes": 0,
            "cookingStreak": 0
        })
        
        logger.info("User stats retrieved successfully", uid=uid)
        return ApiResponse(
            success=True,
            data=stats,
            message="User stats retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user stats", uid=uid, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}") 