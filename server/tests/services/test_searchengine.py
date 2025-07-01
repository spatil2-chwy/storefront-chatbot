"""
These tests make sure our product search works correctly.
We want to make sure we can find products and sort them in a way that makes sense for users.
"""
import pytest
from src.services.search.searchengine import query_products, query_products_with_followup, rank_products

@pytest.fixture
def mock_chroma_client(mocker):
    """
    Creates a fake database client for testing.
    
    We don't want to use a real database for tests because:
    1. Tests would be slow
    2. We might accidentally change real data
    3. We want to control exactly what data we're testing with
    """
    mock = mocker.MagicMock()
    mock.get_collection.return_value = mocker.MagicMock()
    return mock

@pytest.fixture
def mock_collection(mocker):
    """
    Creates a fake database with some test products in it.
    
    This is like having a small test store with just one product,
    so we know exactly what to expect when we search.
    """
    mock = mocker.MagicMock()
    # Create a fake product with all the details we need to test
    mock.query.return_value = {
        'metadatas': [[{
            "PRODUCT_ID": "123",
            "CLEAN_NAME": "Test Product",
            "PURCHASE_BRAND": "Test Brand",
            "PRICE": "29.99",
            "AUTOSHIP_PRICE": "25.99",
            "RATING_AVG": "4.5",
            "RATING_CNT": "100",
            "DESCRIPTION_LONG": "Test product description",
            "CATEGORY_LEVEL1": "Test Category"
        }]],
        'documents': [["Test product document"]],
        'ids': [["123"]],
        'distances': [[0.1]]  # How well the product matches the search
    }
    return mock

def test_rank_products():
    """
    Makes sure we can sort products in a way that makes sense.
    
    For example, we want to:
    - Show cheaper products first (if price is important)
    - Show better-rated products first (if ratings matter more)
    - Show products with more reviews (so we know the rating is reliable)
    
    This test makes sure our sorting works correctly for all these cases.
    """
    # Create two test products with different prices, ratings, and reviews
    products = [
        {
            'title': 'Product A',
            'price': 10.0,         # Cheaper
            'rating': 4.5,         # Better rating
            'reviewCount': 100     # More reviews
        },
        {
            'title': 'Product B', 
            'price': 20.0,         # More expensive
            'rating': 3.5,         # Lower rating
            'reviewCount': 50      # Fewer reviews
        }
    ]
    
    # Tell the system how to sort the products:
    criteria = [
        ('price', -1.0),      # Lower price is better (that's why it's negative)
        ('rating', 2.0),      # Higher rating is better (positive number)
        ('reviewCount', 0.5)  # More reviews is better (positive number)
    ]
    
    # Sort the products based on our criteria
    ranked = rank_products(products, criteria)
    
    # Make sure we got both products back
    assert len(ranked) == 2
    # Product A should be first because it's cheaper and has better ratings
    assert ranked[0]['title'] == 'Product A'
    # Product B should be second because it's more expensive and has worse ratings
    assert ranked[1]['title'] == 'Product B' 