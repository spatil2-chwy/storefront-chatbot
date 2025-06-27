from pydantic import BaseModel, EmailStr, field_validator
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

    @field_validator("birthday", "adoption_date", "first_birthday", mode="before")
    def parse_dates(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # Try SQLite format first
            try:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f").date()
            except ValueError:
                pass
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                pass
            try:
                return date.fromisoformat(v)
            except Exception:
                pass
            raise ValueError(f"Unrecognized date format: {v}")
        return v

    @field_validator("time_created", "time_updated", mode="before")
    def parse_datetimes(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                pass
            try:
                return datetime.fromisoformat(v)
            except Exception:
                pass
            raise ValueError(f"Unrecognized datetime format: {v}")
        return v

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

    @field_validator("customer_order_first_placed_dttm", mode="before")
    def parse_user_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                pass
            try:
                return datetime.fromisoformat(v)
            except Exception:
                pass
            raise ValueError(f"Unrecognized datetime format: {v}")
        return v

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
    description: str
    inStock: Optional[bool]
    category: str
    keywords: list
    what_customers_love: Optional[str]
    what_to_watch_out_for: Optional[str]
    should_you_buy_it: Optional[str]

class Product(ProductBase):
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    products: List[Product]
    reply: str