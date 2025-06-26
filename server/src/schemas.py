from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date
from src.models.constants import SenderType
from src.models.pet import PetProfile as PetProfileModel

class PetProfileBase(BaseModel):
    pet_profile_id: int
    customer_id: int
    pet_name: Optional[str]
    pet_type: Optional[str]
    pet_breed: Optional[str]
    pet_breed_size_type: Optional[str]
    gender: Optional[str]
    weight_type: Optional[str]
    size_type: Optional[str]
    birthday: Optional[date]
    life_stage: Optional[str]
    adopted: Optional[bool]
    adoption_date: Optional[date]
    status: str
    status_reason: Optional[str]
    time_created: datetime
    time_updated: Optional[datetime]
    weight: Optional[int]
    allergy_count: Optional[int]
    photo_count: Optional[int]
    pet_breed_id: Optional[int]
    pet_type_id: Optional[int]
    pet_new: Optional[bool]
    first_birthday: Optional[date]

class PetProfile(PetProfileBase):
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    customer_key: int
    customer_id: int
    name: str
    email: EmailStr
    password: str
    operating_revenue_trailing_365: Optional[float]
    customer_order_first_placed_dttm: Optional[datetime]
    customer_address_zip: Optional[str]
    customer_address_city: Optional[str]
    customer_address_state: Optional[str]

class User(UserBase):
    pets: List[PetProfile] = []
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatMessageBase(BaseModel):
    id: str
    content: str
    sender: SenderType
    timestamp: datetime

class ChatMessage(ChatMessageBase):
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    id: int
    title: str
    brand: str
    price: float
    originalPrice: Optional[float]
    autoshipPrice: float
    rating: float
    reviewCount: int
    image: str
    images: list
    deal: Optional[bool]
    flavors: list
    sizes: list
    description: str
    inStock: Optional[bool]
    category: str
    keywords: list

class Product(ProductBase):
    class Config:
        from_attributes = True