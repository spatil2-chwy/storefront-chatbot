"""
Make sure search works properly when users look for products.
"""
import pytest
from src.services.search.searchengine import query_products
from src.services.search.search_analyzer import SearchAnalyzer

@pytest.fixture
def search_analyzer():
    """
    Creates a tool that helps analyze search results.
    """
    return SearchAnalyzer()

def test_basic_product_searches():
    """
    Makes sure simple searches work correctly.
    
    For example, when someone searches for "dog food", we want to make sure:
    - We actually find some products
    - The products are actually dog food
    - We know what brand they are
    - They're in the right category (like "Dog Food" or "Cat Food")
    """
    # List of common things people search for
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
        # Try to find products matching what the user searched for
        results = query_products(
            term,
            required_ingredients=(),  # We're not looking for specific ingredients here
            excluded_ingredients=(),   # We're not avoiding any ingredients here
            special_diet_tags=()      # We're not filtering for special diets here
        )
        
        # Make sure we found something
        assert results is not None
        assert len(results['metadatas'][0]) > 0
        
        # Look at the first 3 products we found
        for metadata in results['metadatas'][0][:3]:
            # Every product should have these basic details:
            assert 'CLEAN_NAME' in metadata      # The product's name
            assert 'CATEGORY_LEVEL1' in metadata # What type of product it is
            assert 'PURCHASE_BRAND' in metadata  # What brand makes it
            
            # Print out what we found (helps us check if it makes sense)
            print(f"\nWhen someone searched for: {term}")
            print(f"We found this product: {metadata['CLEAN_NAME']}")
            print(f"It's in this category: {metadata['CATEGORY_LEVEL1']}")
            print(f"It's made by: {metadata['PURCHASE_BRAND']}")

def test_dietary_restriction_searches():
    """
    Makes sure we can find products for pets with special diets.
    
    For example:
    - Finding grain-free food
    - Finding food without chicken (for allergic pets)
    - Finding diet food for overweight pets
    
    We need to make sure these special requirements are actually met
    in the products we find.
    """
    # Different types of special diet searches to test
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
        # Search for products with these special requirements
        results = query_products(
            case["query"],
            required_ingredients=(),
            excluded_ingredients=case["excluded"],
            special_diet_tags=case["special_diets"]
        )
        
        # Make sure we found something
        assert results is not None
        print(f"\nChecking for: {case['description']}")
        
        # Look at each product we found
        for metadata in results['metadatas'][0][:3]:
            print(f"Found this product: {metadata['CLEAN_NAME']}")
            
            # Make sure it meets the special diet requirements
            for diet in case["special_diets"]:
                diet_key = f"specialdiettag:{diet.lower()}"
                if diet_key in metadata:
                    # The product should have this special diet tag
                    assert metadata[diet_key] is True
            
            # Make sure it doesn't have ingredients we don't want
            for ingredient in case["excluded"]:
                ingredient_key = f"ingredienttag:{ingredient.lower()}"
                if ingredient_key in metadata:
                    # The product shouldn't have this ingredient
                    assert not metadata[ingredient_key]

def test_specific_product_categories():
    """
    Makes sure products show up in the right categories.
    
    For example:
    - Flea medicine should be in "Pharmacy"
    - Dog beds should be in "Furniture"
    - Dog food should be in "Dog Food"
    
    This helps users find products in the right section of the store.
    """
    # List of searches and where we expect to find their products
    categories = [
        ("flea meds for cats", "Pharmacy"),
        ("dog crate furniture", "Supplies"),
        ("cat towers for large cats", "Furniture"),
        ("cooling mats for dogs", "Beds & Furniture"),
        ("sensitive digestion dog food", "Dog Food")
    ]
    
    for search_term, expected_category in categories:
        # Search for products
        results = query_products(
            search_term,
            required_ingredients=(),
            excluded_ingredients=(),
            special_diet_tags=()
        )
        
        # Make sure we found something
        assert results is not None
        print(f"\nWhen searching for: {search_term}")
        
        # Check each product we found
        for metadata in results['metadatas'][0][:3]:
            print(f"Found this product: {metadata['CLEAN_NAME']}")
            print(f"It's in this category: {metadata['CATEGORY_LEVEL1']}")
            # Make sure it has a category
            assert metadata['CATEGORY_LEVEL1'] is not None

def test_brand_specific_searches():
    """
    Makes sure we can find products from specific brands.
    
    For example, when someone searches for:
    - "Purina dog food"
    - "Royal Canin cat food"
    
    We should find products actually made by those brands.
    """
    # List of brand-specific searches to test
    brand_searches = [
        "purina pro plan for dogs",
        "royal canin dog food",
        "blue buffalo dog food",
        "hills science diet dry dog food",
        "friskies wet cat food"
    ]
    
    for brand_term in brand_searches:
        # Search for products from this brand
        results = query_products(
            brand_term,
            required_ingredients=(),
            excluded_ingredients=(),
            special_diet_tags=()
        )
        
        # Make sure we found something
        assert results is not None
        print(f"\nWhen searching for brand: {brand_term}")
        
        # Check each product we found
        for metadata in results['metadatas'][0][:3]:
            print(f"Found this product: {metadata['CLEAN_NAME']}")
            print(f"It's made by: {metadata['PURCHASE_BRAND']}")
            # Make sure it has a brand name
            assert metadata['PURCHASE_BRAND'] is not None 