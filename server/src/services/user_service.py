from typing import List
from sqlalchemy.orm import Session, joinedload
from src.models.user import User
from src.models.pet import PetProfile

class UserService:
    def get_users(self, db: Session) -> List[User]:
        return db.query(User).all()

    def get_user(self, db: Session, customer_key: int) -> User | None:
        return (
            db.query(User)
              .options(joinedload(User.pets))
              .filter(User.customer_key == customer_key)
              .one_or_none()
        )

    def create_user(self, db: Session, user_data: User) -> User:
        db.add(user_data)
        db.commit()
        db.refresh(user_data)
        return user_data

    def update_user(self, db: Session, customer_key: int, user_data: User) -> User | None:
        user = db.query(User).filter(User.customer_key == customer_key).one_or_none()
        if not user:
            return None
        for attr, value in vars(user_data).items():
            if attr.startswith('_') or attr == 'customer_key':
                continue
            setattr(user, attr, value)
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, customer_key: int) -> bool:
        user = db.query(User).filter(User.customer_key == customer_key).one_or_none()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

    def get_pets_by_user(self, db: Session, customer_key: int) -> List[PetProfile]:
        # First get the user to find their customer_id
        user = db.query(User).filter(User.customer_key == customer_key).one_or_none()
        if not user:
            return []
        
        # Then find pets using the customer_id
        return (
            db.query(PetProfile)
              .filter(PetProfile.customer_id == user.customer_id)
              .all()
        )
    
    def authenticate_user(self, db: Session, email: str, password: str) -> User | None:
        user = db.query(User).filter(User.email == email).one_or_none()
        # if not user or user.password != password:
        #     return None
        # Temporary authentication so we don't need passwords for now
        if not user:
            return None
        return user

    def get_user_context_for_chat(self, db: Session, customer_key: int) -> dict | None:
        """Get user and pet information formatted for chat context"""
        user = self.get_user(db, customer_key)
        if not user:
            return None
        
        user_context = {
            "user_id": user.customer_key,
            "name": user.name,
            "email": user.email,
            "location": {
                "city": user.customer_address_city,
                "state": user.customer_address_state,
                "zip": user.customer_address_zip
            },
            "pets": [],
            # Add persona data
            "persona_summary": user.persona_summary,
            "preferred_brands": user.preferred_brands,
            "special_diet": user.special_diet,
            "possible_next_buys": user.possible_next_buys,
        }
        
        # Add pet information
        pets = self.get_pets_by_user(db, customer_key)
        for pet in pets:
            pet_info = {
                "pet_profile_id": pet.pet_profile_id,
                "name": pet.pet_name,
                "type": pet.pet_type,
                "breed": pet.pet_breed,
                "size": pet.pet_breed_size_type or pet.size_type,
                "weight": pet.weight,
                "life_stage": pet.life_stage,
                "gender": pet.gender,
                "age_months": self._calculate_age_months(pet.birthday) if pet.birthday else None,
                "allergies": pet.allergies or "",
                "is_new": pet.pet_new,
                "status": pet.status
            }
            user_context["pets"].append(pet_info)
        
        return user_context
    
    def _calculate_age_months(self, birthday) -> int:
        """Calculate pet age in months"""
        from datetime import date
        if not birthday:
            return None
        
        today = date.today()
        months = (today.year - birthday.year) * 12 + (today.month - birthday.month)
        return max(0, months)
    
    def format_pet_context_for_ai(self, user_context: dict) -> str:
        """Format user and pet information for AI context"""
        if not user_context:
            return ""
        
        context_parts = []
        
        # Always include basic customer info
        context_parts.append(f"Customer: {user_context['name']}")
        
        if user_context.get("location", {}).get("state"):
            context_parts.append(f"Location: {user_context['location']['city']}, {user_context['location']['state']}")
        
        # Add persona information if available
        if user_context.get("persona_summary"):
            context_parts.append(f"Customer Profile: {user_context['persona_summary']}")
        
        if user_context.get("special_diet"):
            try:
                import json
                special_diet_list = json.loads(user_context['special_diet'])
                if special_diet_list:
                    context_parts.append(f"Dietary Preferences: {', '.join(special_diet_list)}")
            except (json.JSONDecodeError, TypeError):
                pass
        
        if user_context.get("preferred_brands"):
            try:
                import json
                preferred_brands_list = json.loads(user_context['preferred_brands'])
                if preferred_brands_list:
                    context_parts.append(f"Preferred Brands: {', '.join(preferred_brands_list)}")
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Add pet information if available
        pets = user_context.get("pets", [])
        if pets:
            context_parts.append(f"The user is currently signed in and has these pets. Talk to the user about their pets and ask if they are shopping for them to further enhance and refine their searches.")
            context_parts.append(f"Pets ({len(pets)}):")
            
            for i, pet in enumerate(pets, 1):
                pet_desc = [f"Pet {i}:"]
                
                # Basic info
                if pet['name']:
                    pet_desc.append(f"Name: {pet['name']}")
                
                # Type and breed
                if pet['breed'] and pet['breed'] != pet['type']:
                    pet_desc.append(f"Breed: {pet['breed']} {pet['type']}")
                elif pet['type']:
                    pet_desc.append(f"Type: {pet['type']}")
                
                # Age and life stage
                if pet['age_months']:
                    years = pet['age_months'] // 12
                    months = pet['age_months'] % 12
                    if years > 0 and months > 0:
                        pet_desc.append(f"Age: {years}yr {months}mo old")
                    elif years > 0:
                        pet_desc.append(f"Age: {years} years old")
                    else:
                        pet_desc.append(f"Age: {months} months old")
                
                if pet['life_stage'] and pet['life_stage'].lower() != 'unknown':
                    pet_desc.append(f"Life Stage: {pet['life_stage']}")
                
                # Size and weight
                if pet['size'] and pet['size'].lower() != 'unknown':
                    pet_desc.append(f"Size: {pet['size']}")
                if pet['weight'] and pet['weight'] > 0:
                    pet_desc.append(f"Weight: {pet['weight']}lbs")
                
                # Special conditions
                if pet['allergies']:
                    pet_desc.append("Conditions: Has allergies")
                if pet['is_new']:
                    pet_desc.append("Status: New pet")
                
                context_parts.append("\n".join(pet_desc))
        else:
            context_parts.append("The user is currently signed in but doesn't have any pets registered yet.")
        
        return "\n".join(context_parts)

