// Chat API - handles chatbot conversations and streaming

import { Product } from '../../types';
import { apiPost, apiRequest } from './client';

export const chatApi = {
  // Send message to chatbot
  async chatbot(
    message: string, 
    history: any[] = [], 
    customer_key?: number
  ): Promise<{message: string, history: any[], products: any[]}> {
    const payload = {
      message,
      history,
      customer_key,
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
    onError?: (error: string) => void
  ): Promise<void> {
    const payload = {
      message,
      history,
      customer_key,
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

  // Get personalized greeting
  async getPersonalizedGreeting(customer_key?: number): Promise<{greeting: string}> {
    const payload = {
      customer_key,
    };
    
    const response = await apiPost<{response: {greeting: string}}>(
      `/chats/personalized_greeting`, 
      payload
    );
    return response.response;
  }
}; 