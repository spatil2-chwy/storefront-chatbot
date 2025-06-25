from fastapi import APIRouter, HTTPException
from typing import List, Optional
from src.models.pet import PetProfile
from src.services import pet_service

router = APIRouter(prefix="/pets", tags=["pets"])

@router.get("/", response_model=List[PetProfile])
async def list_pets(customer_id: Optional[int] = None):
    return await pet_service.get_pet_profiles(customer_id)

@router.get("/{pet_profile_id}", response_model=PetProfile)
async def get_pet(pet_profile_id: int):
    pet = await pet_service.get_pet_profile(pet_profile_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

@router.post("/", response_model=PetProfile)
async def create_pet(profile: PetProfile):
    return await pet_service.create_pet_profile(profile)

@router.put("/{pet_profile_id}", response_model=PetProfile)
async def update_pet(pet_profile_id: int, profile: PetProfile):
    updated = await pet_service.update_pet_profile(pet_profile_id, profile)
    if not updated:
        raise HTTPException(status_code=404, detail="Pet not found")
    return updated

@router.delete("/{pet_profile_id}")
async def delete_pet(pet_profile_id: int):
    success = await pet_service.delete_pet_profile(pet_profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"detail": "Deleted"}