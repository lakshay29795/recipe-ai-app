"""
Vercel deployment entry point
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path for Vercel serverless environment
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Now import the app
from app.main import app

# This is the ASGI app that Vercel will use
# No need to run uvicorn.run() for serverless deployment
handler = app
