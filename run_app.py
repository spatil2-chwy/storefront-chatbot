#!/usr/bin/env python3
"""
Start the FastAPI server for the Chewy clone application
"""
import uvicorn
import os
import sys

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

if __name__ == "__main__":
    # Run the FastAPI app
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )