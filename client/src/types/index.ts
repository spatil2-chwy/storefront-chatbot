// Centralized type definitions for the application
// All interfaces and types should be defined here

// User authentication and profile data
export interface User {
  customer_key: number;
  customer_id: number;
  name: string;
  email: string;
  password: string;
  operating_revenue_trailing_365?: number;
  customer_order_first_placed_dttm?: string;
  customer_address_zip?: string;
  customer_address_city?: string;
  customer_address_state?: string;
}

// Pet profile data
export interface Pet {
  pet_profile_id: number;
  pet_name: string;
  pet_type: string;        // "DOG", "CAT", etc.
  pet_breed: string;       // "Golden Retriever", etc.
  gender: string;          // "MALE", "FMLE"
  birthday: string;        // ISO date string
  life_stage: string;      // "PUPPY", "ADULT", "SENIOR"
  adopted: boolean;        // Whether pet was adopted
  adoption_date: string | null; // When adopted
  weight: number;          // Weight in pounds
  allergy_count: number;   // Number of allergies
  status: string;          // Current status
  image?: string;          // Optional pet image URL
}

// Product variant size information
export interface Size {
  name?: string; // Variant name
  price?: number;
  pricePerLb?: string;
}

// Search match analysis data
export interface SearchMatch {
  field: string; // e.g., "title", "description", "category", "brand", "keywords"
  matched_terms: string[]; // e.g., ["dental", "dog"]
  confidence: number; // 0.0 to 1.0, how confident we are in this match
  field_value?: string; // the actual field value that matched
}

// Product catalog item
export interface Product {
  // ===== CORE PRODUCT INFORMATION =====
  id?: number; // PRODUCT_ID
  name?: string; // NAME
  title?: string; // CLEAN_NAME
  brand?: string; // PURCHASE_BRAND
  parent_company?: string; // PARENT_COMPANY
  
  // ===== PRICING & DEALS =====
  price?: number; // PRICE
  originalPrice?: number; // PRICE (for strikethrough/original price)
  autoshipPrice?: number; // AUTOSHIP_PRICE
  autoship_save_description?: string; // AUTOSHIP_SAVE_DESCRIPTION
  deal?: boolean; // Not available, can be false
  
  // ===== RATINGS & REVIEWS =====
  rating?: number; // RATING_AVG
  reviewCount?: number; // RATING_CNT
  
  // ===== IMAGES & MEDIA =====
  image?: string; // THUMBNAIL
  images?: string[]; // FULLIMAGE (array for gallery)
  
  // ===== PRODUCT DESCRIPTION =====
  description?: string; // DESCRIPTION_LONG
  inStock?: boolean; // Not available, can be true
  
  // ===== CATEGORIZATION =====
  category_level_1?: string; // CATEGORY_LEVEL1
  category_level_2?: string; // CATEGORY_LEVEL2
  category_level_3?: string; // CATEGORY_LEVEL3
  product_type?: string; // PRODUCT_TYPE
  
  // ===== PET & LIFE STAGE ATTRIBUTES =====
  attr_pet_type?: string; // ATTR_PET_TYPE
  pet_types?: string; // PET_TYPES
  life_stage?: string; // LIFE_STAGE
  lifestage?: string; // LIFESTAGE
  breed_size?: string; // BREED_SIZE
  
  // ===== FOOD & DIET ATTRIBUTES =====
  attr_food_form?: string; // ATTR_FOOD_FORM
  is_food_flag?: string; // IS_FOOD_FLAG
  ingredients?: string; // INGREDIENTS
  
  // ===== MERCHANDISING CLASSIFICATIONS =====
  merch_classification1?: string; // MERCH_CLASSIFICATION1
  merch_classification2?: string; // MERCH_CLASSIFICATION2
  merch_classification3?: string; // MERCH_CLASSIFICATION3
  merch_classification4?: string; // MERCH_CLASSIFICATION4
  
  // ===== SEARCH & FILTERING =====
  keywords?: string[]; // specialdiettag/ingredienttag
  search_matches?: SearchMatch[]; // New field for search match analysis
  
  // ===== AI-GENERATED CONTENT =====
  what_customers_love?: string; // what_customers_love
  what_to_watch_out_for?: string; // what_to_watch_out_for
  should_you_buy_it?: string; // should_you_buy_it
  
  // ===== FAQ CONTENT =====
  unanswered_faqs?: string; // Unanswered FAQs
  answered_faqs?: string; // Answered FAQs
}

// Chat message structure
export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  comparisonProductIds?: number[]; // For comparison messages to store product IDs
  comparisonProductCount?: number; // For comparison messages to store original product count
  productTitle?: string; // For product discussion messages to store product title
  comparisonProducts?: Product[]; // For comparison messages to store full product data
  productData?: Product; // For product transition messages to store full product data
  isTransition?: boolean; // For transition messages between contexts
  transitionType?: 'general' | 'product' | 'comparison'; // Type of transition for styling
}

// Chat context for different conversation modes
export interface ChatContext {
  type: 'general' | 'product' | 'comparison';
  product?: Product;
  products?: Product[];
} 