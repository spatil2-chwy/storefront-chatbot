// Users API - handles user profiles and pets

import { apiGet } from './client';
import { Pet } from '../../types';

export const usersApi = {
  // Get all pets for a user
  async getUserPets(customerKey: number): Promise<Pet[]> {
    return apiGet<Pet[]>(`/customers/${customerKey}/pets`);
  }
}; 