from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..models.product import Product
from src.services import product_service

router = APIRouter()

@router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    keywords: Optional[str] = Query(None, description="Comma-separated keywords to filter by")
):
    """Get products with optional filtering"""
    keyword_list = [k.strip() for k in keywords.split(",")] if keywords else None
    return await product_service.get_products(category=category, keywords=keyword_list)

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get product by ID"""
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
