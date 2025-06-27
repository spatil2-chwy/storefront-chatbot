import { Product } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const api = {
  async searchProducts(query: string, limit: number = 10): Promise<Product[]> {
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('limit', limit.toString());

    const response = await fetch(`${API_BASE_URL}/products/search?${params.toString()}`);
    
    if (!response.ok) {
      throw new ApiError(response.status, `Failed to search products: ${response.statusText}`);
    }

    return response.json();
  },

  async getSearchStats(query: string, limit: number = 10): Promise<any> {
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('limit', limit.toString());

    const response = await fetch(`${API_BASE_URL}/products/search/stats?${params.toString()}`);
    
    if (!response.ok) {
      throw new ApiError(response.status, `Failed to get search stats: ${response.statusText}`);
    }

    return response.json();
  },

  async getProduct(productId: number): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new ApiError(404, 'Product not found');
      }
      throw new ApiError(response.status, `Failed to fetch product: ${response.statusText}`);
    }

    return response.json();
  }
}; 