from fastapi import APIRouter, HTTPException
from ..models.user import User, UserCreate
from src.services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.get("/customers/{customer_key}", response_model=User)
async def get_customer(customer_key: int):
    customer = await user_service.get_user(customer_key)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/customers", response_model=User)
async def create_customer(user_data: UserCreate):
    if await user_service.get_user(user_data.customer_key):
        raise HTTPException(status_code=400, detail="Customer with this key already exists")
    return await user_service.create_user(user_data)
