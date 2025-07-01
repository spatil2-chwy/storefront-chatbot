"""
Make sure we create the right messages to ask the AI about products.
"""
import pytest
from src.services.prompts.prompts import format_single_product_details, get_comparison_prompt, get_ask_about_product_prompt

@pytest.fixture
def sample_product():
    """
    Creates a fake product.
    """
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
    """
    Makes sure we show all the important details about a product.
    
    When someone asks about a product, we need to tell them:
    - What it's called
    - Who makes it
    - How much it costs
    - What the subscription price is
    - How good the reviews are
    - What it does
    - What special features it has
    - What category it's in
    
    This test makes sure we don't forget any of these details.
    """
    # Get all the details about our test product
    details = format_single_product_details(sample_product)
    
    # Check that all the important information is included
    assert "Title: Test Product" in details          # Product name
    assert "Brand: Test Brand" in details           # Who makes it
    assert "Price: $29.99" in details               # Regular price
    assert "Autoship Price: $25.99" in details      # Subscription price
    assert "Rating: 4.5 stars (100 reviews)" in details  # How good it is
    assert "Description: Test product description" in details  # What it does
    assert "Key Features: feature1, feature2" in details  # Special features
    assert "Category: Test Category" in details     # What type of product it is

def test_get_comparison_prompt():
    """
    Makes sure we can help compare two products.
    
    When someone wants to compare products, we need to:
    1. Show details for both products side by side
    2. Include their question about the comparison
    3. Make it easy for the AI to spot the differences
    
    This test makes sure we format the comparison in a helpful way.
    """
    # Create two different products to compare
    products = [
        {
            "title": "Product 1",
            "brand": "Brand 1",
            "price": 29.99,
            "description": "Description 1",
            "rating": 4.5,
            "reviewCount": 100,
            "keywords": ["feature1"],
            "category": "Category 1"
        },
        {
            "title": "Product 2",
            "brand": "Brand 2",
            "price": 39.99,
            "description": "Description 2",
            "rating": 4.0,
            "reviewCount": 50,
            "keywords": ["feature2"],
            "category": "Category 2"
        }
    ]
    
    # This is what the user wants to know about the products
    question = "What are the main differences between these products?"
    
    # Create the message that will help compare the products
    prompt = get_comparison_prompt(products, question)
    
    # Make sure the message includes all the important details
    assert "Product 1" in prompt         # First product name
    assert "Product 2" in prompt         # Second product name
    assert "Brand 1" in prompt           # First brand
    assert "Brand 2" in prompt           # Second brand
    assert "Description 1" in prompt     # What first product does
    assert "Description 2" in prompt     # What second product does
    assert question in prompt            # The user's question

def test_get_ask_about_product_prompt(sample_product):
    """
    Makes sure we can ask questions about a single product.
    
    When someone has a specific question about a product, we need to:
    1. Show all the important product details
    2. Include their question
    3. Format it in a way that helps the AI give a good answer
    
    This test makes sure we create a helpful message for the AI.
    """
    # This is what the user wants to know
    question = "What are the key features?"
    
    # Create the message using our test product
    prompt = get_ask_about_product_prompt(sample_product, question)
    
    # Make sure the message has the product details and the question
    assert "Test Product" in prompt      # Product name
    assert "Test Brand" in prompt        # Brand name
    assert "Test product description" in prompt  # What it does
    assert question in prompt            # The user's question 