from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from product import Product 
from pet import PetProfile

class User(BaseModel):
    customer_id: str
    operating_revenue: float
    first_placed_order: datetime
    zip_code: str
    city: str
    state: str
    orders: List[Product] = []
    pets: List[PetProfile] = []
