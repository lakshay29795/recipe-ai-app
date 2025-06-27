"""
Recipe AI App - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog
from app.core.config import settings
from app.core.logging import setup_logging

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.recipes import router as recipes_router
from app.api.v1.history import router as history_router
from app.api.v1.ingredients import router as ingredients_router
from app.api.v1.recipe_management import router as recipe_management_router
from app.api.v1.personalization import router as personalization_router

# Setup logging
setup_logging()
logger = structlog.get_logger()


# Create FastAPI application
app = FastAPI(
    title="Recipe AI App API",
    description="AI-powered recipe generation with personalized recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "Recipe AI App API",
            "version": "1.0.0",
            "environment": settings.NODE_ENV
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "error",
            "service": "Recipe AI App API",
            "version": "1.0.0",
            "error": str(e)
        }


# Simple test endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint for basic connectivity test"""
    return {"message": "Recipe AI App API is running"}


# Include API routes
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    recipes_router,
    prefix="/api/v1/recipes",
    tags=["Recipes"]
)

app.include_router(
    history_router,
    prefix="/api/v1/history",
    tags=["History"]
)

app.include_router(
    ingredients_router,
    prefix="/api/v1/ingredients",
    tags=["Ingredients"]
)

app.include_router(
    recipe_management_router,
    prefix="/api/v1",
    tags=["Recipe Management"]
)

app.include_router(
    personalization_router,
    prefix="/api/v1",
    tags=["Personalization"]
)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    logger.error(
        "Unexpected error occurred",
        error=str(exc),
        path=request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 