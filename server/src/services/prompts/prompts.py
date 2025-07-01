"""
Prompts for various chat modes.
"""
import json

COMPARISON_PROMPT_TEMPLATE = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in product comparisons.

Number of products to compare: {num_products}

PRODUCT INFORMATION:
{product_details}

USER QUESTION: {user_question}

Answer in short, concise sentences.
"""

def format_product_details(products):
    """
    Format product details for the comparison prompt.
    """
    formatted_details = []
    
    for i, product in enumerate(products, 1):
        details = f"PRODUCT {i}: {product.get('title', 'Unknown Product')}\n"
        details += f"  Brand: {product.get('brand', 'Unknown')}\n"
        
        # Handle price safely
        price = product.get('price', 0)
        price = price if price is not None else 0
        details += f"  Price: ${price:.2f}\n"
        
        # Handle autoship price safely
        if product.get('autoshipPrice'):
            autoship_price = product.get('autoshipPrice', 0)
            autoship_price = autoship_price if autoship_price is not None else 0
            details += f"  Autoship Price: ${autoship_price:.2f}\n"
        
        # Handle rating safely
        rating = product.get('rating', 0)
        rating = rating if rating is not None else 0
        review_count = product.get('reviewCount', 0)
        review_count = review_count if review_count is not None else 0
        details += f"  Rating: {rating:.1f} stars ({review_count} reviews)\n"
        
        if product.get('description'):
            details += f"  Description: {product.get('description', '')}\n"
            
        if product.get('keywords'):
            details += f"  Key Features: {', '.join(product.get('keywords', []))}\n"
            
        if product.get('category'):
            details += f"  Category: {product.get('category', '')}\n"
            
        formatted_details.append(details)
    
    return "\n".join(formatted_details)

def get_comparison_prompt(products, question):
    """
    Generate a prompt for comparing multiple products.
    """
    prompt = "Please compare the following products:\n\n"
    
    for i, product in enumerate(products, 1):
        prompt += f"Product {i}:\n"
        prompt += format_single_product_details(product)
        prompt += "\n"
    
    prompt += f"\nQuestion: {question}\n"
    prompt += "\nPlease provide a detailed comparison focusing on the key differences and similarities between these products."
    
    return prompt

ASK_ABOUT_PRODUCT_PROMPT_TEMPLATE = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in answering questions about specific products.

PRODUCT INFORMATION:
{product_details}

USER QUESTION: {user_question}

Answer in short, concise sentences.
"""

def format_single_product_details(product):
    """
    Format product details for the ask about product prompt.
    """
    details = f"Title: {product.get('title', 'Unknown Product')}\n"
    details += f"Brand: {product.get('brand', 'Unknown')}\n"
    details += f"Price: ${product.get('price', 0.00):.2f}\n"
    details += f"Autoship Price: ${product.get('autoshipPrice', 0.00):.2f}\n"
    details += f"Rating: {product.get('rating', 0.0)} stars ({product.get('reviewCount', 0)} reviews)\n"
    details += f"Description: {product.get('description', 'No description available')}\n"
    
    # Format keywords/features if available
    keywords = product.get('keywords', [])
    if keywords:
        details += f"Key Features: {', '.join(keywords)}\n"
    
    details += f"Category: {product.get('category', 'Unknown')}\n"
    
    return details

def get_ask_about_product_prompt(product_data, question):
    """
    Generate a prompt for asking about a specific product.
    """
    prompt = "Please analyze the following product:\n\n"
    prompt += format_single_product_details(product_data)
    prompt += f"\nQuestion: {question}\n"
    prompt += "\nPlease provide a detailed answer based on the product information above."
    
    return prompt
    
