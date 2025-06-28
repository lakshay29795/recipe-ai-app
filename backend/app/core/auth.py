"""
Authentication utilities and middleware
"""

import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as firebase_auth
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()


class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass


async def verify_firebase_token(token: str) -> Dict[str, Any]:
    """Verify Firebase ID token and return user claims"""
    try:
        # Try to initialize Firebase if not already done
        try:
            firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase with proper credentials
            from app.core.config import get_firebase_credentials
            from firebase_admin import credentials
            
            cred_dict = get_firebase_credentials()
            if cred_dict.get('project_id') and cred_dict.get('private_key'):
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized with credentials for authentication")
            else:
                # Fallback to default initialization for development
                firebase_admin.initialize_app()
                logger.warning("Firebase initialized without credentials")
        
        # Verify the Firebase ID token
        decoded_token = firebase_auth.verify_id_token(token)
        logger.info("Firebase token verified successfully", user_id=decoded_token.get('uid'))
        return decoded_token
    except firebase_auth.InvalidIdTokenError:
        logger.warning("Invalid Firebase ID token")
        raise AuthenticationError("Invalid authentication token")
    except firebase_auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase ID token")
        raise AuthenticationError("Authentication token has expired")
    except Exception as e:
        logger.error("Firebase token verification failed", error=str(e))
        raise AuthenticationError("Token verification failed")


async def create_access_token(user_data: Dict[str, Any]) -> str:
    """Create a JWT access token for the user"""
    try:
        # Token payload
        payload = {
            "user_id": user_data.get("uid"),
            "email": user_data.get("email"),
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "iss": "recipe-ai-app"
        }
        
        # Encode the token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.info("Access token created", user_id=user_data.get("uid"))
        return token
    except Exception as e:
        logger.error("Failed to create access token", error=str(e))
        raise AuthenticationError("Failed to create access token")


async def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify JWT access token and return payload"""
    try:
        # Decode and verify the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            raise AuthenticationError("Token has expired")
        
        logger.info("Access token verified", user_id=payload.get("user_id"))
        return payload
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        raise AuthenticationError("Invalid token")
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        raise AuthenticationError("Token verification failed")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Dependency to get the current authenticated user"""
    try:
        token = credentials.credentials
        
        # First try to verify as Firebase token, then as JWT
        try:
            # Try Firebase token verification first
            user_data = await verify_firebase_token(token)
            return {
                "uid": user_data.get("uid"),
                "user_id": user_data.get("uid"),
                "email": user_data.get("email"),
                "display_name": user_data.get("name"),
                "photo_url": user_data.get("picture"),
                "is_verified": user_data.get("email_verified", False),
                "auth_provider": "firebase"
            }
        except AuthenticationError:
            # If Firebase verification fails, try JWT
            payload = await verify_access_token(token)
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "auth_provider": "jwt"
            }
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Optional[Dict[str, Any]]:
    """Dependency to get the current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


class RequireAuth:
    """Decorator class for requiring authentication on routes"""
    
    def __init__(self, require_verified: bool = False):
        self.require_verified = require_verified
    
    async def __call__(self, current_user: Dict[str, Any] = Security(get_current_user)) -> Dict[str, Any]:
        if self.require_verified and not current_user.get("is_verified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required"
            )
        return current_user


# Pre-configured auth dependencies
require_auth = RequireAuth()
require_verified_auth = RequireAuth(require_verified=True)


async def create_user_session(user_data: Dict[str, Any]) -> Dict[str, str]:
    """Create a new user session with access token"""
    try:
        access_token = await create_access_token(user_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": str(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)  # in seconds
        }
    except Exception as e:
        logger.error("Failed to create user session", error=str(e))
        raise AuthenticationError("Failed to create session")


async def validate_user_permissions(current_user: Dict[str, Any], resource_user_id: str) -> bool:
    """Validate if current user can access resource belonging to specific user"""
    # Users can only access their own resources
    return current_user.get("user_id") == resource_user_id


async def require_user_access(current_user: Dict[str, Any], resource_user_id: str):
    """Require that current user has access to the specified user's resources"""
    if not await validate_user_permissions(current_user, resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        ) 