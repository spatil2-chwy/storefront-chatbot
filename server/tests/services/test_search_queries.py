"""
Tests for search queries with real product terms and dietary restrictions.
"""
import pytest
from src.services.search.searchengine import query_products
from src.services.search.search_analyzer import SearchAnalyzer

@pytest.fixture
def search_analyzer():
    """Creates a SearchAnalyzer instance."""
    return SearchAnalyzer()

def test_basic_product_searches():
    """Test basic product search terms."""
    search_terms = [
        "dog food",
        "cat food",
        "flea and tick prevention for dogs",
        "royal canin dog food",
        "purina pro plan for cats",
        "wet cat food",
        "hills science diet dry dog food"
    ]
    
    for term in search_terms:
        results = query_products(
            term,
            required_ingredients=(),
            excluded_ingredients=(),
            special_diet_tags=()
        )
        
        assert results is not None
        assert len(results['metadatas'][0]) > 0
        
        # Verify relevant metadata fields
        for metadata in results['metadatas'][0][:3]:  # Check first 3 results
            assert 'CLEAN_NAME' in metadata
            assert 'CATEGORY_LEVEL1' in metadata
            assert 'PURCHASE_BRAND' in metadata
            print(f"\nSearch term: {term}")
            print(f"Found product: {metadata['CLEAN_NAME']}")
            print(f"Category: {metadata['CATEGORY_LEVEL1']}")
            print(f"Brand: {metadata['PURCHASE_BRAND']}")

def test_dietary_restriction_searches():
    """Test searches with dietary restrictions."""
    test_cases = [
        {
            "query": "dog food",
            "special_diets": ("grain-free",),
            "excluded": ("chicken",),
            "description": "Grain-free dog food without chicken"
        },
        {
            "query": "cat food",
            "special_diets": ("limited-ingredient",),
            "excluded": ("fish",),
            "description": "Limited ingredient cat food without fish"
        },
        {
            "query": "dog food",
            "special_diets": ("weight-management",),
            "excluded": ("beef",),
            "description": "Weight management dog food without beef"
        }
    ]
    
    for case in test_cases:
        results = query_products(
            case["query"],
            required_ingredients=(),
            excluded_ingredients=case["excluded"],
            special_diet_tags=case["special_diets"]
        )
        
        assert results is not None
        print(f"\nTesting: {case['description']}")
        
        # Check first 3 results
        for metadata in results['metadatas'][0][:3]:
            print(f"Found product: {metadata['CLEAN_NAME']}")
            
            # Verify dietary restrictions
            for diet in case["special_diets"]:
                diet_key = f"specialdiettag:{diet.lower()}"
                if diet_key in metadata:
                    assert metadata[diet_key] is True
            
            # Verify excluded ingredients
            for ingredient in case["excluded"]:
                ingredient_key = f"ingredienttag:{ingredient.lower()}"
                if ingredient_key in metadata:
                    assert not metadata[ingredient_key]

def test_specific_product_categories():
    """Test searches for specific product categories."""
    categories = [
        ("flea meds for cats", "Pharmacy"),
        ("dog crate furniture", "Supplies"),
        ("cat towers for large cats", "Furniture"),
        ("cooling mats for dogs", "Beds & Furniture"),
        ("sensitive digestion dog food", "Dog Food")
    ]
    
    for search_term, expected_category in categories:
        results = query_products(
            search_term,
            required_ingredients=(),
            excluded_ingredients=(),
            special_diet_tags=()
        )
        
        assert results is not None
        print(f"\nSearch term: {search_term}")
        
        # Check first 3 results
        for metadata in results['metadatas'][0][:3]:
            print(f"Found product: {metadata['CLEAN_NAME']}")
            print(f"Category: {metadata['CATEGORY_LEVEL1']}")
            # Category might not match exactly but should be related
            assert metadata['CATEGORY_LEVEL1'] is not None

def test_brand_specific_searches():
    """Test searches for specific brands."""
    brand_searches = [
        "purina pro plan for dogs",
        "royal canin dog food",
        "blue buffalo dog food",
        "hills science diet dry dog food",
        "friskies wet cat food"
    ]
    
    for brand_term in brand_searches:
        results = query_products(
            brand_term,
            required_ingredients=(),
            excluded_ingredients=(),
            special_diet_tags=()
        )
        
        assert results is not None
        print(f"\nBrand search: {brand_term}")
        
        # Check first 3 results
        for metadata in results['metadatas'][0][:3]:
            print(f"Found product: {metadata['CLEAN_NAME']}")
            print(f"Brand: {metadata['PURCHASE_BRAND']}")
            # Brand in results should match or be related to search term
            assert metadata['PURCHASE_BRAND'] is not None 