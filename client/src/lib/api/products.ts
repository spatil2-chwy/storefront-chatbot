// Products API - handles product search, details, and comparisons

import { Product } from '../../types';
import { apiGet, apiPost } from './client';

export const productsApi = {
  // Search for products by query
  async searchProducts(query: string, limit: number = 10): Promise<{products: Product[]}> {
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('limit', limit.toString());
    
    return apiGet<{products: Product[]}>(`/products/search?${params.toString()}`);
  },

  // Get search statistics
  async getSearchStats(query: string, limit: number = 10): Promise<any> {
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('limit', limit.toString());
    
    return apiGet<any>(`/products/search/stats?${params.toString()}`);
  },

  // Get single product details
  async getProduct(productId: number): Promise<Product> {
    return apiGet<Product>(`/products/${productId}`);
  },

  // Compare multiple products
  async compareProducts(message: string, products: Product[], history: any[] = []): Promise<string> {
    const payload = {
      message,
      products,
      history,
    };
    
    const response = await apiPost<{response: string}>(`/chats/compare`, payload);
    return response.response;
  },

  // Ask about a specific product
  async askAboutProduct(message: string, product: Product, history: any[] = []): Promise<string> {
    const payload = {
      message,
      product,
      history,
    };
    
    const response = await apiPost<{response: string}>(`/chats/ask_about_product`, payload);
    return response.response;
  }
}; 