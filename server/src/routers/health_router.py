# Health router - handles system health checks
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    # Basic health check endpoint
    return {"status": "healthy", "message": "FastAPI backend is running"}

