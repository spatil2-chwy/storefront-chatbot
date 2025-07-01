"""
Tests for the chat modes service functions.
"""
import pytest
from src.services.chat_modes.chatmodes_service import get_openai_response, ask_about_product, get_product_data

@pytest.fixture
def sample_product():
    """Creates a sample product dictionary for testing."""
    return {
        "title": "Test Product",
        "brand": "Test Brand",
        "price": 29.99,
        "autoshipPrice": 25.99,
        "originalPrice": None,
        "rating": 4.5,
        "description": "Test product description",
        "keywords": ["keyword1", "keyword2"],
        "category": "Test Category",
        "unanswered_faqs": "FAQ1? FAQ2?",
        "answered_faqs": "Q1: A1, Q2: A2"
    }

def test_get_openai_response(mock_openai_client, mocker):
    """Test getting response from OpenAI API."""
    mocker.patch('src.services.chat_modes.chatmodes_service.client', mock_openai_client)
    
    # Test JSON mode
    response = get_openai_response("Test query", json_mode=True)
    assert response == "Test response"
    mock_openai_client.chat.completions.create.assert_called_with(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": "Test query"}],
        response_format={"type": "json_object"},
        temperature=0.2
    )
    
    # Test non-JSON mode
    response = get_openai_response("Test query", json_mode=False)
    assert response == "Test response"
    mock_openai_client.chat.completions.create.assert_called_with(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": "Test query"}],
        temperature=0.2
    )

def test_get_openai_response_error_handling(mock_openai_client, mocker):
    """Test error handling in OpenAI response."""
    mocker.patch('src.services.chat_modes.chatmodes_service.client', mock_openai_client)
    
    # Test rate limit error
    mock_openai_client.chat.completions.create.side_effect = Exception("rate_limit exceeded")
    response = get_openai_response("Test query")
    assert "Rate limit exceeded" in response
    
    # Test quota error
    mock_openai_client.chat.completions.create.side_effect = Exception("quota exceeded")
    response = get_openai_response("Test query")
    assert "usage limit" in response
    
    # Test general error
    mock_openai_client.chat.completions.create.side_effect = Exception("unknown error")
    response = get_openai_response("Test query")
    assert "encountered an error" in response

def test_ask_about_product(sample_product, mocker):
    """Test asking questions about a product."""
    # Mock get_openai_response
    mock_response = "This is a test product response"
    mocker.patch('src.services.chat_modes.chatmodes_service.get_openai_response', return_value=mock_response)
    
    response = ask_about_product("Tell me about this product", sample_product)
    assert response == mock_response

def test_get_product_data(sample_product):
    """Test extracting relevant product data."""
    product_data = get_product_data(sample_product)
    
    assert product_data["title"] == sample_product["title"]
    assert product_data["brand"] == sample_product["brand"]
    assert product_data["price"] == sample_product["price"]
    assert product_data["autoshipPrice"] == sample_product["autoshipPrice"]
    assert product_data["originalPrice"] == sample_product["originalPrice"]
    assert product_data["rating"] == sample_product["rating"]
    assert product_data["description"] == sample_product["description"]
    assert product_data["keywords"] == sample_product["keywords"]
    assert product_data["category"] == sample_product["category"]
    assert product_data["unanswered_faqs"] == sample_product["unanswered_faqs"]
    assert product_data["answered_faqs"] == sample_product["answered_faqs"] 