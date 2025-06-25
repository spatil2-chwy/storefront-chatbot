from pydantic import BaseModel, EmailStr
from datetime import datetime

class User(BaseModel):
    customer_key: int
    customer_id: int
    operating_revenue_trailing_365: float
    customer_order_first_placed_dttm: datetime
    customer_address_zip: str
    customer_address_city: str
    customer_address_state: str

class UserCreate(BaseModel):
    customer_key: int
    customer_id: int
    operating_revenue_trailing_365: float
    customer_order_first_placed_dttm: datetime
    customer_address_zip: str
    customer_address_city: str
    customer_address_state: str
