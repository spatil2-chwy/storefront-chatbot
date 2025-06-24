from fastapi import APIRouter, HTTPException
from ..models.user import User, UserCreate
from storage import storage

router = APIRouter()

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = await storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/email/{email}", response_model=User)
async def get_user_by_email(email: str):
    user = await storage.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    existing_user = await storage.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    return await storage.create_user(user_data)
