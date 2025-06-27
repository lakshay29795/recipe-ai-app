"""
Vercel deployment entry point
"""

from app.main import app

# This is the ASGI app that Vercel will use
# No need to run uvicorn.run() for serverless deployment
handler = app
