// Chat API - handles chatbot conversations and streaming

import { Product, PetOption, PetProfileInfo } from '../../types';
import { apiPost, apiRequest, apiGet, apiPut } from './client';

export const chatApi = {
  // Send message to chatbot
  async chatbot(
    message: string, 
    history: any[] = [], 
    customer_key?: number,
    image?: string // Base64 encoded image
  ): Promise<{message: string, history: any[], products: any[]}> {
    const payload = {
      message,
      history,
      customer_key,
      image, // Include image in payload
    };
    
    const response = await apiPost<{response: {message: string, history: any[], products: any[]}}>(
      `/chats/chatbot`, 
      payload
    );
    return response.response;
  },

  // Stream chatbot responses in real-time
  async chatbotStream(
    message: string, 
    history: any[] = [], 
    customer_key?: number,
    onChunk?: (chunk: string) => void,
    onProducts?: (products: any[]) => void,
    onComplete?: (fullMessage: string, products?: any[]) => void,
    onError?: (error: string) => void,
    image?: string, // Base64 encoded image
    selectedPet?: PetProfileInfo // Selected pet context
  ): Promise<void> {
    const payload = {
      message,
      history,
      customer_key,
      image, // Include image in payload
      selected_pet: selectedPet, // Include selected pet context
    };

    // Use centralized API client for consistency
    const response = await apiRequest('/chats/chatbot/stream', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    if (!response.body) {
      throw new Error('No response body for streaming');
    }

    // Set up streaming reader and decoder
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullMessage = '';
    let products: any[] = [];
    let buffer = ''; // Buffer for incomplete chunks

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value);
        buffer += chunk;
        const lines = buffer.split('\n');

        // Keep the last line in buffer if it's incomplete
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6);
              if (!jsonStr.trim()) continue; // Skip empty data lines

              const data = JSON.parse(jsonStr);

              // Handle different types of streaming events
              if (data.chunk) {
                fullMessage += data.chunk;
                onChunk?.(data.chunk);
              } else if (data.end) {
                onComplete?.(fullMessage, products);
                return;
              } else if (data.products) {
                products = data.products || [];
                onProducts?.(products);
              } else if (data.error) {
                onError?.(data.error);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },

  // Get personalized greeting with pet options
  async getPersonalizedGreeting(customer_key?: number): Promise<{
    greeting: string;
    has_pets: boolean;
    pet_options: PetOption[];
  }> {
    const payload = {
      customer_key,
    };
    
    const response = await apiPost<{response: {
      greeting: string;
      has_pets: boolean;
      pet_options: PetOption[];
    }}>(
      `/chats/personalized_greeting`, 
      payload
    );
    return response.response;
  },

  // Select a pet for shopping
  async selectPet(customer_key: number, pet_id: string): Promise<{
    type: 'browse' | 'pet_profile';
    message?: string;
    pet_context?: string;
    pet_info?: PetProfileInfo;
  }> {
    const payload = {
      customer_key,
      pet_id,
    };
    
    const response = await apiPost<{response: {
      type: 'browse' | 'pet_profile';
      message?: string;
      pet_context?: string;
      pet_info?: PetProfileInfo;
    }}>(
      `/chats/select_pet`, 
      payload
    );
    return response.response;
  },

  // Get pet profile for editing
  async getPetProfile(pet_profile_id: number): Promise<{
    pet_info: PetProfileInfo;
  }> {
    const response = await apiGet<{response: {
      pet_info: PetProfileInfo;
    }}>(
      `/chats/pet_profile/${pet_profile_id}`
    );
    return response.response;
  },

  // Update pet profile
  async updatePetProfile(pet_profile_id: number, pet_data: Partial<PetProfileInfo>): Promise<{
    type: 'pet_updated';
    pet_info: PetProfileInfo;
    pet_context: string;
  }> {
    const response = await apiPut<{response: {
      type: 'pet_updated';
      pet_info: PetProfileInfo;
      pet_context: string;
    }}>(
      `/chats/pet_profile/${pet_profile_id}`,
      pet_data
    );
    return response.response;
  }
}; 