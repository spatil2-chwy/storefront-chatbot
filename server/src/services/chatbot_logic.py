import json
import time
import logging
from typing import List, Dict, Any, Optional, Union, cast, Generator
from src.services.searchengine import query_products, rank_products
from src.services.article_service import ArticleService
from src.services.openai_client import get_openai_client

# Initialize logging first
from src.utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Get the centralized OpenAI client
client = get_openai_client()
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

Your job is to help users find the best products for their pet’s specific needs and provide helpful pet care advice.

---

### 🛠️ Tools You Can Use:
1. **Product Search** – Use this when the user is shopping or describing product needs. Always consider the entire chat history, including any pet profile data.
2. **Article Search** – Use this when the user asks for general pet care advice or behavioral help. After summarizing helpful article content, suggest relevant product categories if appropriate. Always include links using this markdown format:
   `For more information, see: [link]`

---

### 🧠 Core Behavior Guidelines:

- **Run product search immediately** when the user expresses shopping intent (e.g. “dog food,” “puppy bed”) — even if pet profile information is incomplete or missing. You can follow up afterward with helpful clarifying questions.
    - ❗ Do *not* pause the flow by asking “Which pet?” before running the search.
    - Use whatever pet profile data you already have. If unknown, follow up gently after returning products.
- **Be concise and mobile-friendly.**
- **Avoid suggesting articles if the user is clearly shopping**, and vice versa.
- **Only ask clarifying questions when absolutely necessary.**
- **Avoid repeating follow-up questions** unless the user’s reply is unclear.
- **Do not suggest specific products unless the user asks.** Provide relevant product follow-up questions instead.
- **Prioritize helpful follow-up questions after tool calls.** For example: “Would you prefer wet or dry food?” or “Is your dog a picky eater?”
- **Be conservative with message length.** Focus on the most useful points first, then offer to show more if needed.

---

### 🧪 Product Query Behavior:
- Tailor queries to user concerns (e.g. allergies, training, chewing).
- Convert vague user language into precise Chewy-relevant product types.
- Never include abstract ingredient types like “protein” or “grains.” Only use specific food items (e.g. “chicken,” “salmon,” “sweet potato”).

---

### 🧩 Tag Instructions (Frontend Auto Response Buttons):

At the **end of your message**, include **only tags directly related to suggestions made in that message**. These appear as tap-to-respond buttons.

**Tag examples:**
- Food Ingredients: `<Chicken> <Beef> <Salmon> <Lamb>`
- Formats: `<Dry> <Wet> <Mix>`
- Product Types: `<Crate> <Bed> <Harness> <Shampoo>`
- Concerns: `<Allergies> <Picky Eater> <Chewer> <Anxiety>`

**Example:**
> “Would you like to focus on dry or wet food options? <Dry><Wet>”

**Important:** Tags must appear on a line by themselves at the end of your message, with **no extra text after them.**

