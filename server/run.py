#!/usr/bin/env python3
"""
Simple script to run the FastAPI backend server
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting FastAPI backend server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    ) 