from src.config.env import get_openai_client
from typing import List, Dict, Any
from src.services.prompts.prompts import get_comparison_prompt, get_ask_about_product_prompt

client = get_openai_client()

def get_openai_response(query: str, json_mode: bool = True) -> str:
    """
    Get response from OpenAI API with optional JSON formatting.
    
    Args:
        query (str): The prompt to send to OpenAI
        json_mode (bool): Whether to request JSON formatted response
    
    Returns:
        str: The generated response or error message
    """
    try:
        if json_mode:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}],
                temperature=0.2
            )

        content = response.choices[0].message.content
        return content if content is not None else "Sorry, I couldn't generate a response at this time."
    
    except Exception as e:
        error_message = str(e)
        if "rate_limit" in error_message.lower() or "429" in error_message:
            return "Rate limit exceeded. Please try again in a moment."
        elif "quota" in error_message.lower():
            return "I've reached my usage limit for today. Please try again tomorrow."
        else:
            return "Sorry, I encountered an error processing your request. Please try again."

def compare_products(user_question: str, products: List[Dict[str, Any]]) -> str:
    """
    Compare products based on user question using OpenAI.
    """
    if not products or len(products) < 2:
        return "Please select at least 2 products to compare them."
    
    # Generate the comparison prompt
    prompt = get_comparison_prompt(user_question, products)
    
    # Get response from OpenAI (not in JSON mode for natural language response)
    response = get_openai_response(prompt, json_mode=False)
    
    return response


def get_product_comparison_data(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract and format product data for comparison.
    
    Args:
        products (List[Dict]): List of product dictionaries
        
    Returns:
        Dict: Formatted product comparison data
    """
    comparison_data = {
        "num_products": len(products),
        "products": []
    }
    
    for product in products:
        product_data = {
            "title": product.get("title"),
            "brand": product.get("brand"),
            "price": product.get("price"),
            "autoshipPrice": product.get("autoshipPrice"),
            "originalPrice": product.get("originalPrice"),
            "rating": product.get("rating"),
            "description": product.get("description"),
            "keywords": product.get("keywords", []),
            "category": product.get("category"),
            "unanswered_faqs": product.get("unanswered_faqs"),
            "answered_faqs": product.get("answered_faqs"),
        }
        comparison_data["products"].append(product_data)
    
    return comparison_data 


def ask_about_product(user_question: str, product: Dict[str, Any]) -> str:
    """
    Generate a response about a product based on user's question.
    
    Args:
        user_question (str): The user's question about the product
        product (Dict[str, Any]): Product data dictionary
    
    Returns:
        str: Generated response about the product
    """
    product_data = get_product_data(product)
    prompt = get_ask_about_product_prompt(user_question, product_data)
    response = get_openai_response(prompt, json_mode=False)
    return response


def get_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant product data for question answering.
    
    Args:
        product (Dict[str, Any]): Raw product dictionary
    
    Returns:
        Dict[str, Any]: Cleaned product data with relevant fields
    """
    product_data = {
        "title": product.get("title"),
        "brand": product.get("brand"),
        "price": product.get("price"),
        "autoshipPrice": product.get("autoshipPrice"),
        "originalPrice": product.get("originalPrice"),
        "rating": product.get("rating"),
        "description": product.get("description"),
        "keywords": product.get("keywords", []),
        "category": product.get("category"),
        "unanswered_faqs": product.get("unanswered_faqs"),
        "answered_faqs": product.get("answered_faqs"),
    }
    return product_data

