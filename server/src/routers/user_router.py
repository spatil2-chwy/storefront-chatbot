from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import User as UserSchema, UserLogin, PetProfile as PetSchema
from src.services.user_service import UserService
from src.models.user import User

router = APIRouter(prefix="/customers", tags=["customers"])
user_svc = UserService()

@router.get("/", response_model=List[UserSchema])
def list_users(db: Session = Depends(get_db)):
    return user_svc.get_users(db)

@router.get("/{customer_key}", response_model=UserSchema)
def read_user(customer_key: int, db: Session = Depends(get_db)):
    user = user_svc.get_user(db, customer_key)
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    return user

@router.get("/{customer_key}/pets", response_model=List[PetSchema])
def read_user_pets(customer_key: int, db: Session = Depends(get_db)):
    return user_svc.get_pets_by_user(db, customer_key)

@router.post("/", response_model=UserSchema)
def create_user(user_data: UserSchema, db: Session = Depends(get_db)):
    return user_svc.create_user(db, User(**user_data.dict()))

@router.put("/{customer_key}", response_model=UserSchema)
def update_user(customer_key: int, user_data: UserSchema, db: Session = Depends(get_db)):
    updated = user_svc.update_user(db, customer_key, User(**user_data.dict()))
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated

@router.delete("/{customer_key}")
def delete_user(customer_key: int, db: Session = Depends(get_db)):
    success = user_svc.delete_user(db, customer_key)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"detail": "Deleted"}

@router.post("/login", response_model=UserSchema)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = user_svc.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user
