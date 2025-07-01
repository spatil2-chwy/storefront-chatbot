from .database import ProductService, PetService, UserService, ChatService
from .chat_modes import compare_products, get_product_comparison_data, ask_about_product

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
    'get_product_comparison_data',
    'ask_about_product'
]