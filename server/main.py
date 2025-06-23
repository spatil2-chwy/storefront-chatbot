from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
from datetime import datetime
from routes import router
from storage import storage

# Custom middleware for logging (replicates Express logging)
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration = int((time.time() - start_time) * 1000)
        
        # Log API requests (similar to Express logging)
        if request.url.path.startswith("/api"):
            # Try to capture response body for logging
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Reconstruct response
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Format log message
            log_line = f"{request.method} {request.url.path} {response.status_code} in {duration}ms"
            
            # Try to add response data if it's JSON
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    response_data = json.loads(response_body.decode())
                    if response_data:
                        log_line += f" :: {json.dumps(response_data)}"
            except:
                pass
            
            # Truncate long log lines
            if len(log_line) > 80:
                log_line = log_line[:79] + "…"
            
            # Log with timestamp
            timestamp = datetime.now().strftime("%I:%M:%S %p")
            print(f"{timestamp} [fastapi] {log_line}")
        
        return response

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Storefront Chatbot API",
        description="FastAPI backend for the storefront chatbot application",
        version="1.0.0"
    )
    
    # Add CORS middleware (allows frontend to call backend)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Include API routes
    app.include_router(router)
    
    return app

# Create the app instance
app = create_app()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize storage on startup"""
    print(f"{datetime.now().strftime('%I:%M:%S %p')} [fastapi] Starting FastAPI server...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"{datetime.now().strftime('%I:%M:%S %p')} [fastapi] Shutting down FastAPI server...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000) 