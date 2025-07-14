from .product_service import ProductService
from .pet_service import PetService
from .user_service import UserService
from .chat_service import ChatService
from src.chat.chat_modes import compare_products, ask_about_product

# Create singleton instances
product_service = ProductService()
pet_service = PetService()
user_service = UserService()
chat_service = ChatService()

__all__ = [
    'product_service',
    'pet_service', 
    'user_service',
    'chat_service',
    'compare_products',
    'ask_about_product'
]