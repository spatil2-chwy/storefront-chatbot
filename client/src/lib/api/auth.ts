// Auth API - handles login/logout operations

import axios from 'axios';
import { User } from '../../types';

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

  // Refresh user data (including persona updates)
  async refreshUserData(customerKey: number): Promise<User> {
    const { data } = await axios.get<User>(`${API_BASE_URL}/customers/refresh/${customerKey}`);
    return data;
  },

  // Logout user (placeholder for now)
  async logout(): Promise<void> {
    // TODO: Add logout API call when backend supports it
    return Promise.resolve();
  }
}; 