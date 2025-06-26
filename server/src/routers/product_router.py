from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import Product as ProductSchema
from src.models.product import Product
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])
product_svc = ProductService()

@router.get("/products/search", response_model=List[Product])
async def search_products(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """Search products using semantic search with embeddings"""
    return await product_svc.search_products(query, limit)

@router.get("/{product_id}", response_model=ProductSchema)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    prod = await product_svc.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod