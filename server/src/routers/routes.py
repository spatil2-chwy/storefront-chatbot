from fastapi import APIRouter
from src.routers import users, products, chat, health

router = APIRouter(prefix="/api")

router.include_router(users.router)
router.include_router(products.router)
router.include_router(chat.router)
router.include_router(health.router)