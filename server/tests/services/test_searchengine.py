"""
Tests for the search engine service.
"""
import pytest
from src.services.search.searchengine import query_products, query_products_with_followup, rank_products

@pytest.fixture
def mock_chroma_client(mocker):
    """Creates a mock ChromaDB client."""
    mock = mocker.MagicMock()
    mock.get_collection.return_value = mocker.MagicMock()
    return mock

@pytest.fixture
def mock_collection(mocker):
    """Creates a mock ChromaDB collection with sample results."""
    mock = mocker.MagicMock()
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
            "CATEGORY_LEVEL1": "Test Category",
            "review_synthesis": '{"what_customers_love": ["Great quality"], "what_to_watch_out_for": ["Size runs small"], "should_you_buy_it": "Yes"}'
        }]],
        'documents': [["Test product document"]],
        'ids': [["123"]],
        'distances': [[0.5]]
    }
    return mock

def test_query_products(mocker, mock_chroma_client, mock_collection):
    """Test querying products."""
    mocker.patch('chromadb.PersistentClient', return_value=mock_chroma_client)
    mock_chroma_client.get_collection.return_value = mock_collection
    
    # Test basic query
    results = query_products("test query")
    assert results is not None
    assert len(results['metadatas'][0]) == 1
    assert results['metadatas'][0][0]["CLEAN_NAME"] == "Test Product"
    
    # Test with filters
    results = query_products(
        "test query",
        required_ingredients=["chicken"],
        excluded_ingredients=["beef"],
        special_diet_tags=["grain-free"]
    )
    assert results is not None
    
    # Test error handling
    mock_collection.query.side_effect = Exception("Test error")
    results = query_products("test query")
    assert results is None

def test_query_products_with_followup(mocker, mock_chroma_client, mock_collection):
    """Test follow-up product queries."""
    mocker.patch('chromadb.PersistentClient', return_value=mock_chroma_client)
    mock_chroma_client.get_collection.return_value = mock_collection
    
    # Test basic follow-up query
    results = query_products_with_followup(
        "follow-up query",
        required_ingredients=[],
        excluded_ingredients=[],
        special_diet_tags=[],
        original_query="original query"
    )
    assert results is not None
    assert len(results['metadatas'][0]) == 1
    
    # Test error handling
    mock_collection.query.side_effect = Exception("Test error")
    results = query_products_with_followup(
        "follow-up query",
        required_ingredients=[],
        excluded_ingredients=[],
        special_diet_tags=[],
        original_query="original query"
    )
    assert results is not None  # Should return original results on error

def test_rank_products():
    """Test product ranking."""
    results = {
        'metadatas': [[{
            "PRODUCT_ID": "123",
            "CLEAN_NAME": "Test Product",
            "RATING_AVG": "4.5",
            "RATING_CNT": "100",
            "review_synthesis": '{"what_customers_love": ["Great quality"], "what_to_watch_out_for": ["Size runs small"], "should_you_buy_it": "Yes"}',
            "review_synthesis_flag": True,
            "answered_faqs": "Q1: A1"
        }]],
        'documents': [["Test product document"]],
        'ids': [["123"]],
        'distances': [[0.5]]
    }
    
    # Test ranking with user query
    ranked = rank_products(results, user_query="test query")
    assert ranked is not None
    assert len(ranked['metadatas'][0]) == 1
    
    # Test ranking without user query
    ranked = rank_products(results)
    assert ranked is not None
    assert len(ranked['metadatas'][0]) == 1 