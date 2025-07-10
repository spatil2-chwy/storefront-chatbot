// Users API - handles user profiles and pets

import { apiGet } from './client';

// Pet data structure
export interface Pet {
  pet_profile_id: number;
  pet_name: string;
  pet_type: string;        // "DOG", "CAT", etc.
  pet_breed: string;       // "Golden Retriever", etc.
  gender: string;          // "MALE", "FMLE"
  birthday: string;        // ISO date string
  life_stage: string;      // "P" (puppy), "A" (adult), "S" (senior)
  adopted: boolean;        // Whether pet was adopted
  adoption_date: string | null; // When adopted
  weight: number;          // Weight in pounds
  allergy_count: number;   // Number of allergies
  status: string;          // Current status
}

export const usersApi = {
  // Get all pets for a user
  async getUserPets(customerKey: number): Promise<Pet[]> {
    return apiGet<Pet[]>(`/customers/${customerKey}/pets`);
  }
}; 