"""
Authentication API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import structlog
from app.core.auth import (
    verify_firebase_token, 
    create_user_session, 
    get_current_user,
    get_optional_user,
    AuthenticationError
)
from app.services.user_service import user_service
from app.models.user_models import UserRegistrationRequest, UserResponse

logger = structlog.get_logger(__name__)
router = APIRouter()


# Request/Response Models
class LoginRequest(BaseModel):
    firebase_token: str  # Firebase ID token from frontend


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: str
    user: UserResponse


class RegisterRequest(BaseModel):
    firebase_token: str  # Firebase ID token from frontend
    display_name: Optional[str] = None


class TokenRefreshRequest(BaseModel):
    firebase_token: str


class MessageResponse(BaseModel):
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with Firebase ID token
    """
    try:
        # Verify Firebase token
        firebase_user_data = await verify_firebase_token(request.firebase_token)
        
        # Check if user exists in our database
        user = await user_service.get_user_by_email(firebase_user_data.get("email"))
        
        if not user:
            # Create new user if doesn't exist
            user_data = {
                "id": firebase_user_data.get("uid"),
                "email": firebase_user_data.get("email"),
                "display_name": firebase_user_data.get("name", ""),
                "photo_url": firebase_user_data.get("picture"),
                "is_verified": firebase_user_data.get("email_verified", False)
            }
            
            user = await user_service.create_user(user_data)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user account"
                )
            
            logger.info("New user created during login", user_id=user.id)
        
        # Create session
        session_data = await create_user_session(firebase_user_data)
        
        # Update user stats
        await user_service.update_user_stats(user.id, {"last_activity": None})
        
        logger.info("User logged in successfully", user_id=user.id)
        
        return LoginResponse(
            access_token=session_data["access_token"],
            token_type=session_data["token_type"],
            expires_in=session_data["expires_in"],
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                photo_url=user.photo_url,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )
        
    except AuthenticationError as e:
        logger.warning("Authentication failed during login", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """
    Register new user with Firebase ID token
    """
    try:
        # Verify Firebase token
        firebase_user_data = await verify_firebase_token(request.firebase_token)
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(firebase_user_data.get("email"))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        
        # Create new user
        user_data = {
            "id": firebase_user_data.get("uid"),
            "email": firebase_user_data.get("email"),
            "display_name": request.display_name or firebase_user_data.get("name", ""),
            "photo_url": firebase_user_data.get("picture"),
            "is_verified": firebase_user_data.get("email_verified", False)
        }
        
        user = await user_service.create_user(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        # Create session
        session_data = await create_user_session(firebase_user_data)
        
        logger.info("User registered successfully", user_id=user.id)
        
        return LoginResponse(
            access_token=session_data["access_token"],
            token_type=session_data["token_type"],
            expires_in=session_data["expires_in"],
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                photo_url=user.photo_url,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )
        
    except AuthenticationError as e:
        logger.warning("Authentication failed during registration", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh access token using Firebase ID token
    """
    try:
        # Verify Firebase token
        firebase_user_data = await verify_firebase_token(request.firebase_token)
        
        # Get user from database
        user = await user_service.get_user(firebase_user_data.get("uid"))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new session
        session_data = await create_user_session(firebase_user_data)
        
        logger.info("Token refreshed successfully", user_id=user.id)
        
        return LoginResponse(
            access_token=session_data["access_token"],
            token_type=session_data["token_type"],
            expires_in=session_data["expires_in"],
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                photo_url=user.photo_url,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )
        
    except AuthenticationError as e:
        logger.warning("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout current user
    """
    try:
        # Update user stats
        await user_service.update_user_stats(
            current_user["user_id"], 
            {"last_activity": None}
        )
        
        logger.info("User logged out successfully", user_id=current_user["user_id"])
        
        return MessageResponse(message="Logged out successfully")
        
    except Exception as e:
        logger.error("Logout failed", error=str(e), user_id=current_user.get("user_id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    try:
        user = await user_service.get_user(current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            photo_url=user.photo_url,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user info", error=str(e), user_id=current_user.get("user_id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.get("/status")
async def auth_status(current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    """
    Check authentication status (optional authentication)
    """
    if current_user:
        return {
            "authenticated": True,
            "user_id": current_user["user_id"],
            "email": current_user.get("email"),
            "auth_provider": current_user.get("auth_provider")
        }
    else:
        return {
            "authenticated": False
        } 