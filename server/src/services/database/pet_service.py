from typing import List
from sqlalchemy.orm import Session, joinedload
from src.models.pet import PetProfile
from src.models.user import User

class PetService:
    """
    Service class for managing pet profile operations in the database.
    Provides methods for creating, retrieving, updating, and deleting pet profiles.
    """
    
    def get_pet_profiles(self, db: Session) -> List[PetProfile]:
        """
        Retrieve all pet profiles from the database.
        
        Args:
            db (Session): Database session
        
        Returns:
            List[PetProfile]: List of all pet profiles
        """
        return db.query(PetProfile).all()

    def get_pet_profile(self, db: Session, pet_profile_id: int) -> PetProfile | None:
        """
        Retrieve a pet profile by its ID.
        
        Args:
            db (Session): Database session
            pet_profile_id (int): ID of the pet profile to retrieve
        
        Returns:
            PetProfile | None: The pet profile if found, None otherwise
        """
        return (
            db.query(PetProfile)
              .filter(PetProfile.pet_profile_id == pet_profile_id)
              .one_or_none()
        )

    def get_pet_owner(self, db: Session, pet_profile_id: int) -> User | None:
        """
        Retrieve the owner of a pet profile.
        
        Args:
            db (Session): Database session
            pet_profile_id (int): ID of the pet profile
        
        Returns:
            User | None: The pet's owner if found, None otherwise
        """
        pet = (
            db.query(PetProfile)
              .options(joinedload(PetProfile.owner))
              .filter(PetProfile.pet_profile_id == pet_profile_id)
              .one_or_none()
        )
        return pet.owner if pet else None

    def create_pet(self, db: Session, profile: PetProfile) -> PetProfile:
        """
        Create a new pet profile in the database.
        
        Args:
            db (Session): Database session
            profile (PetProfile): Pet profile to create
        
        Returns:
            PetProfile: The created pet profile
        """
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def update_pet(self, db: Session, pet_profile_id: int, profile: PetProfile) -> PetProfile | None:
        """
        Update an existing pet profile.
        
        Args:
            db (Session): Database session
            pet_profile_id (int): ID of the pet profile to update
            profile (PetProfile): Updated pet profile data
        
        Returns:
            PetProfile | None: The updated pet profile if found, None otherwise
        """
        pet = db.query(PetProfile).filter(PetProfile.pet_profile_id == pet_profile_id).one_or_none()
        if not pet:
            return None
        for attr, value in vars(profile).items():
            if attr.startswith('_') or attr == 'pet_profile_id':
                continue
            setattr(pet, attr, value)
        db.commit()
        db.refresh(pet)
        return pet

    def delete_pet(self, db: Session, pet_profile_id: int) -> bool:
        """
        Delete a pet profile from the database.
        
        Args:
            db (Session): Database session
            pet_profile_id (int): ID of the pet profile to delete
        
        Returns:
            bool: True if the pet was deleted, False if not found
        """
        pet = db.query(PetProfile).filter(PetProfile.pet_profile_id == pet_profile_id).one_or_none()
        if not pet:
            return False
        db.delete(pet)
        db.commit()
        return True