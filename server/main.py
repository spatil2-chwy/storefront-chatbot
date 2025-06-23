from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
from routes import router
from storage import storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print(f"{datetime.now().strftime('%I:%M:%S %p')} [fastapi] Starting FastAPI server...")
    yield
    # Shutdown
    print(f"{datetime.now().strftime('%I:%M:%S %p')} [fastapi] Shutting down FastAPI server...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Storefront Chatbot API",
        description="FastAPI backend for the storefront chatbot application",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware (allows frontend to call backend)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router)
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000) 