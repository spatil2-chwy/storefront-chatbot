from openai import OpenAI
from dotenv import load_dotenv
import json
import time
from os import getenv
import time
from typing import List, Dict, Any, Optional, Union, cast
load_dotenv()
from src.services.searchengine import query_products, rank_products
from src.services.article_service import ArticleService
api_key = getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
client = OpenAI(api_key=api_key)
# refactor needed, tools, system prompt, model, etc should be in a separate file
tools = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Use this for any product-related query based on the pet parent's natural-language input. This includes initial needs (e.g. 'my cat has bad breath'), specific intents ('puppy training treats'), or conversationally described situations (e.g. 'my dog developed a chicken allergy. needs protein. should i switch to salmon? idk'). This function constructs a semantic query using the user's language and applies optional filters like ingredients or diet tags. ",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """Structured, product-focused search query. Map the situation to **specific, search-friendly product types** that Chewy likely sells. This will be semantically matched against product **titles and customer reviews**, so it's okay to use **natural phrasing**, subjective preferences, or descriptive modifiers. For example: 'easy to digest and good for picky eaters', or 'convenient packaging and not too smelly'. Don't include ingredients information like "chicken" or "salmon" here since they have seperate filters"""
                },
                "required_ingredients": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Ingredients must be concrete foods like 'chicken', 'salmon', 'peas'. Do not use generic terms like 'protein', 'grain', or nutrient types — they are not ingredients."
                    },
                    "description": "List of required ingredients that must be present in the product. Leave empty if no specific ingredients are required. Ingredients should be in lowercase. Ingredients should be in the format of 'ingredient_name' (e.g. 'chicken', 'peas')."
                },
                "excluded_ingredients": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Ingredients must be concrete foods like 'chicken', 'salmon', 'peas'. Do not use generic terms like 'protein', 'grain', or nutrient types — they are not ingredients."
                    },
                    "description": "List of ingredients that must not be present in the product. Leave empty if no specific ingredients should be excluded. Ingredients should be in lowercase. Ingredients should be in the format of 'ingredient_name' (e.g. 'chicken', 'peas')."
                },
                "category_level_1": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ['Farm', 'Bird', 'Cat', 'Dog', 'Fish', 'Wild Bird', 'Reptile', 'Horse', 'Small Pet', 'Gifts & Books', 'Pharmacy', 'Gift Cards', 'Virtual Bundle', 'Services', 'ARCHIVE', 'Programs'],
                        "description": "The category of the product, e.g. 'Dog', 'Cat'.. if applicable"
                    },
                    "description": "The first level category of the product, e.g. 'Dog', 'Cat'.. if applicable. Leave empty if no category is required."
                },
                "category_level_2": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ['Chicken', 'Litter & Nesting', 'Beds, Crates & Gear', 'Flea & Tick', 'Treats', 'Grooming', 'Food', 'Bowls & Feeders', 'Water Care', 'Sand & Gravel', 'Tools & Hobby Products', 'Cleaning & Maintenance', 'Filters & Media', 'Dog Apparel', 'Aquariums & Stands', 'Litter & Accessories', 'Leashes & Collars', 'Horse Tack', 'Stable Supplies', 'Toys', 'Health & Wellness', 'Cleaning', 'Waste Management', 'Habitat Accessories', 'Cages & Stands', 'Heating & Lighting', 'Decor & Accessories', 'Terrariums & Habitats', 'Beds & Hideouts', 'Cages & Habitats', 'Habitat Decor', 'Feed & Treats', 'Equestrian Riding Gear', 'Supplies', 'Farrier Supplies', 'Home Goods', 'Bedding & Litter', 'Training', 'Flea, Tick, Mite & Dewormers', 'Memorials & Keepsakes', 'Gift Cards', 'Drinkware & Kitchenware', 'Feeding Accessories', 'Books & Calendars', 'Prescription Food', 'Apparel & Accessories', 'Magnets & Decals', 'Harnesses & Carriers', 'Habitats', 'Virtual Bundle', 'Substrate & Bedding', 'Grooming & Topicals', 'Cleaning & Training', 'Healthcare Services', 'Apparel', 'Prescription Treats', 'Frozen Food', 'Human Food', 'Loyalty', 'Electronics & Accessories', 'Promotional'],
                        "description": "The second level category of the product, e.g. 'Treats', 'Grooming'.. if applicable."
                    },
                    "description": "The second level category of the product, e.g. 'Treats', 'Grooming'.. if applicable. Leave empty if no category is required."
                },
                "special_diet_tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "Grain-Free",
                            "No Corn No Wheat No Soy",
                            "Limited Ingredient Diet",
                            "Natural",
                            "With Grain",
                            "High-Protein",
                        ],
                        "description": "Special diet tags that the food product must adhere to, e.g. 'Grain-Free', 'Organic'. Leave empty if no specific diet tags are required, or if the product is not food."
                    },
                    "description": "List of special diet tags that the product must adhere to. Leave empty if no specific diet tags are required."
                },
            },
            "required": ["query", "required_ingredients", "excluded_ingredients", "category_level_1", "special_diet_tags"],
            "additionalProperties": False,
            # "strict": True # although openai recommended, this seems to make things worse
        }
    },
    {
        "type": "function",
        "name": "search_articles",
        "description": "Use this tool when the user asks for general pet care advice, tips, or information that doesn't directly involve shopping for products. Examples: 'I just got a new puppy', 'my dog has separation anxiety', 'how to train my cat', 'puppy care tips'. This searches through Chewy's expert articles and advice content.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for pet care articles and advice. Use natural language describing the pet situation, concern, or topic the user is asking about."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
]


system_message = {
    "role": "system",
    "content": """
