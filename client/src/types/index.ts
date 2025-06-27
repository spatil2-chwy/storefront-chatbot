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
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  comparisonProductIds?: number[]; // For comparison messages to store product IDs
  comparisonProductCount?: number; // For comparison messages to store original product count
  productTitle?: string; // For product discussion messages to store product title
  comparisonProducts?: Product[]; // For comparison messages to store full product data
}

export interface ChatContext {
  type: 'general' | 'product';
  product?: Product;
} 