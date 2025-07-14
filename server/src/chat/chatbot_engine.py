import json
import time
import logging
from typing import List, Dict, Any, Optional, Union, cast, Generator
from src.search.product_search import query_products, rank_products
from src.search.article_search import ArticleService
from src.config.openai_loader import get_openai_client
from src.chat.prompts import function_call_system_prompt, tools

# Initialize logging first
from src.utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Get the centralized OpenAI client
client = get_openai_client()

MODEL = "gpt-4.1"

def search_products(query: str, required_ingredients=(), excluded_ingredients=(), category_level_1=(), category_level_2=()):
    """Searches for pet products based on user query and filters.
    Parameters:
        query (str): User intent in natural language, e.g. 'puppy food' or 'grain-free dog treats'
        required_ingredients (list): List of ingredients that must be present in the product
        excluded_ingredients (list): List of ingredients that must not be present in the product
    Returns:
        list: A list of products
    """
    logger.info(f"Searching products with query: '{query}', required ingredients: {required_ingredients}, excluded ingredients: {excluded_ingredients}, category level 1: {category_level_1}, category level 2: {category_level_2}")
    start = time.time()
    
    # Use ProductService to convert raw results to properly formatted Product objects
    from src.services.product_service import ProductService
    product_service = ProductService()
    
    # Use query_products for all searches (it handles empty filters fine)
    # This will automatically store the top 300 products in the buffer
    results = query_products(query, tuple(required_ingredients), tuple(excluded_ingredients), tuple(category_level_1), tuple(category_level_2))
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



def chat_stream_with_products(user_input: str, history: list, user_context: str = "", image_base64: Optional[str] = None):
    """
    Streaming version of the chat function that yields text chunks as they're generated.
    Only streams the final response, not during function calls.
    Returns a tuple of (generator, products) where generator yields text chunks and products is the list of found products.
    """
    start_time = time.time()
    print(f"User context: {user_context}")
    logger.info(f"Streaming chat started - User message: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
    
    # Create system message with user context if provided
    system_msg = function_call_system_prompt.copy()
    if user_context:
        system_msg["content"] += f"\n\nCUSTOMER CONTEXT:\n{user_context}\n\nAbove are details about the customer based on their historical shopping behavior as well as their current pets. Enhance user query with brand preferences and dietary needs if applicable. Use this information if applicable to provide personalized recommendations and for any logical follow-ups."
    
    # Create user message with optional image
    if image_base64:
        user_message = {
            "role": "user",
            "content": [
                {"type": "input_text", "text": user_input},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image_base64}",
                },
            ],
        }
    else:
        user_message = {"role": "user", "content": user_input}
    
    full_history = (
        [system_msg] + history + [user_message]
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
                
                import json
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