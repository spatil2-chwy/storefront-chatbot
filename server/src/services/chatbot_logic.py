from openai import OpenAI
from dotenv import load_dotenv
import json
import time
from os import getenv
load_dotenv()
from src.services.searchengine import query_products, rank_products
api_key = getenv("OPENAI_API_KEY_3")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
client = OpenAI(api_key=api_key)
# refactor needed, tools, system prompt, model, etc should be in a separate file
tools = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Searches for pet products like food, toys, and accessories based on a natural language query and filters. Use this function for ANY product-related query, including general searches like 'dog food', 'cat toys', etc. - even if no specific ingredients or diet requirements are mentioned.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "User intent in natural language, e.g. 'puppy food' or 'grain-free dog treats'"
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
IMPORTANT: When users ask about pet products (food, toys, accessories, etc.), you MUST use the search_products function to find relevant products. This includes general queries like "dog food", "cat toys", etc. - even if no specific ingredients or diet requirements are mentioned.
Do not answer questions unrelated to pet products. If you receive a non-product-related question, gently steer the conversation back to product needs.
Your tone should reflect:
- The deep, joyful, sometimes messy bond between pets and their people.
- Clear, empathetic, human guidance—like a kind, pet-savvy friend.
- No puns, gimmicks, or vague language. Be specific, mobile-friendly, and supportive.
Remember: Always search for products when users mention pet items, even if the query is general.
""",
}
MODEL = "gpt-4.1-nano"

def search_products(query: str, required_ingredients: list, excluded_ingredients: list, special_diet_tags: list):
    """Searches for pet products based on user query and filters.
    Parameters:
        query (str): User intent in natural language, e.g. 'puppy food' or 'grain-free dog treats'
        required_ingredients (list): List of ingredients that must be present in the product
        excluded_ingredients (list): List of ingredients that must not be present in the product
        special_diet_tags (list): List of special diet tags that the product must adhere to
    Returns:
        tuple: A tuple containing a list of products and a message
    """
    results = query_products(query, required_ingredients, excluded_ingredients, special_diet_tags)
    ranked_products = rank_products(results)
    
    if not ranked_products:
        return [], "No products found matching your criteria."

    message = "Products succesfully retrieved and are being displayed to the user! Ask the user if they want to see more details about products or refine the search."
    return ranked_products, message


function_mapping = {
    "search_products": search_products
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


def chat(user_input: str, history: list):
    start_time = time.time()
    print(f"Searching {user_input}:")
    full_history = (
        [system_message] + history + [{"role": "user", "content": user_input}]
    )

    # Step 1: Get model response
    response = client.responses.create(
        model=MODEL,
        input=full_history,
        tools=tools,
    )
    llm_time = time.time() - start_time
    print(f"First LLM response after {llm_time:.4f} seconds from start")
    # print(response)
    products = []

    if len(response.output) == 1 and response.output[0].type == "message":
        assistant_reply = response.output[0].content[0].text
        full_history.append({"role": "assistant", "content": assistant_reply})
    else:
        function_start = time.time()
        print(f"Function call start after {function_start - start_time:.4f} seconds from start")
        tool_call = response.output[0]
        full_history.append(tool_call)
        if tool_call.name != "search_products":
            raise ValueError(f"Unexpected tool call: {tool_call.name}")
        
        args = json.loads(tool_call.arguments)
        print(f"Calling {tool_call.name}(**{args})")
        result = call_function(tool_call.name, args)
        products, message = result
        function_end = time.time()
        print(f"Function call returned after {function_end - start_time:.4f} seconds from start")
        full_history.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": message,
        })
        # Instead of calling LLM again, use a predefined message
        assistant_reply = "Just found some products! Let me know if you would like to further refine your search."
        full_history.append({"role": "assistant", "content": assistant_reply})
    total_time = time.time() - start_time
    print(f"Chat message returned in {total_time:.4f} seconds")
    return {
        "message": assistant_reply,
        "history": full_history[1:],  # Exclude system message
        "products": products,
    }