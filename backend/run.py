"""
Development server runner
"""

import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Use PORT environment variable for production compatibility
    port = int(os.getenv("PORT", 8000))
    is_production = os.getenv("NODE_ENV") == "production"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,  # Disable reload in production
        log_level="info"
    ) 