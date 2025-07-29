from typing import List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from src.models.pet import PetProfile
from src.models.user import User

class PetService:
    def get_pet_profiles(self, db: Session) -> List[PetProfile]:
        return db.query(PetProfile).all()

    def get_pet_profile(self, db: Session, pet_profile_id: int) -> PetProfile | None:
        return (
            db.query(PetProfile)
              .filter(PetProfile.pet_profile_id == pet_profile_id)
              .one_or_none()
        )

    def get_pet_owner(self, db: Session, pet_profile_id: int) -> User | None:
        pet = (
            db.query(PetProfile)
              .options(joinedload(PetProfile.owner))
              .filter(PetProfile.pet_profile_id == pet_profile_id)
              .one_or_none()
        )
        return pet.owner if pet else None

    def create_pet(self, db: Session, profile: PetProfile) -> PetProfile:
        # Ensure time_created is set if not provided
        if not profile.time_created:
            profile.time_created = datetime.utcnow()
        
        try:
            db.add(profile)
            db.commit()
            
            # Query the database to get the created pet with its ID
            created_pet = db.query(PetProfile).filter(
                PetProfile.customer_id == profile.customer_id,
                PetProfile.pet_name == profile.pet_name,
                PetProfile.pet_type == profile.pet_type,
                PetProfile.time_created == profile.time_created
            ).order_by(PetProfile.pet_profile_id.desc()).first()
            
            if created_pet:
                return created_pet
            else:
                raise Exception("Failed to retrieve created pet from database")
                
        except Exception as e:
            db.rollback()
            raise

    def update_pet(self, db: Session, pet_profile_id: int, profile: PetProfile) -> PetProfile | None:
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
        pet = db.query(PetProfile).filter(PetProfile.pet_profile_id == pet_profile_id).one_or_none()
        if not pet:
            return False
        db.delete(pet)
        db.commit()
        return True