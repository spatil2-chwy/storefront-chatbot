from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from schemas import User, UserCreate, Product, ChatMessage, ChatMessageCreate
from storage import storage

router = APIRouter(prefix="/api")

# User routes
@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user by ID"""
    user = await storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/email/{email}", response_model=User)
async def get_user_by_email(email: str):
    """Get user by email"""
    user = await storage.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    # Check if user already exists
    existing_user = await storage.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    return await storage.create_user(user_data)

# Product routes
@router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    keywords: Optional[str] = Query(None, description="Comma-separated keywords to filter by")
):
    """Get products with optional filtering"""
    keyword_list = None
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",")]
    
    return await storage.get_products(category=category, keywords=keyword_list)

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get product by ID"""
    product = await storage.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Chat routes
@router.get("/chat/messages", response_model=List[ChatMessage])
async def get_chat_messages():
    """Get all chat messages"""
    return await storage.get_chat_messages()

@router.post("/chat/messages", response_model=ChatMessage)
async def add_chat_message(message_data: ChatMessageCreate):
    """Add a new chat message"""
    return await storage.add_chat_message(message_data)

@router.delete("/chat/messages")
async def clear_chat_messages():
    """Clear all chat messages"""
    await storage.clear_chat_messages()
    return {"message": "Chat messages cleared"}

# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastAPI backend is running"} 