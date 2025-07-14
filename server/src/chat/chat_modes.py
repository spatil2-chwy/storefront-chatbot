import os
from typing import List, Dict, Any, Optional
from .prompts import comparison_prompt, ask_about_product_prompt, chat_modes_system_prompt
from src.config.openai_loader import get_openai_client

# Get the centralized OpenAI client
client = get_openai_client()

def get_openai_response(query: str, json_mode: bool = True) -> str:
    """
    Get response from OpenAI API.
    """
    try:
        if json_mode:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": chat_modes_system_prompt}, 
                    {"role": "user", "content": query}
                    ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[
                    {"role": "system", "content": chat_modes_system_prompt}, 
                    {"role": "user", "content": query}
                    ],
                # temperature=0.2
            )

        print(response)
        content = response.choices[0].message.content

        # Check if content is None or empty
        if not content:
            return "Sorry, I couldn't generate a response at this time."

        # we do not want competitor links or product links in the response
        blacklisted_domains = [
            "amazon.com",
            "walmart.com",
            "petco.com",
            "petsmart.com",
            "target.com",
            "bestbuy.com",
            "tractorsupply.com",
            "mypetfoodcenter.com",
            "petsupermarket.com",
            "fleetfarm.com"
        ]
        # replace any links in markdown format with an empty string with regex
        # split by space and remove any words that contain blacklisted domains
        content_words = content.split()
        content = ' '.join(
            word for word in content_words if not any(domain in word for domain in blacklisted_domains)
        )


        return content if content is not None else "Sorry, I couldn't generate a response at this time."
    
    except Exception as e:
        error_message = str(e)
        if "rate_limit" in error_message.lower() or "429" in error_message:
            return "I'm currently experiencing high demand. Please try again in a few minutes."
        elif "quota" in error_message.lower():
            return "I've reached my usage limit for today. Please try again tomorrow."
        else:
            return f"Sorry, I encountered an error: {error_message}"

def extract_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and format product data consistently across all functions.
    
    Args:
        product (Dict): Product dictionary
        
    Returns:
        Dict: Formatted product data with safe defaults
    """
    return {
        "title": product.get("title"),
        "brand": product.get("brand"),
        "price": product.get("price"),
        "autoshipPrice": product.get("autoshipPrice"),
        "originalPrice": product.get("originalPrice"),
        "rating": product.get("rating"),
        "description": product.get("description"),
        "keywords": product.get("keywords", []),
        "category_level_1": product.get("category_level_1"),
        "category_level_2": product.get("category_level_2"),
        "unanswered_faqs": product.get("unanswered_faqs"),
        "answered_faqs": product.get("answered_faqs"),
    }

def format_product_details(product_data: Dict[str, Any], product_index: Optional[int] = None) -> str:
    """
    Format product details for prompt inclusion.
    
    Args:
        product_data (Dict): Product data from extract_product_data
        product_index (Optional[int]): Product number for comparison prompts
        
    Returns:
        str: Formatted product details string
    """
    prefix = f"PRODUCT {product_index}: " if product_index else ""
    details = f"{prefix}{product_data.get('title', 'Unknown Product')}\n"
    
    if product_index:
        details = details.replace("PRODUCT 1: ", "  ")  # Indent for comparison format
    else:
        details = f"Title: {product_data.get('title', 'Unknown Product')}\n"
    
    details += f"  Brand: {product_data.get('brand', 'Unknown')}\n"
    
    # Handle price safely
    price = product_data.get('price', 0)
    price = price if price is not None else 0
    details += f"  Price: ${price:.2f}\n"
    
    # Handle autoship price safely
    if product_data.get('autoshipPrice'):
        autoship_price = product_data.get('autoshipPrice', 0)
        autoship_price = autoship_price if autoship_price is not None else 0
        details += f"  Autoship Price: ${autoship_price:.2f}\n"
    
    # Handle rating safely
    rating = product_data.get('rating', 0)
    rating = rating if rating is not None else 0
    review_count = product_data.get('reviewCount', 0)
    review_count = review_count if review_count is not None else 0
    details += f"  Rating: {rating:.1f} stars ({review_count} reviews)\n"
    
    if product_data.get('description'):
        details += f"  Description: {product_data.get('description', '')}\n"
        
    if product_data.get('keywords'):
        details += f"  Key Features: {', '.join(product_data.get('keywords', []))}\n"
        
    if product_data.get('category_level_1'):
        details += f"  Category: {product_data.get('category_level_1', '')}\n"
    if product_data.get('category_level_2'):
        details += f"  Subcategory: {product_data.get('category_level_2', '')}\n"
    
    return details

def format_conversation_history(history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Format conversation history for prompt inclusion.
    
    Args:
        history (Optional[List]): Conversation history
        
    Returns:
        str: Formatted conversation history string
    """
    if not history or len(history) == 0:
        return ""
    
    conversation_history = "CONVERSATION HISTORY:\n"
    for msg in history:
        role = "User" if msg.get('role') == 'user' else "Assistant"
        conversation_history += f"{role}: {msg.get('content', '')}\n"
    conversation_history += "\n"
    
    return conversation_history

def compare_products(user_question: str, products: List[Dict[str, Any]], history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Compare products based on user question using OpenAI.
    """
    if not products or len(products) < 2:
        return "Please select at least 2 products to compare them."
    
    # Format product details for comparison
    product_details = []
    for i, product in enumerate(products, 1):
        product_data = extract_product_data(product)
        product_details.append(format_product_details(product_data, i))
    
    # Format conversation history
    conversation_history = format_conversation_history(history)
    
    # Generate the comparison prompt
    prompt = comparison_prompt.format(
        conversation_history=conversation_history,
        num_products=len(products),
        product_details="\n".join(product_details),
        user_question=user_question
    )
    
    # Get response from OpenAI (not in JSON mode for natural language response)
    response = get_openai_response(prompt, json_mode=False)
    
    return response

def ask_about_product(user_question: str, product: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Ask about a product based on user question using OpenAI.
    """
    product_data = extract_product_data(product)
    product_details = format_product_details(product_data)
    conversation_history = format_conversation_history(history)
    
    prompt = ask_about_product_prompt.format(
        conversation_history=conversation_history,
        user_question=user_question,
        product_details=product_details
    )
    
    response = get_openai_response(prompt, json_mode=False)
    return response
