from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..models.product import Product
from src.services import product_service

router = APIRouter()

@router.get("/products/search", response_model=List[Product])
async def search_products(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """Search products using semantic search with embeddings"""
    return await product_service.search_products(query, limit)

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get product by ID"""
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
