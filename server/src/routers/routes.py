from fastapi import APIRouter

from src.routers.health_router import router as health_router
from src.routers.user_router import router as user_router
from src.routers.pet_router import router as pet_router
from src.routers.product_router import router as product_router
from src.routers.chat_router import router as chat_router
from src.routers.cart_router import router as cart_router
from src.routers.orders import router as orders_router
from src.routers.interaction_router import router as interaction_router

router = APIRouter()
router.include_router(health_router)
router.include_router(user_router)
router.include_router(pet_router)
router.include_router(product_router)
router.include_router(chat_router)
router.include_router(cart_router)
router.include_router(orders_router)
router.include_router(interaction_router)
