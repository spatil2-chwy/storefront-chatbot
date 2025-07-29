// Users API - handles user profiles and pets

import { apiGet, apiPost, apiDelete } from './client';
import { Pet } from '../../types';

export const usersApi = {
  // Get all pets for a user
  async getUserPets(customerKey: number): Promise<Pet[]> {
    console.log('usersApi.getUserPets: Called with customerKey:', customerKey);
    const result = await apiGet<Pet[]>(`/customers/${customerKey}/pets`);
    console.log('usersApi.getUserPets: Received result:', result);
    return result;
  },

  // Create a new pet
  async createPet(customerKey: number, petData: {
    pet_name: string;
    pet_type: string;
    pet_breed?: string;
    gender?: string;
    weight?: number;
    life_stage?: string;
    birthday?: string;
    allergies?: string;
  }): Promise<Pet> {
    console.log('usersApi.createPet: Called with customerKey:', customerKey, 'petData:', petData);
    
    // Create payload with minimal temporary ID to let database auto-generate
    const payload = {
      pet_profile_id: 1, // Minimal temporary ID
      customer_id: customerKey,
      pet_name: petData.pet_name,
      pet_type: petData.pet_type,
      pet_breed: petData.pet_breed || null,
      pet_breed_size_type: null,
      gender: petData.gender || null,
      weight_type: null,
      size_type: null,
      birthday: petData.birthday || null,
      life_stage: petData.life_stage || null,
      adopted: null,
      adoption_date: null,
      status: "active",
      status_reason: null,
      time_created: new Date().toISOString(),
      time_updated: null,
      weight: petData.weight ? Math.round(petData.weight) : null,
      allergies: petData.allergies || null,
      photo_count: null,
      pet_breed_id: null,
      pet_type_id: null,
      pet_new: null,
      first_birthday: null
    };
    
    console.log('usersApi.createPet: Sending payload:', payload);
    const result = await apiPost<Pet>(`/pets`, payload);
    console.log('usersApi.createPet: Received result:', result);
    return result;
  },

  // Delete a pet
  async deletePet(petId: number): Promise<void> {
    return apiDelete<void>(`/pets/${petId}`);
  }
}; 