You are a helpful, fast, emotionally intelligent shopping assistant for pet parents on Chewy.

Your job is to help users find the best products for their pet's specific needs and to provide helpful pet care advice.

You have two tools:
1. Product search - when users are shopping or describing product needs. Refer to entire chat history to understand the user's needs and preferences.
2. Article search - for general pet care advice or behavioral questions. When users ask for general pet advice (like "I just got a new puppy!" or pet care questions), use the article search tool to find relevant expert content. After providing helpful advice from articles, suggest relevant products they might need.

Key rules:
- Be concise and mobile-friendly.
- Only ask clarifying questions when absolutely necessary.
- Never include abstract terms like "protein", "grain", or "nutrients" in ingredient fields — only use real food items (e.g. chicken, peas).
- Convert vague user language into precise, Chewy-relevant product types.
- If a user mentions a concern (like allergies, picky eater, etc.), tailor the product query accordingly.
- Do NOT suggest articles when the user is clearly shopping, and vice versa.
- Avoid repetitive follow-up questions unless the user response is unclear.
- After products are loaded, you will receive a list of products with review synthesis and FAQs. Use this information to generate highly specific, helpful follow-up questions or statements that help the user narrow their choice.
- Provide the user with follow up questions rather than product suggestions unless the user asks about it.
- Do not suggest any products unless the user explicitly asks for them.
- Be vary conservative with your output length. If you have a lot of information, focus on the most relevant points and ask if the user wants to see more. We do not want to overwhelm users with too much information at once.
- Its better to call the product search tool more often than not, rather than trying to get clarification for pet info. That can be included in the follow up.
"""

}
MODEL = "gpt-4.1"

def search_products(query: str, required_ingredients: list, excluded_ingredients: list, category_level_1: list, category_level_2: list, special_diet_tags: list):
    """Searches for pet products based on user query and filters.
    Parameters:
        query (str): User intent in natural language, e.g. 'puppy food' or 'grain-free dog treats'
        required_ingredients (list): List of ingredients that must be present in the product
        excluded_ingredients (list): List of ingredients that must not be present in the product
        special_diet_tags (list): List of special diet tags that the product must adhere to
    Returns:
        list: A list of products
    """
    start = time.time()
    
    # Use ProductService to convert raw results to properly formatted Product objects
    from src.services.product_service import ProductService
    product_service = ProductService()
    
    # Use query_products for all searches (it handles empty filters fine)
    # This will automatically store the top 300 products in the buffer
    results = query_products(query, tuple(required_ingredients), tuple(excluded_ingredients), tuple(category_level_1), tuple(category_level_2), tuple(special_diet_tags))
    print(f"Query executed in {time.time() - start:.4f} seconds")
    
    ranking_start = time.time()
    ranked_products = rank_products(results)
    print(f"Ranking completed in {time.time() - ranking_start:.4f} seconds")
    
    if not ranked_products:
        return []
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
    return products

# Initialize ArticleService instance
article_service = ArticleService()

def search_articles(query: str):
    """Searches for relevant pet care articles and advice content.
    Parameters:
        query (str): User's question or topic about pet care, training, health, etc.
    Returns:
        str: Formatted article content for the LLM to reference
    """
    start = time.time()
    
    # Search for relevant articles
    articles = article_service.search_articles(query, n_results=3)
    
    print(f"Article search completed in {time.time() - start:.4f} seconds")
    
    if not articles:
        return "No relevant articles found for this topic."
    
    # Format articles for LLM consumption
    return article_service.get_article_summary_for_llm(articles)


function_mapping = {
    "search_products": search_products,
    "search_articles": search_articles,
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


def format_products_for_llm(products, limit=10):
    """Format products for LLM with review synthesis and FAQ data for follow-up generation"""
    if not products:
        return "No products found."
    
    # Get top 10 products with reviews or FAQs (similar to old logic)
    products_with_content = []
    for product in products:
        # Check if product has review synthesis or answered FAQs
        has_review_content = hasattr(product, 'what_customers_love') and product.what_customers_love
        has_faqs = hasattr(product, 'answered_faqs') and product.answered_faqs
        
        if has_review_content or has_faqs:
            products_with_content.append(product)
            if len(products_with_content) >= limit:
                break
    
    if not products_with_content:
        # Fallback to top 5 products if none have reviews/FAQs
        products_with_content = products[:5]
    
    lines = []
    for i, p in enumerate(products_with_content):
        # Basic product info
        product_line = f"{i+1}. {p.title}"
        
        # Add review synthesis if available
        if hasattr(p, 'what_customers_love') and p.what_customers_love:
            product_line += f"\n   What customers love: {p.what_customers_love}"
        
        if hasattr(p, 'what_to_watch_out_for') and p.what_to_watch_out_for:
            product_line += f"\n   What to watch out for: {p.what_to_watch_out_for}"
        
        # Add FAQ info if available
        if hasattr(p, 'answered_faqs') and p.answered_faqs:
            product_line += f"\n   Answered FAQs: {p.answered_faqs[:200]}..."
        
        lines.append(product_line)
    
    print(f"Formatted products for LLM: {lines}")
    return "Here are the top product recommendations with customer insights:\n\n" + "\n\n".join(lines)


def chat(user_input: str, history: list, user_context: str = ""):
    start_time = time.time()
    
    # Create system message with user context if provided
    system_msg = system_message.copy()
    if user_context:
        system_msg["content"] += f"\n\nCUSTOMER CONTEXT:\n{user_context}\n\nUse this information to provide personalized recommendations and for any logical follow-ups."
    
    full_history = (
        [system_msg] + history + [{"role": "user", "content": user_input}]
    )
    # print(full_history)
    # Step 1: Get model response
    response = client.responses.create(
        model=MODEL,
        input=full_history,
        tools=cast(Any, tools),
        temperature=0.1,
    )   
    print(f"First response received in {time.time() - start_time:.4f} seconds")
    # print(response)
    products = []
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
                print(f"🔧 LLM chose to use tool: {tool_call.name}")
                
                # Convert tool_call to dict for history
                tool_call_dict = {
                    "type": "function_call",
                    "id": tool_call.id,
                    "call_id": tool_call.call_id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments
                }
                full_history.append(tool_call_dict)
                
                if tool_call.name not in ["search_products", "search_articles"]:
                    raise ValueError(f"Unexpected tool call: {tool_call.name}")
                
                args = json.loads(tool_call.arguments)
                print(f"Calling {tool_call.name}(**{args}), its been {time.time() - start_time:.4f} seconds since the chat started")
                
                if tool_call.name == "search_articles":
                    # Handle article search differently - no products returned
                    result = call_function(tool_call.name, args)
                    article_content = result
                    
                    print(f"Article search returned in {time.time() - start_time:.4f} seconds")
                    
                    # Add function result to history
                    full_history.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": article_content
                    })

                    # generate a response
                    second_response = client.responses.create(
                        model=MODEL,
                        input=full_history,
                        # tools=[]  # No tools for this follow-up
                        temperature=0.1,
                    )

                    full_history.append({
                        "role": "assistant",
                        "content": second_response.output[0].content[0].text
                    })
                    assistant_reply = second_response.output[0].content[0].text

                    
                    continue  # Continue to next tool call or final response
                else:
                    products = call_function(tool_call.name, args)
                    print(f"Function call returned in {time.time() - start_time:.4f} seconds")
                    function_end = time.time()
                    print(f"Function call returned after {function_end - start_time:.4f} seconds from start")
                    
                    # Add function result to history
                    full_history.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": f"{len(products)} products returned"
                    })
                    
  
                    # Format and inject product context for LLM
                    product_context = format_products_for_llm(products)
                    full_history.append({
                        "role": "user",
                        "content": f"""
- Carefully read the review theme synthesis to identify product trade-offs, standout features, or pain points across products.
- Ask 1-3 short, highly specific follow-up questions or make short statements that help the user narrow their choice.
- Only include questions if there's real ambiguity or a decision to make. Don't ask generic questions.
- Only user review-data to generate follow-ups.
- Do not repeat already answered or previously asked questions. Say "These look like great options based on the reviews — go with what fits your style or budget!" if no more questions or clarifications are left to be asked or made.

Product Reviews: {product_context}

You're not being chatty — you're being helpful, warm, and efficient."""
                    })
                    # Now let the LLM generate the final message
                    final_response = client.responses.create(
                        model=MODEL,
                        input=full_history,
                        temperature=0.1,
                    )
                    final_reply = final_response.output[0].content[0].text
                    
                    assistant_reply = final_reply
    print(f"Chat message returned in {time.time() - start_time:.4f} seconds")
    return {
        "message": str(assistant_reply),
        "history": full_history[1:],  # Exclude system message
        "products": products,
    }