from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import Product as ProductSchema, SearchResponse
from src.models.product import Product
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])
product_svc = ProductService()

@router.get("/search", response_model=SearchResponse)
async def search_products(
    query: str = Query(..., description="Search query"),
    limit: int = Query(30, description="Maximum number of results to return"),
    include_search_matches: bool = Query(True, description="Include search match analysis (slower but more detailed)")
):
    """Search products using semantic search with embeddings and return both products and AI reply"""
    return await product_svc.search_products(query, limit, include_search_matches)

@router.get("/search/fast", response_model=SearchResponse)
async def search_products_fast(
    query: str = Query(..., description="Search query"),
    limit: int = Query(30, description="Maximum number of results to return")
):
    """Fast product search without search match analysis for better response times"""
    return await product_svc.search_products(query, limit, include_search_matches=False)

@router.get("/search/stats", response_model=Dict)
async def get_search_stats(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """Get search statistics including matched criteria and terms for filtering"""
    products = await product_svc.search_products(query, limit)
    
    # Collect all unique matched criteria and terms
    all_matched_criteria = set()
    criteria_counts = {}
    
    for product in products:
        if product.search_matches:
            for match in product.search_matches:
                # Track the actual search criteria that matched
                for term in match.matched_terms:
                    all_matched_criteria.add(term)
                    criteria_counts[term] = criteria_counts.get(term, 0) + 1
    
    return {
        "total_products": len(products),
        "matched_criteria": list(all_matched_criteria),
        "term_counts": criteria_counts,
        "products_with_matches": len([p for p in products if p.search_matches])
    }

@router.get("/search/terms", response_model=Dict)
async def get_available_search_terms():
    """Get all available search terms extracted from the database"""
    return {
        "metadata_filters": {
            category: list(filters.values())[0] if filters else []
            for category, filters in product_svc.search_analyzer.metadata_filters.items()
        },
        "total_terms": sum(len(list(filters.values())[0]) if filters else 0 
                          for filters in product_svc.search_analyzer.metadata_filters.values())
    }

@router.get("/search/brands", response_model=Dict)
async def get_available_brands():
    """Get all discovered brands from the database"""
    brands = list(product_svc.search_analyzer.metadata_filters['brands']['all'])
    return {
        "brands": sorted(brands),
        "total_brands": len(brands)
    }

@router.get("/search/categories", response_model=Dict)
async def get_available_categories():
    """Get all discovered categories from the database"""
    categories = list(product_svc.search_analyzer.metadata_filters['categories']['all'])
    return {
        "categories": sorted(categories),
        "total_categories": len(categories)
    }

@router.get("/search/fields", response_model=Dict)
async def get_searchable_fields():
    """Get summary of searchable metadata fields"""
    return {
        "searchable_fields": ["brands", "categories", "ingredients", "diet_tags", "pet_attributes"],
        "total_products_analyzed": 10000,
        "cache_status": "Using metadata-driven discovery"
    }

@router.get("/{product_id}", response_model=ProductSchema)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    prod = await product_svc.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod