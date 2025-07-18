// Cart API - handles cart operations

import { Cart, CartItem, Product } from '../../types';
import { apiGet, apiPost, apiPut, apiDelete } from './client';

export const cartApi = {
  // Get user's cart
  async getCart(userId?: number): Promise<Cart> {
    const endpoint = userId ? `/cart/${userId}` : '/cart';
    return apiGet<Cart>(endpoint);
  },

  // Add item to cart
  async addToCart(productId: number, quantity: number = 1, purchaseOption: 'buyonce' | 'autoship' = 'buyonce', userId?: number): Promise<CartItem> {
    const payload = {
      productId,
      quantity,
      purchaseOption,
      userId,
    };
    
    return apiPost<CartItem>('/cart/items', payload);
  },

  // Update cart item quantity
  async updateCartItem(itemId: string, quantity: number): Promise<CartItem> {
    const payload = { quantity };
    return apiPut<CartItem>(`/cart/items/${itemId}`, payload);
  },

  // Remove item from cart
  async removeFromCart(itemId: string): Promise<void> {
    return apiDelete<void>(`/cart/items/${itemId}`);
  },

  // Clear entire cart
  async clearCart(userId?: number): Promise<void> {
    const endpoint = userId ? `/cart/${userId}/clear` : '/cart/clear';
    return apiPost<void>(endpoint, {});
  },

  // Apply coupon or discount
  async applyCoupon(couponCode: string, userId?: number): Promise<Cart> {
    const payload = { couponCode, userId };
    return apiPost<Cart>('/cart/coupon', payload);
  },

  // Calculate shipping
  async calculateShipping(zipCode: string, userId?: number): Promise<{ shippingCost: number; estimatedDelivery: string }> {
    const payload = { zipCode, userId };
    return apiPost<{ shippingCost: number; estimatedDelivery: string }>('/cart/shipping', payload);
  },

  // Create checkout session
  async createCheckoutSession(userId?: number): Promise<{ checkoutUrl: string; sessionId: string }> {
    const payload = { userId };
    return apiPost<{ checkoutUrl: string; sessionId: string }>('/cart/checkout', payload);
  }
};
