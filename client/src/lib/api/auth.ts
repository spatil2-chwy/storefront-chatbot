// Auth API - handles login/logout

import axios from 'axios';

// Use the same User interface as the auth provider
export interface User {
  customer_key: number;
  customer_id: number;
  name: string;
  email: string;
  password: string;
  operating_revenue_trailing_365?: number;
  customer_order_first_placed_dttm?: string;
  customer_address_zip?: string;
  customer_address_city?: string;
  customer_address_state?: string;
}

const API_BASE_URL = 'http://localhost:8000';

export const authApi = {
  // Login user with email/password
  async login(email: string, password: string): Promise<User> {
    const { data } = await axios.post<User>(`${API_BASE_URL}/customers/login`, { 
      email, 
      password 
    });
    return data;
  },

  // Logout user (placeholder for now)
  async logout(): Promise<void> {
    // TODO: Add logout API call when backend supports it
    return Promise.resolve();
  }
}; 