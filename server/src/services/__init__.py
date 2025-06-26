from .product_service import ProductService
from .pet_service import PetService
from .user_service import UserService
from .chat_service import ChatService
from .comparison_service import compare_products, get_product_comparison_data

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
    'get_product_comparison_data'
]