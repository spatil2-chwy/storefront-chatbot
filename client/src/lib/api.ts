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

  async chatbotStream(
    message: string, 
    history: any[] = [], 
    customer_key?: number,
    onChunk?: (chunk: string) => void,
    onComplete?: (fullMessage: string, products?: any[]) => void,
    onError?: (error: string) => void
  ): Promise<void> {
    const payload = {
      message,
      history,
      customer_key,
    };
    
    const response = await fetch(`${API_BASE_URL}/chats/chatbot/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error text:', errorText);
      throw new ApiError(response.status, `Failed to get chatbot stream: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('No response body for streaming');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullMessage = '';
    let products: any[] = [];

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.chunk) {
                fullMessage += data.chunk;
                onChunk?.(data.chunk);
              } else if (data.end) {
                console.log('Streaming completed');
                console.log('Calling onComplete with products:', products);
                console.log('Products length in completion:', products?.length || 0);
                onComplete?.(fullMessage, products);
                return;
              } else if (data.products) {
                console.log('Received products event:', data);
                console.log('Products count:', data.products?.length || 0);
                console.log('Products type:', typeof data.products);
                console.log('Products is array:', Array.isArray(data.products));
                if (data.products && data.products.length > 0) {
                  console.log('First product:', data.products[0]);
                }
                products = data.products || [];
                console.log('Stored products array:', products);
              } else if (data.error) {
                console.error('Streaming error received:', data.error);
                onError?.(data.error);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, 'Line:', line);
              console.error('Raw line content:', line);
              // Try to extract the problematic part
              if (line.length > 6) {
                const jsonPart = line.slice(6);
                console.error('JSON part that failed to parse:', jsonPart.substring(0, 200) + '...');
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
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
};