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
    
    # Persona fields
    persona_summary: Optional[str] = None
    preferred_brands: Optional[str] = None  # JSON string
    special_diet: Optional[str] = None  # JSON string
    possible_next_buys: Optional[str] = None
    price_range_food: Optional[str] = None  # JSON string
    price_range_treats: Optional[str] = None  # JSON string
    price_range_waste_management: Optional[str] = None  # JSON string
    price_range_beds: Optional[str] = None  # JSON string
    price_range_feeders: Optional[str] = None  # JSON string
    price_range_leashes_and_collars: Optional[str] = None  # JSON string

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

class SearchMatch(BaseModel):
    field: str  # e.g., "title", "description", "category", "brand", "keywords"
    matched_terms: List[str]  # e.g., ["dental", "dog"]
    confidence: float  # 0.0 to 1.0, how confident we are in this match
    field_value: Optional[str] = None  # the actual field value that matched

# Sibling item for product variants
class SiblingItem(BaseModel):
    id: int  # PRODUCT_ID
    name: str  # NAME
    clean_name: str  # CLEAN_NAME
    price: float  # PRICE
    autoship_price: float  # AUTOSHIP_PRICE
    rating: float  # RATING_AVG
    review_count: int  # RATING_CNT
    thumbnail: str  # THUMBNAIL
    fullimage: str  # FULLIMAGE
    variant: Optional[str] = None  # Extracted variant (e.g., "3.3-lb bag", "7-lb bag")

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
    category_level_1: str
    category_level_2: str
    keywords: list
    search_matches: Optional[List[SearchMatch]] = None
    what_customers_love: Optional[str]
    what_to_watch_out_for: Optional[str]
    should_you_buy_it: Optional[str]
    unanswered_faqs: Optional[str] = None
    answered_faqs: Optional[str] = None
    sibling_items: Optional[List[SiblingItem]] = None
    current_variant: Optional[str] = None

class Product(ProductBase):
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    products: List[Product]
    reply: str

# Order Schemas
class OrderItemBase(BaseModel):
    product_id: int
    product_title: str
    product_brand: Optional[str] = None
    product_image: Optional[str] = None
    quantity: int
    purchase_option: str = "buyonce"  # buyonce or autoship
    unit_price: float
    total_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    item_id: int
    order_id: int
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_id: int
    subtotal: float
    shipping_cost: float = 0.0
    tax_amount: float = 0.0
    total_amount: float
    
    # Shipping Information
    shipping_first_name: str
    shipping_last_name: str
    shipping_email: EmailStr
    shipping_phone: Optional[str] = None
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_zip_code: str
    
    # Payment Information (masked)
    payment_method: str = "credit_card"
    card_last_four: Optional[str] = None
    cardholder_name: Optional[str] = None
    
    # Billing Address (optional)
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_zip_code: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    order_id: int
    status: str = "processing"
    order_date: datetime
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []
    
    class Config:
        from_attributes = True

class OrderSummary(BaseModel):
    order_id: int
    order_date: datetime
    status: str
    total_amount: float
    items_count: int
    
    class Config:
        from_attributes = True