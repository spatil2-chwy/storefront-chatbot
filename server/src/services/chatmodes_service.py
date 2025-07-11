import os
from typing import List, Dict, Any
from .prompts import get_comparison_prompt, get_ask_about_product_prompt
from .openai_client import get_openai_client

# Get the centralized OpenAI client
client = get_openai_client()

product_system_prompt = {
    "role": "system",
    "content": """
You are helping users compare products and answer individual questions about them for Chewy.

You may search the web for publicly available product information **only to extract helpful facts** (like dimensions, ingredients, compatibility, fit, etc.). Your goal is to summarize this information clearly and concisely.

### Critical Rules:
- **DO NOT** provide any product links, including to Chewy or competitor websites.
- **DO NOT** name or reference competitors (like Amazon, PetSmart, Walmart, etc.).
- **DO NOT** copy or paraphrase promotional language from third-party sites.
- **Only provide factual, neutral summaries** of product information (e.g., size, weight limit, materials, use cases).
- If a specific answer is not available, **say so politely** and invite the user to ask another product-related question.
- If the user asks for anything other than product comparisons or product-specific questions, **decline** and redirect them.

### Example behavior:
- ✅ “This bed has orthopedic memory foam and is best for senior dogs up to 70 lbs.”
- ❌ “Here’s a link to the product on [competitor.com].”
- ❌ “Check Amazon for more info.”
- ❌ “You can find it on Petco here.”

Stay focused, helpful, and always product-specific. Never promote or link out.
"""
}


def get_openai_response(query: str, json_mode: bool = True) -> str:
    """
    Get response from OpenAI API.
    """
    try:
        if json_mode:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[product_system_prompt, {"role": "user", "content": query}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[product_system_prompt, {"role": "user", "content": query}],
                # temperature=0.2
            )

        print(response)
        content = response.choices[0].message.content

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

def compare_products(user_question: str, products: List[Dict[str, Any]], history: List[Dict[str, Any]] = None) -> str:
    """
    Compare products based on user question using OpenAI.
    """
    if not products or len(products) < 2:
        return "Please select at least 2 products to compare them."
    
    # Generate the comparison prompt with conversation history
    prompt = get_comparison_prompt(user_question, products, history or [])
    
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
            "category_level_1": product.get("category_level_1"),
            "category_level_2": product.get("category_level_2"),
            "unanswered_faqs": product.get("unanswered_faqs"),
            "answered_faqs": product.get("answered_faqs"),
        }
        comparison_data["products"].append(product_data)
    
    return comparison_data 
    

def ask_about_product(user_question: str, product: Dict[str, Any], history: List[Dict[str, Any]] = None) -> str:
    """
    Ask about a product based on user question using OpenAI.
    """
    product_data = get_product_data(product)
    prompt = get_ask_about_product_prompt(user_question, product_data, history or [])
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
        "category_level_1": product.get("category_level_1"),
        "category_level_2": product.get("category_level_2"),
        "unanswered_faqs": product.get("unanswered_faqs"),
        "answered_faqs": product.get("answered_faqs"),
    }
    return product_data
