from openai import OpenAI
from dotenv import load_dotenv
import json
import time
from os import getenv
import time
from typing import List, Dict, Any, Optional, Union, cast
load_dotenv()
from src.services.searchengine import query_products, rank_products, get_product_buffer, clear_product_buffer
api_key = getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
client = OpenAI(api_key=api_key)
# refactor needed, tools, system prompt, model, etc should be in a separate file
tools = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Use this for any product-related query based on the pet parent's natural-language input. This includes initial needs (e.g. 'my cat has bad breath'), specific intents ('puppy training treats'), or conversationally described situations (e.g. 'my dog developed a chicken allergy. needs protein'). This function constructs a semantic query using the user's language and applies optional filters like ingredients or diet tags.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """Extract structured, product-focused information from the user's natural-language input to power Chewy's personalized product search. Map the situation to **specific, search-friendly product types** that Chewy likely sells. Do NOT repeat the emotional or behavioral language unless it's part of a recognized product label or tag. Favor concrete product terms: formats (treats, kibble, diffusers), features (low-calorie, long-lasting), or function (digestive aid, calming aid).

For example:
User: "My cat is allergic to chicken but needs protein, what should I get?"                 
query: "cat food"
required_ingredients: []
excluded_ingredients: ["chicken"]
special_diet_tags: ["Chicken-Free", "High-Protein"]


User: "Bird food for my parakeet"
query: "bird food parakeet"
required_ingredients: []
excluded_ingredients: []
special_diet_tags: []
"""
                },
                "required_ingredients": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Ingredients that must be present in the product, e.g. 'Chicken', 'Peas'"
                    },
                    "description": "List of required ingredients that must be present in the product. Leave empty if no specific ingredients are required."
                },
                "excluded_ingredients": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Ingredients that must not be present in the product, e.g. 'Corn', 'Soy'"
                    },
                    "description": "List of ingredients that must not be present in the product. Leave empty if no specific ingredients should be excluded."
                },
                "special_diet_tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            'Chicken-Free',
                            'Flax-Free',
                            'Gluten Free',
                            'Grain-Free',
                            'High Calcium',
                            'High Calorie',
                            'High Fat',
                            'High Fiber',
                            'High-Protein',
                            'Human-Grade',
                            'Hydrolyzed Protein',
                            'Indoor',
                            'Limited Ingredient Diet',
                            'Low Calorie',
                            'Low Fat',
                            'Low Glycemic',
                            'Low NSC',
                            'Low Phosphorus',
                            'Low Sodium',
                            'Low Starch',
                            'Low Sugar',
                            'Low-Protein',
                            'Medicated',
                            'Molasses-Free',
                            'Natural',
                            'No Corn No Wheat No Soy',
                            'Non-GMO',
                            'Odor-Free',
                            'Organic',
                            'Pea-Free',
                            'Plant Based',
                            'Premium',
                            'Raw',
                            'Rawhide-Free',
                            'Sensitive Digestion',
                            'Soy Free',
                            'Starch Free',
                            'Sugar Free',
                            'Vegan',
                            'Vegetarian',
                            'Veterinary Diet',
                            'Weight Control',
                            'With Grain',
                            'Yeast Free'
                        ],
                        "description": "Special diet tags that the food product must adhere to, e.g. 'Grain-Free', 'Organic'. Leave empty if no specific diet tags are required, or if the product is not food."
                    },
                    "description": "List of special diet tags that the product must adhere to. Leave empty if no specific diet tags are required."
                },
            },
            "required": ["query", "required_ingredients", "excluded_ingredients", "special_diet_tags"],
            "additionalProperties": False,
            # "strict": True # although openai recommended, this seems to make things worse
        }
    },

        {
        "type": "function",
        "name": "search_products_with_followup",
        "description": "Use this when the user answers a follow-up question that helps refine their preferences. This function re-ranks a previously shown list of products using semantic similarity between user input and product reviews + titles. This is for personalization and streamlining the search — not for starting a new search.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """Extract structured, product-focused information from the user history to power Chewy's personalized product search. Map the situation to **specific, search-friendly product types** that Chewy likely sells. Do NOT repeat the emotional or behavioral language unless it's part of a recognized product label or tag. Favor concrete product terms: formats (treats, kibble, diffusers), features (low-calorie, long-lasting), or function (digestive aid, calming aid).
                    
User: "Easiest way to deal with dog yard dog poop? + Re-usable scoopers should be fine."
query: "Re-usable dog poop scoopers"
required_ingredients: []
excluded_ingredients: []
special_diet_tags: []
"""
                },
                "required_ingredients": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Ingredients that must be present in the product, e.g. 'Chicken', 'Peas'"
                    },
                    "description": "List of required ingredients that must be present in the product. Leave empty if no specific ingredients are required."
                },
                "excluded_ingredients": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Ingredients that must not be present in the product, e.g. 'Corn', 'Soy'"
                    },
                    "description": "List of ingredients that must not be present in the product. Leave empty if no specific ingredients should be excluded."
                },
                "special_diet_tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            'Chicken-Free',
                            'Flax-Free',
                            'Gluten Free',
                            'Grain-Free',
                            'High Calcium',
                            'High Calorie',
                            'High Fat',
                            'High Fiber',
                            'High-Protein',
                            'Human-Grade',
                            'Hydrolyzed Protein',
                            'Indoor',
                            'Limited Ingredient Diet',
                            'Low Calorie',
                            'Low Fat',
                            'Low Glycemic',
                            'Low NSC',
                            'Low Phosphorus',
                            'Low Sodium',
                            'Low Starch',
                            'Low Sugar',
                            'Low-Protein',
                            'Medicated',
                            'Molasses-Free',
                            'Natural',
                            'No Corn No Wheat No Soy',
                            'Non-GMO',
                            'Odor-Free',
                            'Organic',
                            'Pea-Free',
                            'Plant Based',
                            'Premium',
                            'Raw',
                            'Rawhide-Free',
                            'Sensitive Digestion',
                            'Soy Free',
                            'Starch Free',
                            'Sugar Free',
                            'Vegan',
                            'Vegetarian',
                            'Veterinary Diet',
                            'Weight Control',
                            'With Grain',
                            'Yeast Free'
                        ],
                        "description": "Special diet tags that the food product must adhere to, e.g. 'Grain-Free', 'Organic'. Leave empty if no specific diet tags are required, or if the product is not food."
                    },
                    "description": "List of special diet tags that the product must adhere to. Leave empty if no specific diet tags are required."
                },
            },
            "required": ["query", "required_ingredients", "excluded_ingredients", "special_diet_tags"],
            "additionalProperties": False,
            # "strict": True # although openai recommended, this seems to make things worse
        }
    }
]


system_message = {
    "role": "system",
    "content": """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice.

Your mission is to guide pet parents toward the best products for their pet's specific needs. You can either ask a follow-up question if the query is too vague or respond through *action* by using one of the tools available to you.

---
🔧 TOOL SELECTION RULES:

Use the `search_products` function:
- When a pet parent starts with a need, product question, or describes a situation like: "My cat has a chicken allergy" or "I need a toy for a heavy chewer".
- Also use it if the pet parent gives a new, unrelated response to a follow-up question (e.g. "products to help my dog with anxiety").

Use the `search_products_with_followup` function:
- When the pet parent answers a follow-up question based on previously recommended products.
- The follow-up should be relevant to the original search — like "Yes, she needs low-fat too."

---
🌟 CHEWY BRAND TONE:

- Be clear, friendly, and deeply empathetic — like a savvy pet parent who knows what it's like.
- Use precise, mobile-friendly language.

---
❌ DO NOT:
- Answer questions unrelated to pet products. Gently steer back to product needs.
- Prioritize calling a tool over returning text explanations unless the query is super vague or not product related.
"""
}
MODEL = "gpt-4.1-mini"

def search_products(query: str, required_ingredients: list, excluded_ingredients: list, special_diet_tags: list):
    """Searches for pet products based on user query and filters.
    Parameters:
        query (str): User intent in natural language, e.g. 'puppy food' or 'grain-free dog treats'
        required_ingredients (list): List of ingredients that must be present in the product
        excluded_ingredients (list): List of ingredients that must not be present in the product
        special_diet_tags (list): List of special diet tags that the product must adhere to
    Returns:
        tuple: A tuple containing a list of products and follow-up questions
    """
    start = time.time()
    
    # Use ProductService to convert raw results to properly formatted Product objects
    from src.services.product_service import ProductService
    product_service = ProductService()
    
    # Use query_products for all searches (it handles empty filters fine)
    # This will automatically store the top 300 products in the buffer
    results = query_products(query, required_ingredients, excluded_ingredients, special_diet_tags)
    print(f"Query executed in {time.time() - start:.4f} seconds")
    
    ranking_start = time.time()
    ranked_products, followup_questions = rank_products(results, user_query=query, previous_questions=None)
    print(f"Ranking completed in {time.time() - ranking_start:.4f} seconds")
    
    if not ranked_products:
        return [], ""

    # Convert raw ranked results to Product objects using ProductService
    conversion_start = time.time()
    products = []
    for i, ranked_result in enumerate(ranked_products[:30]):  # Limit to 30 products
        try:
            product = product_service._ranked_result_to_product(ranked_result, query)
            products.append(product)
        except Exception as e:
            print(f"⚠️ Error converting ranked result to product: {e}")
            continue
    
    conversion_time = time.time() - conversion_start
    print(f"Product conversion took: {conversion_time:.4f} seconds ({len(products)} products)")

    print(f"Total search_products time: {time.time() - start:.4f} seconds")
    return products, followup_questions

def search_products_with_followup(query: str, required_ingredients: list, excluded_ingredients: list, special_diet_tags: list):
    """Searches for pet products based on user's follow-up response to previous questions.
    Parameters:
        query (str): User's follow-up response/refinement
        required_ingredients (list): List of ingredients that must be present in the product
        excluded_ingredients (list): List of ingredients that must not be present in the product
        special_diet_tags (list): List of special diet tags that the product must adhere to
    Returns:
        tuple: A tuple containing a list of products and follow-up questions
    """
    from src.services.searchengine import query_products_with_followup, get_product_buffer, clear_product_buffer
    start = time.time()
    
    # Use ProductService to convert raw results to properly formatted Product objects
    from .product_service import ProductService
    product_service = ProductService()
    
    # Get previous products from the product buffer
    previous_products = get_product_buffer()
    
    if not previous_products:
        print("No previous products in buffer, falling back to regular search")
        return search_products(query, required_ingredients, excluded_ingredients, special_diet_tags)
    
    # Use query_products_with_followup for refined searches
    # This will re-rank the products from the buffer using the review collection
    results = query_products_with_followup(query, required_ingredients, excluded_ingredients, special_diet_tags, previous_products)
    print(f"Follow-up query executed in {time.time() - start:.4f} seconds")
    
    ranking_start = time.time()
    # For follow-up mode, we need to track previous questions to avoid repetition
    # This should be extracted from conversation history in a production system
    previous_questions = []  # TODO: Extract from conversation history
    ranked_products, followup_questions = rank_products(results, user_query=query, previous_questions=previous_questions)
    print(f"Ranking completed in {time.time() - ranking_start:.4f} seconds")
    
    if not ranked_products:
        return [], ""

    # Convert raw ranked results to Product objects using ProductService
    conversion_start = time.time()
    products = []
    for i, ranked_result in enumerate(ranked_products[:30]):  # Limit to 30 products for display
        try:
            product = product_service._ranked_result_to_product(ranked_result, query)
            products.append(product)
        except Exception as e:
            print(f"⚠️ Error converting ranked result to product: {e}")
            continue
    
    conversion_time = time.time() - conversion_start
    print(f"Product conversion took: {conversion_time:.4f} seconds ({len(products)} products)")

    print(f"Total search_products_with_followup time: {time.time() - start:.4f} seconds")
    return products, followup_questions


function_mapping = {
    "search_products": search_products,
    "search_products_with_followup": search_products_with_followup
}


def call_function(name, args):
    """Calls a tool function by its name with the provided arguments.
    Parameters:
        name (str): The name of the function to call
        args (dict): A dictionary of input arguments for the function
    Returns:
        The result of the function call
    Raises:
        ValueError: If the function name is not recognized
    """
    if name in function_mapping:
        return function_mapping[name](**args)
    raise ValueError(f"Unknown function: {name}")


def chat(user_input: str, history: list, user_context: str = "", skip_products: bool = False):
    start_time = time.time()
    
    # Create system message with user context if provided
    system_msg = system_message.copy()
    if user_context:
        system_msg["content"] += f"\n\nCUSTOMER CONTEXT:\n{user_context}\n\nUse this information to provide personalized recommendations. Ask if they're shopping for their specific pets to refine searches."
    
    full_history = (
        [system_msg] + history + [{"role": "user", "content": user_input}]
    )
    # print(full_history)
    # Step 1: Get model response
    response = client.responses.create(
        model=MODEL,
        input=full_history,
        tools=cast(Any, tools),
    )   
    print(f"First response received in {time.time() - start_time:.4f} seconds")
    # print(response)
    products = []
    followup_questions = ""
    assistant_reply = ""

    print(response.output)
    if len(response.output) == 1 and response.output[0].type == "message":
        # Handle message response
        assistant_reply = response.output[0].content[0].text
        full_history.append({"role": "assistant", "content": assistant_reply})
    else:
        function_start = time.time()
        print(f"Function call start after {function_start - start_time:.4f} seconds from start")
        
        # Handle function call response
        for output_item in response.output:
            if output_item.type == "function_call":
                tool_call = output_item
                # Convert tool_call to dict for history
                tool_call_dict = {
                    "type": "function_call",
                    "id": tool_call.id,
                    "call_id": tool_call.call_id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments
                }
                full_history.append(tool_call_dict)
                
                # Determine if this is a new search or follow-up
                is_followup = tool_call.name == "search_products_with_followup"
                
                if tool_call.name not in ["search_products", "search_products_with_followup"]:
                    raise ValueError(f"Unexpected tool call: {tool_call.name}")
                
                args = json.loads(tool_call.arguments)
                print(f"Calling {tool_call.name}(**{args}), its been {time.time() - start_time:.4f} seconds since the chat started")
                
                # Clear product buffer if this is a new search (not follow-up)
                if not is_followup:
                    clear_product_buffer()
                    print("🧹 Cleared product buffer for new search")

                result = call_function(tool_call.name, args)
                products, followup_questions = result
                    
                print(f"Function call returned in {time.time() - start_time:.4f} seconds")
                function_end = time.time()
                print(f"Function call returned after {function_end - start_time:.4f} seconds from start")
                
                # Add function result to history
                full_history.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result)
                })

    print(f"Chat message returned in {time.time() - start_time:.4f} seconds")
    return {
        "message": str(assistant_reply) + "\n\n" + (followup_questions or ""),
        "history": full_history[1:],  # Exclude system message
        "products": products,
    }