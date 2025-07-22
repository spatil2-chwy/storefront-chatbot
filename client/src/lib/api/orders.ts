import { ApiError, apiGet, apiPost, apiRequest } from './client';

export interface OrderItem {
  product_id: number;
  product_title: string;
  product_brand?: string;
  product_image?: string;
  quantity: number;
  purchase_option: 'buyonce' | 'autoship';
  unit_price: number;
  total_price: number;
}

export interface OrderCreate {
  customer_id: number;
  subtotal: number;
  shipping_cost: number;
  tax_amount: number;
  total_amount: number;
  
  // Shipping Information
  shipping_first_name: string;
  shipping_last_name: string;
  shipping_email: string;
  shipping_phone?: string;
  shipping_address: string;
  shipping_city: string;
  shipping_state: string;
  shipping_zip_code: string;
  
  // Payment Information (masked)
  payment_method: string;
  card_last_four?: string;
  cardholder_name?: string;
  
  // Billing Address (optional)
  billing_address?: string;
  billing_city?: string;
  billing_state?: string;
  billing_zip_code?: string;
  
  items: OrderItem[];
}

export interface Order extends OrderCreate {
  order_id: number;
  status: string;
  order_date: string;
  created_at: string;
  updated_at: string;
}

export interface OrderSummary {
  order_id: number;
  order_date: string;
  status: string;
  total_amount: number;
  items_count: number;
}

// Add apiPatch helper function since it doesn't exist yet
async function apiPatch<T>(endpoint: string, data?: unknown): Promise<T> {
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API request failed: ${response.statusText}`);
  }

  return response.json();
}

export const ordersApi = {
  // Create a new order
  createOrder: async (orderData: OrderCreate): Promise<Order> => {
    try {
      return await apiPost<Order>('/api/orders/', orderData);
    } catch (error: any) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(500, 'Failed to create order');
    }
  },

  // Get order by ID
  getOrder: async (orderId: number): Promise<Order> => {
    try {
      return await apiGet<Order>(`/api/orders/${orderId}`);
    } catch (error: any) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(500, 'Failed to fetch order');
    }
  },

  // Get all orders for a customer
  getCustomerOrders: async (customerId: number): Promise<OrderSummary[]> => {
    try {
      return await apiGet<OrderSummary[]>(`/api/orders/customer/${customerId}`);
    } catch (error: any) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(500, 'Failed to fetch customer orders');
    }
  },

  // Update order status
  updateOrderStatus: async (orderId: number, status: string): Promise<Order> => {
    try {
      return await apiPatch<Order>(`/api/orders/${orderId}/status`, { status });
    } catch (error: any) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(500, 'Failed to update order status');
    }
  }
};
