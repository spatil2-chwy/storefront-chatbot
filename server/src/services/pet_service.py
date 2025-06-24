from typing import Dict, List, Optional
from datetime import datetime
import uuid
from src.models.pet import PetProfile

class PetService:
    def __init__(self):
        self.profiles: Dict[int, PetProfile] = {}
        self._init_dummy()
        # next ID is one higher than max existing
        self._next_id = max(self.profiles.keys(), default=0) + 1

    def _init_dummy(self):
        # example dummy
        now = datetime.now()
        dummy = PetProfile(
            pet_profile_id=1,
            customer_id=1,
            pet_name="Fido",
            pet_type="Dog",
            status="active",
            time_created=now
        )
        self.profiles[dummy.pet_profile_id] = dummy

    async def get_pet_profiles(self, customer_id: Optional[int] = None) -> List[PetProfile]:
        if customer_id is None:
            return list(self.profiles.values())
        return [p for p in self.profiles.values() if p.customer_id == customer_id]

    async def get_pet_profile(self, pet_profile_id: int) -> Optional[PetProfile]:
        return self.profiles.get(pet_profile_id)

    async def create_pet_profile(self, data: PetProfile) -> PetProfile:
        pid = self._next_id
        self._next_id += 1
        now = datetime.now()
        profile = data.copy(update={
            "pet_profile_id": pid,
            "time_created": now,
            "time_updated": None
        })
        self.profiles[pid] = profile
        return profile

    async def update_pet_profile(self, pet_profile_id: int, data: PetProfile) -> Optional[PetProfile]:
        existing = self.profiles.get(pet_profile_id)
        if not existing:
            return None
        now = datetime.now()
        updated = existing.copy(update={**data.dict(exclude_unset=True), "time_updated": now})
        self.profiles[pet_profile_id] = updated
        return updated

    async def delete_pet_profile(self, pet_profile_id: int) -> bool:
        return self.profiles.pop(pet_profile_id, None) is not None