from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import Product as ProductSchema
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])
product_svc = ProductService()

@router.get("/", response_model=List[ProductSchema])
def list_products(
    category: Optional[str] = Query(None),
    keywords: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    keyword_list = [k.strip() for k in keywords.split(",")] if keywords else None
    return product_svc.list_products(db, category, keyword_list)

@router.get("/{product_id}", response_model=ProductSchema)
def read_product(product_id: int, db: Session = Depends(get_db)):
    prod = product_svc.get_product(db, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.post("/", response_model=ProductSchema)
def create_product(prod_data: ProductSchema, db: Session = Depends(get_db)):
    return product_svc.create_product(db, Product(**prod_data.dict()))