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
  createPet: async (customerKey: number, petData: any): Promise<any> => {
    try {
      // Ensure weight is always included in the payload
      const weight = petData.weight && petData.weight > 0 ? Math.round(petData.weight) : null;
      
      const payload = {
        customer_id: customerKey,
        pet_name: petData.pet_name || null,
        pet_type: petData.pet_type || null,
        pet_breed: petData.pet_breed || null,
        pet_breed_size_type: petData.pet_breed_size_type || null,
        gender: petData.gender || null,
        weight_type: petData.weight_type || null,
        size_type: petData.size_type || null,
        birthday: petData.birthday || null,
        life_stage: petData.life_stage || null,
        adopted: petData.adopted || null,
        adoption_date: petData.adoption_date || null,
        status: "active",
        status_reason: null,
        time_created: new Date().toISOString(),
        time_updated: null,
        weight: weight,
        allergies: petData.allergies || null,
        photo_count: null,
        pet_breed_id: null,
        pet_type_id: null,
        pet_new: null,
        first_birthday: null
      };

      const result = await apiPost("/pets", payload);
      return result;
    } catch (error) {
      console.error("Error creating pet:", error);
      throw error;
    }
  },

  // Delete a pet
  async deletePet(petId: number): Promise<void> {
    return apiDelete<void>(`/pets/${petId}`);
  }
}; 