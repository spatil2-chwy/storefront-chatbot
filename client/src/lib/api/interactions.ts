// Interactions API - handles interaction logging

import { apiPost } from './client';

export interface InteractionRequest {
  customer_key: number;
  event_type: 'purchase' | 'addToCart' | 'productClick';
  item_id?: number;
  event_value?: number;
  product_metadata?: Record<string, any>;
}

export const interactionsApi = {
  // Log an interaction
  async logInteraction(data: InteractionRequest): Promise<{ message: string; interaction_id: number }> {
    return apiPost<{ message: string; interaction_id: number }>('/interactions/log_interaction', data);
  },
}; 