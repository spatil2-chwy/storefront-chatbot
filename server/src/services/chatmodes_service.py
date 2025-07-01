from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict, Any
from .prompts import get_comparison_prompt, get_ask_about_product_prompt

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")

client = OpenAI(api_key=api_key)

def get_openai_response(query: str, json_mode: bool = True) -> str:
    """
    Get response from OpenAI API.
    """
    try:
        if json_mode:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": query}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": query}],
                temperature=0.2
            )

        content = response.choices[0].message.content
        return content if content is not None else "Sorry, I couldn't generate a response at this time."
    
    except Exception as e:
        error_message = str(e)
        if "rate_limit" in error_message.lower() or "429" in error_message:
            return "I'm currently experiencing high demand. Please try again in a few minutes."
        elif "quota" in error_message.lower():
            return "I've reached my usage limit for today. Please try again tomorrow."
        else:
            return f"Sorry, I encountered an error: {error_message}"

def compare_products(user_question: str, products: List[Dict[str, Any]]) -> str:
    """
    Compare products based on user question using OpenAI.
    """
    if not products or len(products) < 2:
        return "I need at least 2 products to provide a comparison. Please select more products to compare."
    
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
    Ask about a product based on user question using OpenAI.
    """
    product_data = get_product_data(product)
    prompt = get_ask_about_product_prompt(user_question, product_data)
    response = get_openai_response(prompt, json_mode=False)
    return response


def get_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get product data for to answer a question about a product.
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

