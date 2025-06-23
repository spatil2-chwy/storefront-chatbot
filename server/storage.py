from typing import Dict, List, Optional
from datetime import datetime
import uuid
from schemas import User, UserCreate, Product, ChatMessage, ChatMessageCreate, SenderType, Size

class MemStorage:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.products: Dict[int, Product] = {}
        self.chat_messages: List[ChatMessage] = []
        self.current_user_id = 1
        
        # Initialize with some dummy data
        self._initialize_dummy_data()
    
    def _initialize_dummy_data(self):
        """Initialize storage with dummy data for testing"""
        # Add dummy users
        user_data = UserCreate(
            email="test@example.com",
            name="Test User"
        )
        user_id = self.current_user_id
        self.current_user_id += 1
        
        user = User(
            id=user_id,
            email=user_data.email,
            name=user_data.name
        )
        self.users[user_id] = user
        
        # Add dummy products
        self.products[1] = Product(
            id=1,
            title="Purina Pro Plan Adult Dog Food",
            brand="Purina",
            price=49.99,
            originalPrice=59.99,
            autoshipPrice=44.99,
            rating=4.5,
            reviewCount=1250,
            image="/images/dog-food-1.jpg",
            images=["/images/dog-food-1.jpg", "/images/dog-food-1-2.jpg"],
            deal=True,
            flavors=["Chicken & Rice", "Beef & Rice"],
            sizes=[
                Size(name="30 lb", price=49.99, pricePerLb="$1.67/lb"),
                Size(name="47 lb", price=69.99, pricePerLb="$1.49/lb")
            ],
            description="High-quality adult dog food with real chicken as the first ingredient.",
            inStock=True,
            category="Dog Food",
            keywords=["dog", "food", "adult", "chicken", "protein"]
        )
        
        # Add dummy chat messages
        self.chat_messages.append(ChatMessage(
            id=str(uuid.uuid4()),
            content="Hello! How can I help you find the perfect pet food today?",
            sender=SenderType.AI,
            timestamp=datetime.now()
        ))
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user_id = self.current_user_id
        self.current_user_id += 1
        
        user = User(
            id=user_id,
            email=user_data.email,
            name=user_data.name
        )
        
        self.users[user_id] = user
        return user
    
    async def get_products(self, category: Optional[str] = None, keywords: Optional[List[str]] = None) -> List[Product]:
        """Get products with optional filtering"""
        products = list(self.products.values())
        
        if category:
            products = [p for p in products if p.category.lower() == category.lower()]
        
        if keywords:
            # Simple keyword matching
            filtered_products = []
            for product in products:
                product_text = f"{product.title} {product.brand} {product.description}".lower()
                if any(keyword.lower() in product_text for keyword in keywords):
                    filtered_products.append(product)
            products = filtered_products
        
        return products
    
    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    async def get_chat_messages(self) -> List[ChatMessage]:
        """Get all chat messages"""
        return self.chat_messages
    
    async def add_chat_message(self, message_data: ChatMessageCreate) -> ChatMessage:
        """Add a new chat message"""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            content=message_data.content,
            sender=message_data.sender,
            timestamp=datetime.now()
        )
        
        self.chat_messages.append(message)
        return message
    
    async def clear_chat_messages(self) -> None:
        """Clear all chat messages"""
        self.chat_messages.clear()

# Global storage instance
storage = MemStorage() 