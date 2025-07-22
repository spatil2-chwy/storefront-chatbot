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

  // Persona fields
  persona_summary?: string;
  preferred_brands?: string[];
  special_diet?: string[];
  possible_next_buys?: string;
  price_range_food?: { min: number; max: number };
  price_range_treats?: { min: number; max: number };
  price_range_waste_management?: { min: number; max: number };
  price_range_beds?: { min: number; max: number };
  price_range_feeders?: { min: number; max: number };
  price_range_leashes_and_collars?: { min: number; max: number };
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
  allergies: string;       // Comma-separated allergy values
  status: string;          // Current status
  image?: string;          // Optional pet image URL
}

// Pet option for selection
export interface PetOption {
  id: string | number;     // pet_profile_id or "browse"
  name: string;
  type: string;
  breed: string;
}

// Pet profile information for display and editing
export interface PetProfileInfo {
  id: number;
  name: string;
  type: string;
  breed: string;
  gender: string;
  weight: number;
  life_stage: string;
  birthday: string | null;
  allergies: string;       // Comma-separated allergy values
  is_new: boolean;
}

// Product variant size information
export interface Size {
  name?: string; // Variant name
  price?: number;
  pricePerLb?: string;
}

// Sibling item for product variants
export interface SiblingItem {
  id: number; // PRODUCT_ID
  name: string; // NAME
  clean_name: string; // CLEAN_NAME
  price: number; // PRICE
  autoship_price: number; // AUTOSHIP_PRICE
  rating: number; // RATING_AVG
  review_count: number; // RATING_CNT
  thumbnail: string; // THUMBNAIL
  fullimage: string; // FULLIMAGE
  variant?: string; // Extracted variant (e.g., "3.3-lb bag", "7-lb bag")
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
  sibling_items?: SiblingItem[]; // Sibling items for variant switching
  current_variant?: string; // Current variant being displayed
}

// Cart item structure
export interface CartItem {
  id: string;
  product: Product;
  quantity: number;
  purchaseOption: 'buyonce' | 'autoship';
  addedAt: Date;
  price: number; // Price at time of adding to cart
}

// Cart structure
export interface Cart {
  id: string;
  userId?: number;
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
  createdAt: Date;
  updatedAt: Date;
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
  image?: string; // Base64 encoded image data for user messages with images
  imageUrl?: string; // URL for displaying the image
  
  // Pet-related message types
  isPetSelection?: boolean; // For pet selection messages
  petOptions?: PetOption[]; // Available pet options for selection
  isPetProfile?: boolean; // For pet profile display messages
  petProfileInfo?: PetProfileInfo; // Pet information for display
  isPetEdit?: boolean; // For pet editing messages
  petEditData?: PetProfileInfo; // Pet data for editing
  isEditing?: boolean; // For inline editing mode in pet profile messages
}

// Chat context for different conversation modes
export interface ChatContext {
  type: 'general' | 'product' | 'comparison';
  product?: Product;
  products?: Product[];
  selectedPet?: PetProfileInfo; // Currently selected pet for context
} 