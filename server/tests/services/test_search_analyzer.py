"""
Match search terms with the right product details, like brands, categories, ingredients, and special diets.
"""
import pytest
from src.services.search.search_analyzer import SearchAnalyzer
from src.models.product import SearchMatch

@pytest.fixture
def search_analyzer(mocker):
    """
    Creates a helper that understands product searches.
    
    This helper knows about:
    - Popular pet food brands (like Purina, Hill's, Royal Canin)
    - Product types (like Dog Food, Cat Food, Treats)
    - Common ingredients (like Chicken, Beef, Salmon)
    - Special diets (like Grain-Free, Limited Ingredient)
    - Pet types (Dogs and Cats)
    - Food types (Dry and Wet food)
    """
    analyzer = SearchAnalyzer()
    # Give the helper a list of things to look for in searches
    analyzer.metadata_filters = {
        'brands': {'all': {'Purina', 'Hill\'s', 'Royal Canin'}},
        'categories': {'all': {'Dog Food', 'Cat Food', 'Treats'}},
        'ingredients': {'all': {'Chicken', 'Beef', 'Salmon'}},
        'diet_tags': {'all': {'Grain-Free', 'Limited Ingredient'}},
        'pet_attributes': {
            'types': {'Dog', 'Cat'},
            'food_forms': {'Dry', 'Wet'}
        }
    }
    return analyzer

@pytest.fixture
def sample_product_metadata():
    """
    Creates a fake product to test searches with.
    
    This is like a product card with all the important details:
    - Brand name
    - Product type
    - What kind of food it is
    - What pet it's for
    - What's in it
    - Any special diet features
    """
    return {
        "PURCHASE_BRAND": "Purina",
        "CATEGORY_LEVEL1": "Dog Food",
        "CATEGORY_LEVEL2": "Dry Dog Food",
        "ATTR_PET_TYPE": "Dog",
        "ATTR_FOOD_FORM": "Dry",
        "CLEAN_NAME": "Purina Pro Plan Dog Food",
        "DESCRIPTION_LONG": "High-quality dog food with chicken",
        "ingredienttag:chicken": True,
        "specialdiettag:grain-free": True
    }

def test_criterion_matches_product_metadata(search_analyzer, sample_product_metadata):
    """
    Makes sure we can match what users are looking for with product details.
    
    For example, if someone searches for:
    - "Purina" → we should find Purina products
    - "Dog Food" → we should find dog food
    - "chicken" → we should find food with chicken
    - "grain-free" → we should find grain-free food
    - "dog" → we should find products for dogs
    - "dry food" → we should find dry food
    
    This test checks all these different types of matches.
    """
    # Check if we can find the right brand
    assert search_analyzer._criterion_matches_product_metadata("Purina", sample_product_metadata, "Brands")
    assert not search_analyzer._criterion_matches_product_metadata("Unknown", sample_product_metadata, "Brands")
    
    # Check if we can find the right type of food
    assert search_analyzer._criterion_matches_product_metadata("Dog Food", sample_product_metadata, "Categories")
    assert search_analyzer._criterion_matches_product_metadata("Dry Dog Food", sample_product_metadata, "Categories")
    assert not search_analyzer._criterion_matches_product_metadata("Cat Food", sample_product_metadata, "Categories")
    
    # Check if we can find food with specific ingredients
    assert search_analyzer._criterion_matches_product_metadata("chicken", sample_product_metadata, "Ingredients")
    assert not search_analyzer._criterion_matches_product_metadata("beef", sample_product_metadata, "Ingredients")
    
    # Check if we can find food for special diets
    assert search_analyzer._criterion_matches_product_metadata("grain-free", sample_product_metadata, "Diet & Health")
    assert not search_analyzer._criterion_matches_product_metadata("limited-ingredient", sample_product_metadata, "Diet & Health")
    
    # Check if we can find food for specific pets
    assert search_analyzer._criterion_matches_product_metadata("dog", sample_product_metadata, "Pet Types")
    assert not search_analyzer._criterion_matches_product_metadata("cat", sample_product_metadata, "Pet Types")
    
    # Check if we can find specific types of food
    assert search_analyzer._criterion_matches_product_metadata("dry", sample_product_metadata, "Product Forms")
    assert not search_analyzer._criterion_matches_product_metadata("wet", sample_product_metadata, "Product Forms")

def test_analyze_product_matches(search_analyzer, sample_product_metadata):
    """
    Makes sure we can find all the ways a product matches what someone searched for.
    
    For example, if someone searches for "Purina grain-free dog food",
    we should know the product matches:
    - The brand (Purina)
    - The diet type (grain-free)
    - The pet type (dog)
    - The category (dog food)
    
    This helps us show users why a product matches their search.
    """
    # What the user is looking for
    categorized_criteria = {
        "Brands": ["Purina"],
        "Categories": ["Dog Food"],
        "Ingredients": ["chicken"],
        "Diet & Health": ["grain-free"],
        "Pet Types": ["dog"]
    }
    
    # Find all the ways our test product matches
    matches = search_analyzer.analyze_product_matches(
        sample_product_metadata,
        categorized_criteria,
        "Purina dog food with chicken"
    )
    
    # Make sure we found all 5 matches
    assert len(matches) == 5
    
    # Check that we found matches in all the right categories
    match_fields = {match.field for match in matches}
    expected_fields = {
        "Brands: Purina",
        "Categories: Dog Food",
        "Ingredients: chicken",
        "Diet & Health: grain-free",
        "Pet Types: dog"
    }
    assert match_fields == expected_fields
    
    # Make sure each match has the right details
    for match in matches:
        assert isinstance(match, SearchMatch)  # Right type of result
        assert match.confidence == 0.8         # Good confidence score
        assert len(match.matched_terms) == 1   # One matching term

def test_get_matched_metadata_value(search_analyzer, sample_product_metadata):
    """
    Makes sure we can get the right text to show users for each match.
    
    For example:
    - For brands, show the brand name
    - For categories, show the category name
    - For anything else, show the product name
    
    This helps us explain to users why we showed them each product.
    """
    # Check brand names
    assert search_analyzer._get_matched_metadata_value("Purina", sample_product_metadata, "Brands") == "Purina"
    
    # Check category names
    assert search_analyzer._get_matched_metadata_value("Dog Food", sample_product_metadata, "Categories") == "Dog Food"
    
    # Check that we fall back to product name for other things
    assert search_analyzer._get_matched_metadata_value("chicken", sample_product_metadata, "Other").startswith("Purina Pro Plan Dog Food") 