import { Product } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const api = {
  async searchProducts(query: string, limit: number = 10): Promise<{products: Product[]}> {
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
  },

  async compareProducts(message: string, products: Product[], history: any[] = []): Promise<string> {
    const payload = {
      message,
      products,
      history,
    };
    
    const response = await fetch(`${API_BASE_URL}/chats/compare`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error text:', errorText);
      throw new ApiError(response.status, `Failed to compare products: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response;
  },

  async askAboutProduct(message: string, product: Product, history: any[] = []): Promise<string> {
    const payload = {
      message,
      product,
      history,
    };
    
    const response = await fetch(`${API_BASE_URL}/chats/ask_about_product`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error text:', errorText);
      throw new ApiError(response.status, `Failed to ask about product: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response;
  },

  async chatbot(message: string, history: any[] = [], customer_key?: number): Promise<{message: string, history: any[], products: any[]}> {
    const payload = {
      message,
      history,
      customer_key,
    };
    
    const response = await fetch(`${API_BASE_URL}/chats/chatbot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error text:', errorText);
      throw new ApiError(response.status, `Failed to get chatbot response: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response;
  },

  async searchAndChat(query: string, customer_key?: number): Promise<{searchResults: {products: Product[], reply: string}, chatResponse: {message: string, history: any[], products: any[]}}> {
    // COMMENTED OUT: Old approach that called both search and chat endpoints
    // const [searchResults, chatResponse] = await Promise.all([
    //   this.searchProducts(query, 30),
    //   this.chatbot(query, [], customer_key, true) // skip_products = true
    // ]);

    // NEW APPROACH: Only use chat endpoint for search queries
    // This will show "Searching for: {query}" and return products + follow-ups
    const chatResponse = await this.chatbot(query, [], customer_key);

    return {
      searchResults: { products: chatResponse.products || [], reply: "" },
      chatResponse
    };
  },

  async getPersonalizedGreeting(customer_key?: number): Promise<{greeting: string}> {
    const payload = {
      customer_key,
    };
    
    const response = await fetch(`${API_BASE_URL}/chats/personalized_greeting`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error text:', errorText);
      throw new ApiError(response.status, `Failed to get personalized greeting: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response;
  },

  async getUserPets(customer_key: number): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/customers/${customer_key}/pets`);

    if (!response.ok) {
      throw new ApiError(response.status, `Failed to get user pets: ${response.statusText}`);
    }

    return response.json();
  },
};