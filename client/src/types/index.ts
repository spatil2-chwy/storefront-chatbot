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
  life_stage: string;      // "P" (puppy), "A" (adult), "S" (senior)
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
  id?: number; // PRODUCT_ID
  title?: string; // CLEAN_NAME
  brand?: string; // PURCHASE_BRAND
  price?: number; // PRICE
  originalPrice?: number; // PRICE (for strikethrough/original price)
  autoshipPrice?: number; // AUTOSHIP_PRICE
  rating?: number; // RATING_AVG
  reviewCount?: number; // RATING_CNT
  image?: string; // THUMBNAIL
  images?: string[]; // FULLIMAGE (array for gallery)
  deal?: boolean; // Not available, can be false
  description?: string; // DESCRIPTION_LONG
  inStock?: boolean; // Not available, can be true
  category_level_1?: string; // CATEGORY_LEVEL1
  category_level_2?: string; // CATEGORY_LEVEL2
  keywords?: string[]; // specialdiettag/ingredienttag
  search_matches?: SearchMatch[]; // New field for search match analysis
  what_customers_love?: string; // what_customers_love
  what_to_watch_out_for?: string; // what_to_watch_out_for
  should_you_buy_it?: string; // should_you_buy_it
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