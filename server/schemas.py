from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SenderType(str, Enum):
    USER = "user"
    AI = "ai"

class Size(BaseModel):
    name: str
    price: float
    pricePerLb: str

class User(BaseModel):
    id: int
    email: EmailStr
    name: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str

class Product(BaseModel):
    id: int
    title: str
    brand: str
    price: float
    originalPrice: Optional[float] = None
    autoshipPrice: float
    rating: float
    reviewCount: int
    image: str
    images: List[str]
    deal: bool
    flavors: List[str]
    sizes: List[Size]
    description: str
    inStock: bool
    category: str
    keywords: List[str]

class ChatMessage(BaseModel):
    id: str
    content: str
    sender: SenderType
    timestamp: datetime

class ChatMessageCreate(BaseModel):
    content: str
    sender: SenderType 