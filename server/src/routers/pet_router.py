# Pet router - handles pet profile management
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import PetProfile as PetSchema, User as UserSchema
from src.services.pet_service import PetService
from src.models.pet import PetProfile

router = APIRouter(prefix="/pets", tags=["pets"])
pet_svc = PetService()

@router.get("/", response_model=List[PetSchema])
def list_pets(db: Session = Depends(get_db)):
    # Get all pet profiles
    return pet_svc.get_pet_profiles(db)

@router.get("/{pet_profile_id}", response_model=PetSchema)
def get_pet(pet_profile_id: int, db: Session = Depends(get_db)):
    # Get a specific pet by ID
    pet = pet_svc.get_pet_profile(db, pet_profile_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

@router.get("/{pet_profile_id}/owner", response_model=UserSchema)
def read_pet_owner(pet_profile_id: int, db: Session = Depends(get_db)):
    # Get the owner of a specific pet
    owner = pet_svc.get_pet_owner(db, pet_profile_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    return owner

@router.post("/", response_model=PetSchema)
def create_pet(profile: PetSchema, db: Session = Depends(get_db)):
    # Create a new pet profile
    return pet_svc.create_pet(db, PetProfile(**profile.dict()))

@router.put("/{pet_profile_id}", response_model=PetSchema)
def update_pet(pet_profile_id: int, profile: PetSchema, db: Session = Depends(get_db)):
    # Update an existing pet profile
    updated = pet_svc.update_pet(db, pet_profile_id, PetProfile(**profile.dict()))
    if not updated:
        raise HTTPException(status_code=404, detail="Pet not found")
    return updated

@router.delete("/{pet_profile_id}")
def delete_pet(pet_profile_id: int, db: Session = Depends(get_db)):
    # Delete a pet profile
    success = pet_svc.delete_pet(db, pet_profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"detail": "Deleted"}