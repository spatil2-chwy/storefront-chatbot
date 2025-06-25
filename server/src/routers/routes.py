from fastapi import APIRouter

from .user_router    import router as user_router
from .product_router import router as product_router
from .chat_router    import router as chat_router
from .health_router  import router as health_router
from .pet_router     import router as pet_router

router = APIRouter()
router.include_router(user_router,    prefix="/users",   tags=["users"])
router.include_router(product_router, prefix="/products",tags=["products"])
router.include_router(chat_router,    prefix="/chat",    tags=["chat"])
router.include_router(health_router,  prefix="/health",  tags=["health"])
router.include_router(pet_router,     prefix="/pets",    tags=["pets"])
