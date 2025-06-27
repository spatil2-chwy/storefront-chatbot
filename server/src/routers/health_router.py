from fastapi import APIRouter
from src.services.searchengine import warmup
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastAPI backend is running"}

@router.post("/warmup")
async def warmup_search():
    """Endpoint to manually trigger search engine warmup"""
    start_time = time.time()
    try:
        warmup()
        warmup_time = time.time() - start_time
        return {
            "status": "success", 
            "message": f"Search engine warmed up successfully in {warmup_time:.4f} seconds"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Warmup failed: {str(e)}"
        }
