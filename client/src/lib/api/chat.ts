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
    const startTime = performance.now();
    console.log(`🚀 CHAT API CALL START - Message: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`);
    
    const payload = {
      message,
      history,
      customer_key,
    };
    
    try {
      const response = await apiPost<{response: {message: string, history: any[], products: any[]}}>(
        `/chats/chatbot`, 
        payload
      );
      
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.log(`✅ CHAT API CALL COMPLETE - Duration: ${duration.toFixed(0)}ms`);
      
      return response.response;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.error(`❌ CHAT API CALL FAILED - Duration: ${duration.toFixed(0)}ms - Error:`, error);
      throw error;
    }
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
    const startTime = performance.now();
    console.log(`🌊 STREAM API CALL START - Message: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`);
    
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
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.error(`❌ STREAM API CALL FAILED - Duration: ${duration.toFixed(0)}ms - No response body`);
      throw new Error('No response body for streaming');
    }

    // Set up streaming reader and decoder
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullMessage = '';
    let products: any[] = [];
    let buffer = ''; // Buffer for incomplete chunks
    let chunkCount = 0;
    let firstChunkTime: number | null = null;

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
                if (firstChunkTime === null) {
                  firstChunkTime = performance.now();
                  const firstChunkDuration = firstChunkTime - startTime;
                  console.log(`🌊 FIRST CHUNK RECEIVED - Duration: ${firstChunkDuration.toFixed(0)}ms`);
                }
                
                fullMessage += data.chunk;
                chunkCount++;
                onChunk?.(data.chunk);
              } else if (data.end) {
                const endTime = performance.now();
                const duration = endTime - startTime;
                console.log(`✅ STREAM API CALL COMPLETE - Duration: ${duration.toFixed(0)}ms, Chunks: ${chunkCount}`);
                onComplete?.(fullMessage, products);
                return;
              } else if (data.products) {
                products = data.products || [];
                console.log(`📦 PRODUCTS RECEIVED - Count: ${products.length}`);
                onProducts?.(products);
              } else if (data.error) {
                const endTime = performance.now();
                const duration = endTime - startTime;
                console.error(`❌ STREAM API CALL FAILED - Duration: ${duration.toFixed(0)}ms - Error: ${data.error}`);
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
    const startTime = performance.now();
    console.log(`👋 GREETING API CALL START - Customer: ${customer_key}`);
    
    const payload = {
      customer_key,
    };
    
    try {
      const response = await apiPost<{response: {greeting: string}}>(
        `/chats/personalized_greeting`, 
        payload
      );
      
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.log(`✅ GREETING API CALL COMPLETE - Duration: ${duration.toFixed(0)}ms`);
      
      return response.response;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.error(`❌ GREETING API CALL FAILED - Duration: ${duration.toFixed(0)}ms - Error:`, error);
      throw error;
    }
  },

  // Combined search and chat
  async searchAndChat(
    query: string, 
    customer_key?: number
  ): Promise<{searchResults: {products: Product[], reply: string}, chatResponse: {message: string, history: any[], products: any[]}}> {
    const startTime = performance.now();
    console.log(`🔍 SEARCH AND CHAT API CALL START - Query: "${query.substring(0, 50)}${query.length > 50 ? '...' : ''}"`);
    
    try {
      const chatResponse = await this.chatbot(query, [], customer_key);

      const endTime = performance.now();
      const duration = endTime - startTime;
      console.log(`✅ SEARCH AND CHAT API CALL COMPLETE - Duration: ${duration.toFixed(0)}ms`);

      return {
        searchResults: { products: chatResponse.products || [], reply: "" },
        chatResponse
      };
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.error(`❌ SEARCH AND CHAT API CALL FAILED - Duration: ${duration.toFixed(0)}ms - Error:`, error);
      throw error;
    }
  }
}; 