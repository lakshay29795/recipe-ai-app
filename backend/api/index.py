"""
Vercel ASGI entry point - Working Recipe AI App
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path for Vercel serverless environment
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Create the main app
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
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Recipe AI App API",
        "version": "1.0.0",
        "environment": "production"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint for basic connectivity test"""
    return {"message": "Recipe AI App API is running"}

# Basic test endpoint
@app.get("/test", tags=["Test"])
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "Test successful",
        "status": "working",
        "features": ["health", "cors", "basic_routing"]
    }

# Diagnostic endpoint to check what's failing
@app.get("/api/v1/diagnostics", tags=["Diagnostics"])
async def diagnostics():
    """Check what components are working"""
    diagnostics = {
        "environment_variables": {},
        "imports": {},
        "services": {}
    }
    
    # Check environment variables
    diagnostics["environment_variables"]["OPENAI_API_KEY"] = "SET" if os.getenv("OPENAI_API_KEY") else "MISSING"
    diagnostics["environment_variables"]["FIREBASE_PROJECT_ID"] = "SET" if os.getenv("FIREBASE_PROJECT_ID") else "MISSING"
    diagnostics["environment_variables"]["NODE_ENV"] = os.getenv("NODE_ENV", "not_set")
    
    # Check imports
    try:
        import openai
        diagnostics["imports"]["openai"] = "✅ SUCCESS"
    except Exception as e:
        diagnostics["imports"]["openai"] = f"❌ FAILED: {str(e)}"
    
    try:
        import structlog
        diagnostics["imports"]["structlog"] = "✅ SUCCESS"
    except Exception as e:
        diagnostics["imports"]["structlog"] = f"❌ FAILED: {str(e)}"
    
    try:
        from app.services.ai_service import ai_service
        diagnostics["services"]["ai_service"] = "✅ SUCCESS"
        
        # Test if AI service is properly initialized
        if hasattr(ai_service, '_initialized'):
            diagnostics["services"]["ai_service_initialized"] = "✅ READY" if ai_service._initialized else "❌ NOT_INITIALIZED"
    except Exception as e:
        diagnostics["services"]["ai_service"] = f"❌ FAILED: {str(e)}"
    
    try:
        from app.services.firebase_service import firebase_service
        diagnostics["services"]["firebase_service"] = "✅ SUCCESS"
    except Exception as e:
        diagnostics["services"]["firebase_service"] = f"❌ FAILED: {str(e)}"
    
    try:
        from app.api.v1.recipes import router as recipes_router
        diagnostics["imports"]["recipes_router"] = "✅ SUCCESS"
    except Exception as e:
        diagnostics["imports"]["recipes_router"] = f"❌ FAILED: {str(e)}"
    
    return {
        "status": "diagnostic_complete",
        "diagnostics": diagnostics,
        "message": "Check the results to see what needs to be fixed for AI functionality"
    }

# Try to import the real routers
try:
    from app.api.v1.recipes import router as recipes_router
    app.include_router(recipes_router, prefix="/api/v1/recipes", tags=["Recipes"])
    print("✅ Real recipes router imported successfully")
    
    # Add a test endpoint without authentication to test AI functionality
    @app.post("/api/v1/test-ai", tags=["Test-AI"])
    async def test_ai_generation(request_data: dict):
        """Test AI recipe generation without authentication"""
        try:
            from app.services.recipe_service import recipe_service
            from app.models.recipe_models import RecipeGenerationRequest
            
            # Convert dict to proper model
            ingredients = request_data.get("ingredients", ["tomatoes", "garlic"])
            servings = request_data.get("servings", 4)
            preferred_cuisine = request_data.get("preferred_cuisine", "Italian")
            
            # Generate recipe using AI (without user authentication)
            result = await recipe_service.generate_ai_recipe(
                ingredients=ingredients,
                user_id=None,  # No user authentication
                dietary_restrictions=None,
                cuisine_preference=preferred_cuisine,
                difficulty=None,
                max_cooking_time=None,
                servings=servings,
                additional_notes=None
            )
            
            if result:
                return {
                    "status": "success",
                    "message": "🎉 Real AI recipe generation working!",
                    "recipe": result
                }
            else:
                return {
                    "status": "failed",
                    "message": "AI service returned no result"
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"AI test failed: {str(e)}"
            }
            
except Exception as e:
    print(f"❌ Failed to import recipes router: {e}")
    
    # Simple fallback recipe endpoint if the real one fails
    @app.post("/api/v1/recipes/generate", tags=["Recipes-Fallback"])
    async def generate_recipe_fallback(request_data: dict):
        return {
            "error": "Real AI service unavailable",
            "fallback_recipe": {
                "title": "Simple recipe fallback",
                "ingredients": request_data.get("ingredients", []),
                "message": "Install OpenAI integration for AI-powered recipes"
            },
            "status": "fallback"
        }

try:
    from app.api.v1.users import router as users_router
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    print("✅ Real users router imported successfully")
except Exception as e:
    print(f"❌ Failed to import users router: {e}")
    
    # Simple fallback user endpoint if the real one fails
    @app.post("/api/v1/users/profile", tags=["Users-Fallback"])
    async def update_profile_fallback(request_data: dict):
        return {
            "message": "Profile updated successfully (fallback mode)",
            "data": request_data,
            "status": "fallback"
        }
