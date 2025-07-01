from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from src.database import Base
from pydantic import BaseModel
from typing import List, Optional

class Size(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    pricePerLb: Optional[str] = None
    
class SearchMatch(BaseModel):
    field: str  # e.g., "title", "description", "category", "brand", "keywords"
    matched_terms: List[str]  # e.g., ["dental", "dog"]
    confidence: float  # 0.0 to 1.0, how confident we are in this match
    field_value: Optional[str] = None  # the actual field value that matched
    
class Product(BaseModel):
    id: Optional[int] = None  # PRODUCT_ID
    title: Optional[str] = None  # CLEAN_NAME
    brand: Optional[str] = None  # PURCHASE_BRAND
    price: Optional[float] = None  # PRICE
    originalPrice: Optional[float] = None  # PRICE (for strikethrough/original price)
    autoshipPrice: Optional[float] = None  # AUTOSHIP_PRICE
    rating: Optional[float] = None  # RATING_AVG
    reviewCount: Optional[int] = None  # RATING_CNT
    image: Optional[str] = None  # THUMBNAIL
    images: Optional[List[str]] = None  # FULLIMAGE (array for gallery)
    deal: Optional[bool] = None  # Not available, can be False
    description: Optional[str] = None  # DESCRIPTION_LONG
    inStock: Optional[bool] = None  # Not available, can be True
    category: Optional[str] = None  # CATEGORY_LEVEL1
    keywords: Optional[List[str]] = None  # specialdiettag/ingredienttag
    search_matches: Optional[List[SearchMatch]] = None  # New field for search match analysis
    what_customers_love: Optional[str] = None  # what_customers_love
    what_to_watch_out_for: Optional[str] = None  # what_to_watch_out_for
    should_you_buy_it: Optional[str] = None  # should_you_buy_it
    unanswered_faqs: Optional[str] = None  # Unanswered FAQs
    answered_faqs: Optional[str] = None  # Answered FAQs
