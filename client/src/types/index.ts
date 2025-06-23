export interface User {
  id: number;
  email: string;
  name: string;
}

export interface Product {
  id: number;
  title: string;
  brand: string;
  price: number;
  originalPrice?: number;
  autoshipPrice: number;
  rating: number;
  reviewCount: number;
  image: string;
  images: string[];
  deal: boolean;
  flavors: string[];
  sizes: {
    name: string;
    price: number;
    pricePerLb: string;
  }[];
  description: string;
  inStock: boolean;
  category: string;
  keywords: string[];
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
} 