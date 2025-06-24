from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class PetProfile(BaseModel):
    pet_profile_id: int
    customer_id: int
    pet_name: Optional[str] = None
    pet_type: Optional[str] = None
    pet_breed: Optional[str] = None
    pet_breed_size_type: Optional[str] = None
    gender: Optional[str] = None
    weight_type: Optional[str] = None
    size_type: Optional[str] = None
    birthday: Optional[date] = None
    birthday_estimated: Optional[bool] = None
    life_stage: Optional[str] = None
    adopted: Optional[bool] = None
    adoption_date: Optional[date] = None
    status: str
    status_reason: Optional[str] = None
    time_created: datetime
    time_updated: Optional[datetime] = None
    weight: Optional[int] = None
    allergy_count: Optional[int] = None
    photo_count: Optional[int] = None
    pet_breed_id: Optional[int] = None
    pet_type_id: Optional[int] = None
    pet_new: Optional[bool] = None
    first_birthday: Optional[date] = None

