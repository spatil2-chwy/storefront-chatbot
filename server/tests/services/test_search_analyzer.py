"""
Tests for the SearchAnalyzer class.
"""
import pytest
from src.services.search.search_analyzer import SearchAnalyzer
from src.models.product import SearchMatch

@pytest.fixture
def search_analyzer(mocker):
    """Creates a SearchAnalyzer instance with mocked filters."""
    analyzer = SearchAnalyzer()
    # Mock the metadata filters
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
    """Creates sample product metadata for testing."""
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
    """Test matching criteria against product metadata."""
    # Test brand matching
    assert search_analyzer._criterion_matches_product_metadata("Purina", sample_product_metadata, "Brands")
    assert not search_analyzer._criterion_matches_product_metadata("Unknown", sample_product_metadata, "Brands")
    
    # Test category matching
    assert search_analyzer._criterion_matches_product_metadata("Dog Food", sample_product_metadata, "Categories")
    assert search_analyzer._criterion_matches_product_metadata("Dry Dog Food", sample_product_metadata, "Categories")
    assert not search_analyzer._criterion_matches_product_metadata("Cat Food", sample_product_metadata, "Categories")
    
    # Test ingredient matching
    assert search_analyzer._criterion_matches_product_metadata("chicken", sample_product_metadata, "Ingredients")
    assert not search_analyzer._criterion_matches_product_metadata("beef", sample_product_metadata, "Ingredients")
    
    # Test diet tag matching
    assert search_analyzer._criterion_matches_product_metadata("grain-free", sample_product_metadata, "Diet & Health")
    assert not search_analyzer._criterion_matches_product_metadata("limited-ingredient", sample_product_metadata, "Diet & Health")
    
    # Test pet type matching
    assert search_analyzer._criterion_matches_product_metadata("dog", sample_product_metadata, "Pet Types")
    assert not search_analyzer._criterion_matches_product_metadata("cat", sample_product_metadata, "Pet Types")
    
    # Test product form matching
    assert search_analyzer._criterion_matches_product_metadata("dry", sample_product_metadata, "Product Forms")
    assert not search_analyzer._criterion_matches_product_metadata("wet", sample_product_metadata, "Product Forms")

def test_analyze_product_matches(search_analyzer, sample_product_metadata):
    """Test analyzing product matches."""
    categorized_criteria = {
        "Brands": ["Purina"],
        "Categories": ["Dog Food"],
        "Ingredients": ["chicken"],
        "Diet & Health": ["grain-free"],
        "Pet Types": ["dog"]
    }
    
    matches = search_analyzer.analyze_product_matches(
        sample_product_metadata,
        categorized_criteria,
        "Purina dog food with chicken"
    )
    
    assert len(matches) == 5
    
    # Verify each match
    match_fields = {match.field for match in matches}
    expected_fields = {
        "Brands: Purina",
        "Categories: Dog Food",
        "Ingredients: chicken",
        "Diet & Health: grain-free",
        "Pet Types: dog"
    }
    assert match_fields == expected_fields
    
    # Verify match details
    for match in matches:
        assert isinstance(match, SearchMatch)
        assert match.confidence == 0.8
        assert len(match.matched_terms) == 1

def test_get_matched_metadata_value(search_analyzer, sample_product_metadata):
    """Test getting matched metadata values."""
    # Test brand value
    assert search_analyzer._get_matched_metadata_value("Purina", sample_product_metadata, "Brands") == "Purina"
    
    # Test category value
    assert search_analyzer._get_matched_metadata_value("Dog Food", sample_product_metadata, "Categories") == "Dog Food"
    
    # Test default value (product name)
    assert search_analyzer._get_matched_metadata_value("chicken", sample_product_metadata, "Other").startswith("Purina Pro Plan Dog Food") 