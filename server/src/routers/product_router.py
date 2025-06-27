from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import Product as ProductSchema
from src.models.product import Product
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])
product_svc = ProductService()

@router.get("/search", response_model=List[Product])
async def search_products(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """Search products using semantic search with embeddings"""
    return await product_svc.search_products(query, limit)

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
    return product_svc.search_analyzer.get_available_terms()

@router.get("/search/fields", response_model=Dict)
async def get_searchable_fields():
    """Get all searchable fields discovered in the database"""
    return {
        "searchable_fields": product_svc.search_analyzer.get_searchable_fields(),
        "field_analysis": product_svc.search_analyzer.available_fields
    }

@router.get("/search/categories", response_model=Dict)
async def get_category_context():
    """Get complete category context analysis from the actual database"""
    return {
        "category_context": product_svc.search_analyzer.get_category_context(),
        "summary": {
            "total_categories": len(product_svc.search_analyzer.category_context.get('exact_categories', [])),
            "category_fields": list(product_svc.search_analyzer.category_context.get('category_fields', {}).keys()),
            "pet_types_found": list(product_svc.search_analyzer.category_context.get('category_pet_mapping', {}).keys()),
            "most_common_keywords": list(product_svc.search_analyzer.category_context.get('category_patterns', {}).get('common_keywords', {}).keys())[:10]
        }
    }

@router.get("/{product_id}", response_model=ProductSchema)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    prod = await product_svc.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.get("/products/search/patterns")
async def get_search_patterns():
    """Get the dynamically discovered search patterns"""
    try:
        from src.services.search_analyzer import SearchAnalyzer
        analyzer = SearchAnalyzer()
        
        summary = analyzer.get_discovered_patterns_summary()
        
        # Get detailed patterns for the response
        patterns = {
            "summary": summary,
            "brands": dict(list(analyzer.brand_patterns.items())[:20]),  # Top 20 brands
            "product_types": analyzer.product_type_patterns,
            "diet_patterns": dict(list(analyzer.diet_patterns.items())[:15]),  # Top 15 diet patterns
            "health_concerns": analyzer.health_concern_patterns,
            "forms": analyzer.form_patterns,
            "flavors": analyzer.flavor_patterns
        }
        
        return {
            "status": "success",
            "message": "Search patterns retrieved successfully",
            "data": patterns
        }
        
    except Exception as e:
        print(f"Error getting search patterns: {e}")
        return {
            "status": "error", 
            "message": f"Failed to get search patterns: {str(e)}",
            "data": {}
        }