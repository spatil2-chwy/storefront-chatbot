from fastapi import APIRouter
from src.routers import user_router, product_router, chat_router, health_router

router = APIRouter(prefix="/api")

router.include_router(user_router.router)
router.include_router(product_router.router)
router.include_router(chat_router.router)
router.include_router(health_router.router)