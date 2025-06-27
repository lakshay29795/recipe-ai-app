"""
Core configuration settings for the Recipe AI App
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "Recipe AI App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Environment
    NODE_ENV: str = os.getenv("NODE_ENV", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Dynamic based on environment
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3000"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add production origins if in production
        if self.NODE_ENV == "production":
            cors_origins = os.getenv("CORS_ORIGINS", "")
            if cors_origins:
                production_origins = [origin.strip() for origin in cors_origins.split(",")]
                self.ALLOWED_ORIGINS.extend(production_origins)
    
    # Firebase configuration
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_TYPE: str = "service_account"
    
    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ORG_ID: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    # OPENAI_IMAGE_MODEL: str = "dall-e-3"
    OPENAI_IMAGE_MODEL: str = "image-model"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Database settings (if using additional databases)
    DATABASE_URL: Optional[str] = None
    
    # API Keys for external services
    NUTRITION_API_KEY: Optional[str] = None
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Recipe generation settings
    MAX_INGREDIENTS: int = 20
    MAX_RECIPES_PER_REQUEST: int = 5
    DEFAULT_SERVINGS: int = 4
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields to be ignored


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()


def get_firebase_credentials() -> dict:
    """Get Firebase credentials dictionary"""
    return {
        "type": settings.FIREBASE_TYPE,
        "project_id": settings.FIREBASE_PROJECT_ID,
        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
        "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n") if settings.FIREBASE_PRIVATE_KEY else None,
        "client_email": settings.FIREBASE_CLIENT_EMAIL,
        "client_id": settings.FIREBASE_CLIENT_ID,
        "auth_uri": settings.FIREBASE_AUTH_URI,
        "token_uri": settings.FIREBASE_TOKEN_URI,
    } 