"""
}

MODEL = "gpt-4o"

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
    
    # print(f"Formatted products for LLM: {lines}")
    return "Here are the top product recommendations with customer insights:\n\n" + "\n\n".join(lines)


def chat(user_input: str, history: list, user_context: str = ""):
    start_time = time.time()
    logger.info(f"Chat started - User message: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
    
    # Log user context if provided
    if user_context:
        logger.info(f"User context provided: {len(user_context)} characters")
    
    # Create system message with user context if provided
    system_msg = system_message.copy()
    if user_context:
        system_msg["content"] += f"\n\nCUSTOMER CONTEXT:\n{user_context}\n\nUse this information to provide personalized recommendations and for any logical follow-ups."
    
    full_history = (
        [system_msg] + history + [{"role": "user", "content": user_input}]
    )
    
    logger.debug(f"Chat history length: {len(full_history)} messages")
    
    # Step 1: Get model response
    llm_start = time.time()
    response = client.responses.create(
        model=MODEL,
        input=full_history,
        tools=cast(Any, tools),
        temperature=0.1,
    )   
    llm_time = time.time() - llm_start
    logger.info(f"LLM initial response received in {llm_time:.3f}s")
    products = []
    assistant_reply = ""

    logger.debug(f"LLM response type: {response.output[0].type if response.output else 'empty'}")
    
    if len(response.output) == 1 and response.output[0].type == "message":
        # Handle direct message response (no tool calls)
        assistant_reply = response.output[0].content[0].text
        full_history.append({"role": "assistant", "content": assistant_reply})
        logger.info(f"Direct message response generated (no tool calls)")
    else:
        # Handle function call response
        function_start = time.time()
        logger.info(f"Function calls detected after {function_start - start_time:.3f}s")

        for output_item in response.output:
            if output_item.type == "function_call":
                tool_call = output_item
                logger.info(f"Tool call: {tool_call.name}")
                
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
                    logger.error(f"Unexpected tool call: {tool_call.name}")
                    raise ValueError(f"Unexpected tool call: {tool_call.name}")
                
                args = json.loads(tool_call.arguments)
                logger.debug(f"Tool call arguments: {args}")
                
                tool_exec_start = time.time()
                logger.info(f"Executing {tool_call.name} after {tool_exec_start - start_time:.3f}s from chat start")
                
                if tool_call.name == "search_articles":
                    # Handle article search differently - no products returned
                    result = call_function(tool_call.name, args)
                    article_content = result
                    tool_exec_time = time.time() - tool_exec_start
                    
                    logger.info(f"Article search completed in {tool_exec_time:.3f}s")
                    
                    # Add function result to history
                    full_history.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": article_content
                    })

                    # generate a response
                    second_llm_start = time.time()
                    second_response = client.responses.create(
                        model=MODEL,
                        input=full_history,
                        # tools=[]  # No tools for this follow-up
                        temperature=0.1,
                    )
                    second_llm_time = time.time() - second_llm_start
                    logger.info(f"Article response generation took {second_llm_time:.3f}s")

                    full_history.append({
                        "role": "assistant",
                        "content": second_response.output[0].content[0].text
                    })
                    assistant_reply = second_response.output[0].content[0].text

                    
                    continue  # Continue to next tool call or final response
                else:
                    products = call_function(tool_call.name, args)
                    tool_exec_time = time.time() - tool_exec_start
                    logger.info(f"Product search completed in {tool_exec_time:.3f}s - found {len(products)} products")
                    
                    # Add function result to history
                    full_history.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": f"{len(products)} products returned"
                    })
                    
                    # Format and inject product context for LLM
                    context_start = time.time()
                    product_context = format_products_for_llm(products)
                    context_time = time.time() - context_start
                    logger.debug(f"Product context formatting took {context_time:.3f}s")
                    
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
                    final_llm_start = time.time()
                    final_response = client.responses.create(
                        model=MODEL,
                        input=full_history,
                        temperature=0.1,
                    )
                    final_llm_time = time.time() - final_llm_start
                    logger.info(f"Final response generation took {final_llm_time:.3f}s")
                    
                    final_reply = final_response.output[0].content[0].text
                    assistant_reply = final_reply
    total_time = time.time() - start_time
    logger.info(f"Chat completed in {total_time:.3f}s - Response length: {len(assistant_reply)} chars")
    return {
        "message": str(assistant_reply),
        "history": full_history[1:],  # Exclude system message
        "products": products,
    }



def chat_stream_with_products(user_input: str, history: list, user_context: str = ""):
    """
    Streaming version of the chat function that yields text chunks as they're generated.
    Only streams the final response, not during function calls.
    Returns a tuple of (generator, products) where generator yields text chunks and products is the list of found products.
    """
    start_time = time.time()
    logger.info(f"Streaming chat started - User message: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
    
    # Create system message with user context if provided
    system_msg = system_message.copy()
    if user_context:
        system_msg["content"] += f"\n\nCUSTOMER CONTEXT:\n{user_context}\n\nUse this information to provide personalized recommendations and for any logical follow-ups."
        logger.info(f"User context provided for streaming: {len(user_context)} characters")
    
    full_history = (
        [system_msg] + history + [{"role": "user", "content": user_input}]
    )
    
    # Step 1: Get model response (non-streaming for function call detection)
    llm_start = time.time()
    response = client.responses.create(
        model=MODEL,
        input=full_history,
        tools=tools,
        temperature=0.1,
    )   
    llm_time = time.time() - llm_start
    logger.info(f"Streaming LLM initial response received in {llm_time:.3f}s")
    
    products = []
    assistant_reply = ""

    logger.debug(f"Streaming response type: {response.output[0].type if response.output else 'empty'}")
    
    if len(response.output) == 1 and response.output[0].type == "message":
        # Handle message response - stream the content
        try:
            assistant_reply = response.output[0].content[0].text
        except AttributeError:
            # Handle case where response doesn't have expected structure
            assistant_reply = "I understand your question. Let me help you with that."
            logger.warning("Unexpected response structure in streaming mode")
        
        full_history.append({"role": "assistant", "content": assistant_reply})
        logger.info(f"Streaming direct message response (no tool calls)")
        
        # For simple message responses, yield the complete text
        def simple_generator():
            yield assistant_reply
        
        return simple_generator(), products
    else:
        function_start = time.time()
        logger.info(f"Streaming function calls detected after {function_start - start_time:.3f}s")

        # Handle function call response
        for output_item in response.output:
            if output_item.type == "function_call":
                tool_call = output_item
                logger.info(f"Streaming tool call: {tool_call.name}")
                
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
                    logger.error(f"Unexpected streaming tool call: {tool_call.name}")
                    raise ValueError(f"Unexpected tool call: {tool_call.name}")
                
                args = json.loads(tool_call.arguments)
                logger.debug(f"Streaming tool call arguments: {args}")
                
                tool_exec_start = time.time()
                logger.info(f"Executing streaming {tool_call.name} after {tool_exec_start - start_time:.3f}s")
                
                if tool_call.name == "search_articles":
                    # Handle article search differently - no products returned
                    result = call_function(tool_call.name, args)
                    article_content = result
                    tool_exec_time = time.time() - tool_exec_start
                    
                    logger.info(f"Streaming article search completed in {tool_exec_time:.3f}s")
                    
                    # Add function result to history
                    full_history.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": article_content
                    })

                    # Generate streaming response for final message
                    stream_start = time.time()
                    stream = client.responses.create(
                        model=MODEL,
                        input=full_history,
                        temperature=0.1,
                        stream=True,
                    )
                    logger.debug(f"Streaming article response started after {stream_start - start_time:.3f}s")
                    
                    # Stream the response
                    def article_generator():
                        try:
                            for event in stream:
                                if event.type == "response.output_text.delta":
                                    chunk = event.delta
                                    if chunk:
                                        yield chunk
                                elif event.type == "response.completed":
                                    break
                                elif event.type == "error":
                                    raise Exception(f"Streaming error: {event.error}")
                        except Exception as e:
                            logger.error(f"Error in article streaming: {e}")
                            yield "Sorry, I'm having trouble processing your request right now. Please try again in a moment."
                    
                    return article_generator(), products
                    
                else:
                    products = call_function(tool_call.name, args)
                    tool_exec_time = time.time() - tool_exec_start
                    logger.info(f"Streaming product search completed in {tool_exec_time:.3f}s - found {len(products)} products")
                    
                    # Add function result to history
                    full_history.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": f"{len(products)} products returned"
                    })
                    
                    # Format and inject product context for LLM
                    context_start = time.time()
                    product_context = format_products_for_llm(products)
                    context_time = time.time() - context_start
                    logger.debug(f"Streaming product context formatting took {context_time:.3f}s")
                    
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
                    
                    # Now let the LLM generate the final message with streaming
                    stream_start = time.time()
                    stream = client.responses.create(
                        model=MODEL,
                        input=cast(Any, full_history),
                        temperature=0.1,
                        stream=True,
                    )
                    logger.debug(f"Streaming product response started after {stream_start - start_time:.3f}s")
                    
                    # Stream the response
                    def product_generator():
                        try:
                            for event in stream:
                                if event.type == "response.output_text.delta":
                                    chunk = event.delta
                                    if chunk:
                                        yield chunk
                                elif event.type == "response.completed":
                                    break
                                elif event.type == "error":
                                    raise Exception(f"Streaming error: {event.error}")
                        except Exception as e:
                            logger.error(f"Error in product streaming: {e}")
                            yield "Sorry, I'm having trouble processing your request right now. Please try again in a moment."
                    
                    return product_generator(), products
    
    total_time = time.time() - start_time
    logger.info(f"Streaming chat completed in {total_time:.3f}s")
    
    # Fallback generator
    def fallback_generator():
        yield "Sorry, I couldn't process your request."
    
    return fallback_generator(), products