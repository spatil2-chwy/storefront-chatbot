"""
Tests for the prompts service.
"""
import pytest
from src.services.prompts.prompts import format_single_product_details, get_comparison_prompt, get_ask_about_product_prompt

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
        "reviewCount": 100,
        "description": "Test product description",
        "keywords": ["feature1", "feature2"],
        "category": "Test Category"
    }

def test_format_single_product_details(sample_product):
    """Test formatting single product details."""
    details = format_single_product_details(sample_product)
    
    # Check all required fields are present
    assert "Title: Test Product" in details
    assert "Brand: Test Brand" in details
    assert "Price: $29.99" in details
    assert "Autoship Price: $25.99" in details
    assert "Rating: 4.5 stars (100 reviews)" in details
    assert "Description: Test product description" in details
    assert "Key Features: feature1, feature2" in details
    assert "Category: Test Category" in details

def test_format_single_product_details_missing_fields():
    """Test formatting product details with missing fields."""
    product = {
        "title": "Test Product",
        "price": None,
        "rating": None,
        "reviewCount": None
    }
    
    details = format_single_product_details(product)
    
    assert "Title: Test Product" in details
    assert "Brand: Unknown" in details
    assert "Price: $0.00" in details
    assert "Rating: 0.0 stars (0 reviews)" in details

def test_get_comparison_prompt():
    """Test generating comparison prompt."""
    products = [
        {
            "title": "Product 1",
            "brand": "Brand 1",
            "price": 29.99,
            "description": "Description 1"
        },
        {
            "title": "Product 2",
            "brand": "Brand 2",
            "price": 39.99,
            "description": "Description 2"
        }
    ]
    
    prompt = get_comparison_prompt(products)
    
    # Check that the prompt contains product information
    assert "Product 1" in prompt
    assert "Product 2" in prompt
    assert "Brand 1" in prompt
    assert "Brand 2" in prompt
    assert "Description 1" in prompt
    assert "Description 2" in prompt

def test_get_ask_about_product_prompt(sample_product):
    """Test generating ask about product prompt."""
    question = "What are the key features?"
    prompt = get_ask_about_product_prompt(sample_product, question)
    
    # Check that the prompt contains product details and question
    assert "Test Product" in prompt
    assert "Test Brand" in prompt
    assert "Test product description" in prompt
    assert question in prompt 