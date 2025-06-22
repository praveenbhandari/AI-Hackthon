#!/usr/bin/env python
"""
Launcher script for BC CrewAI FastAPI
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the API
from bc.api import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting BC CrewAI FastAPI Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 