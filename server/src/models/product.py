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
    # ===== CORE PRODUCT INFORMATION =====
    id: Optional[int] = None  # PRODUCT_ID
    name: Optional[str] = None  # NAME
    title: Optional[str] = None  # CLEAN_NAME
    brand: Optional[str] = None  # PURCHASE_BRAND
    parent_company: Optional[str] = None  # PARENT_COMPANY
    
    # ===== PRICING & DEALS =====
    price: Optional[float] = None  # PRICE
    originalPrice: Optional[float] = None  # PRICE (for strikethrough/original price)
    autoshipPrice: Optional[float] = None  # AUTOSHIP_PRICE
    autoship_save_description: Optional[str] = None  # AUTOSHIP_SAVE_DESCRIPTION
    deal: Optional[bool] = None  # Not available, can be False
    
    # ===== RATINGS & REVIEWS =====
    rating: Optional[float] = None  # RATING_AVG
    reviewCount: Optional[int] = None  # RATING_CNT
    
    # ===== IMAGES & MEDIA =====
    image: Optional[str] = None  # THUMBNAIL
    images: Optional[List[str]] = None  # FULLIMAGE (array for gallery)
    
    # ===== PRODUCT DESCRIPTION =====
    description: Optional[str] = None  # DESCRIPTION_LONG
    inStock: Optional[bool] = None  # Not available, can be True
    
    # ===== CATEGORIZATION =====
    category_level_1: Optional[str] = None  # CATEGORY_LEVEL1
    category_level_2: Optional[str] = None  # CATEGORY_LEVEL2
    category_level_3: Optional[str] = None  # CATEGORY_LEVEL3
    product_type: Optional[str] = None  # PRODUCT_TYPE
    
    # ===== PET & LIFE STAGE ATTRIBUTES =====
    attr_pet_type: Optional[str] = None  # ATTR_PET_TYPE
    pet_types: Optional[str] = None  # PET_TYPES
    life_stage: Optional[str] = None  # LIFE_STAGE
    lifestage: Optional[str] = None  # LIFESTAGE
    breed_size: Optional[str] = None  # BREED_SIZE
    
    # ===== FOOD & DIET ATTRIBUTES =====
    attr_food_form: Optional[str] = None  # ATTR_FOOD_FORM
    is_food_flag: Optional[str] = None  # IS_FOOD_FLAG
    ingredients: Optional[str] = None  # INGREDIENTS
    
    # ===== MERCHANDISING CLASSIFICATIONS =====
    merch_classification1: Optional[str] = None  # MERCH_CLASSIFICATION1
    merch_classification2: Optional[str] = None  # MERCH_CLASSIFICATION2
    merch_classification3: Optional[str] = None  # MERCH_CLASSIFICATION3
    merch_classification4: Optional[str] = None  # MERCH_CLASSIFICATION4
    
    # ===== SEARCH & FILTERING =====
    keywords: Optional[List[str]] = None  # specialdiettag/ingredienttag
    search_matches: Optional[List[SearchMatch]] = None  # New field for search match analysis
    
    # ===== AI-GENERATED CONTENT =====
    what_customers_love: Optional[str] = None  # what_customers_love
    what_to_watch_out_for: Optional[str] = None  # what_to_watch_out_for
    should_you_buy_it: Optional[str] = None  # should_you_buy_it
    
    # ===== FAQ CONTENT =====
    unanswered_faqs: Optional[str] = None  # Unanswered FAQs
    answered_faqs: Optional[str] = None  # Answered FAQs