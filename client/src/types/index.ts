export interface User {
  id: number;
  email: string;
  name: string;
}

export interface Size {
  name?: string; // Variant name
  price?: number;
  pricePerLb?: string;
}

export interface SearchMatch {
  field: string; // e.g., "title", "description", "category", "brand", "keywords"
  matched_terms: string[]; // e.g., ["dental", "dog"]
  confidence: number; // 0.0 to 1.0, how confident we are in this match
  field_value?: string; // the actual field value that matched
}

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
  category?: string; // CATEGORY_LEVEL1
  keywords?: string[]; // specialdiettag/ingredienttag
  search_matches?: SearchMatch[]; // New field for search match analysis
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export interface ChatContext {
  type: 'general' | 'product';
  product?: Product;
} 