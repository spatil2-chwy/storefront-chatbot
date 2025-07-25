import json
import time
import logging
import re
from typing import List, Dict, Any, Optional, Union, cast, Generator
from src.search.product_search import query_products, rank_products
from src.search.article_search import ArticleService
from src.config.openai_loader import get_openai_client
from src.chat.prompts import function_call_system_prompt, tools

# Initialize logging first
from src.evaluation.logging_config import setup_logging
from src.evaluation.evaluation_logger import evaluation_logger
from src.evaluation.streaming_capture import capture_streaming_response
setup_logging()
logger = logging.getLogger(__name__)

# Get the centralized OpenAI client
client = get_openai_client()

MODEL = "gpt-4.1"

# Button generation system prompt addition
button_generation_prompt_addition = """

### 🔘 Dynamic Button Generation:

At the **end of your response**, generate 3-4 contextually relevant action buttons that help users refine their search based on your recommendations and the conversation flow.

**Button Format**: Place buttons on separate lines at the very end, formatted as: `<Button Text>`

**Context-Aware Button Guidelines:**
- **Make buttons specific to your response content** - for example, if you mention "soft chews vs hard chews", create buttons for both
- **Answer questions you pose** - if you ask about ingredients, create buttons like `<Show Multi-Ingredient Options>` and `<Show Simple Formula Options>`
- **Address specific mentions** - for example, if you mention "chicken sensitivity", include `<Show Chicken-Free Options>`
- **Consider pet context** - use pet size, breed, age appropriately (e.g., `<Show Small Breed Options>` for Chihuahuas)
- **Be actionable** - buttons should lead to meaningful product filtering

**AVOID REDUNDANT OPTIONS:**
- **Don't show buttons for information already known** about the pet (size, breed, life stage, type, allergies)
- **Don't show buttons for filters already applied** in the conversation
- **Focus on new, relevant options** that help narrow down the selection
- **Consider what the user already knows** and what would be genuinely helpful next steps

**Example Button Patterns:**
- Ingredient-based: `<Show Salmon Options>`, `<Show Grain-Free Options>`
- Form-based: `<Show Soft Chew Options>`, `<Show Liquid Supplements>`
- Health-based: `<Show Joint Support Options>`, `<Show Sensitive Stomach Options>`
- Preference-based: `<Show Budget-Friendly Options>`, `<Show Premium Options>`
- Category-based: `<Show Treats Options>`, `<Show Food Options>`
- Feature-based: `<Show Easy-to-Chew Options>`, `<Show Digestive Support Options>`

**Button Placement**: Always place buttons at the very end of your response with no additional text after them.
"""

def extract_buttons_from_response(assistant_response):
    """
    Extract button commands from the assistant's response.
    Looks for patterns like <Button Text> at the end of the response.
    """
    if not assistant_response:
        return []
    
    # Look for button patterns: <text inside angle brackets>
    button_pattern = r'<([^<>]+)>'
    
    # Find all button matches
    matches = re.findall(button_pattern, assistant_response)
    
    if not matches:
        return []
    
    # Clean up button text and validate
    buttons = []
    for match in matches:
        button_text = match.strip()
        
        # Skip if it's not a button-like pattern (avoid false matches)
        if (len(button_text) < 5 or  # Too short
            len(button_text) > 50 or  # Too long
            button_text.lower().startswith('http') or  # URL
            any(char in button_text for char in ['/', '\\', '@', '#'])):  # Invalid chars
            continue
            
        buttons.append(f"<{button_text}>")
    
    return buttons[:6]  # Limit to 6 buttons max





def clean_response_text(assistant_response):
    """
    Remove button markup from the response text for display,
    leaving clean response text without the button commands.
    """
    if not assistant_response:
        return assistant_response
    
    # Remove button patterns from the end of the response
    lines = assistant_response.strip().split('\n')
    
    # Remove lines that are just button patterns
    while lines and re.match(r'^\s*<[^<>]+>\s*$', lines[-1]):
        lines.pop()
    
    return '\n'.join(lines).strip()


class ButtonAwareGenerator:
    """
    Wrapper class that yields chunks and stores extracted buttons
    """
    def __init__(self, generator, on_complete_callback):
        self.generator = generator
        self.on_complete_callback = on_complete_callback
        self.extracted_buttons = []
        self.clean_response = ""
        self.complete_response = ""
        self.start_time = time.time()
    
    def __iter__(self):
        try:
            for chunk in self.generator:
                self.complete_response += chunk
                yield chunk
        finally:
            # Extract buttons and clean response
            self.extracted_buttons = extract_buttons_from_response(self.complete_response)
            self.clean_response = clean_response_text(self.complete_response)
            
            response_time = time.time() - self.start_time
            
            # Call the completion callback with clean response
            if self.on_complete_callback:
                self.on_complete_callback(self.clean_response, response_time)


def capture_streaming_response_with_buttons(generator, on_complete_callback):
    """
    Modified version of capture_streaming_response that extracts buttons
    from the complete response and returns both clean text and buttons.
    """
    return ButtonAwareGenerator(generator, on_complete_callback)


def search_products(query: str, required_ingredients=(), excluded_ingredients=(), category_level_1=(), category_level_2=(), pet_profile=None, user_context=None):
    """Searches for pet products based on user query and filters.
    Parameters:
        query (str): User intent in natural language, e.g. 'puppy food' or 'grain-free dog treats'
        required_ingredients (list): List of ingredients that must be present in the product
        excluded_ingredients (list): List of ingredients that must not be present in the product
        pet_profile (dict): Pet profile information for personalized search
        user_context (dict): User context information for personalized search
    Returns:
        list: A list of products
    """
    # Add pet allergies to excluded ingredients
    enhanced_excluded_ingredients = list(excluded_ingredients) if excluded_ingredients else []
    
    # Extract allergies from pet profile
    if pet_profile and pet_profile.get('allergies'):
        allergies = pet_profile['allergies']
        if isinstance(allergies, str):
            # Split by comma and clean up
            allergy_list = [allergy.strip().lower() for allergy in allergies.split(',') if allergy.strip()]
            enhanced_excluded_ingredients.extend(allergy_list)
        elif isinstance(allergies, list):
            enhanced_excluded_ingredients.extend([allergy.lower() for allergy in allergies if allergy])
    
    # Extract allergies from user context
    if user_context and user_context.get('pet_allergies'):
        allergies = user_context['pet_allergies']
        if isinstance(allergies, str):
            # Split by comma and clean up
            allergy_list = [allergy.strip().lower() for allergy in allergies.split(',') if allergy.strip()]
            enhanced_excluded_ingredients.extend(allergy_list)
        elif isinstance(allergies, list):
            enhanced_excluded_ingredients.extend([allergy.lower() for allergy in allergies if allergy])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_excluded_ingredients = []
    for ingredient in enhanced_excluded_ingredients:
        if ingredient not in seen:
            seen.add(ingredient)
            unique_excluded_ingredients.append(ingredient)
    
    logger.info(f"Searching products with query: '{query}', required ingredients: {required_ingredients}, excluded ingredients: {unique_excluded_ingredients}, category level 1: {category_level_1}, category level 2: {category_level_2}")
    logger.info(f"Pet profile: {pet_profile}, User context: {user_context}")
    start = time.time()
    
    # Use ProductService to convert raw results to properly formatted Product objects
    from src.services.product_service import ProductService
    product_service = ProductService()
    
    # Use query_products for all searches (it handles empty filters fine)
    # This will automatically store the top 300 products in the buffer
    product_search_start = time.time()
    results = query_products(query, tuple(required_ingredients), tuple(unique_excluded_ingredients), tuple(category_level_1), tuple(category_level_2))
    product_search_time = time.time() - product_search_start
    logger.info(f"Query executed in {product_search_time:.4f} seconds")
    
    ranking_start = time.time()
    ranked_products = rank_products(results)
    ranking_time = time.time() - ranking_start
    logger.info(f"Ranking completed in {ranking_time:.4f} seconds")
    
    if not ranked_products:
        return []
    search_analyzer_start = time.time()
    products = []
    for i, ranked_result in enumerate(ranked_products[:30]):  # Limit to 30 products
        try:
            # Filter user_context to only include pet-relevant information for search analyzer
            # This prevents persona/shopping preferences from influencing category matching
            filtered_user_context = None
            if user_context:
                # Only include pet-related context, not shopping preferences
                filtered_user_context = {
                    'pet_type': user_context.get('pet_type'),
                    'pet_breed': user_context.get('pet_breed'),
                    'pet_size': user_context.get('pet_size'),
                    'pet_life_stage': user_context.get('pet_life_stage'),
                    'pet_allergies': user_context.get('pet_allergies'),
                }
                # Remove None values
                filtered_user_context = {k: v for k, v in filtered_user_context.items() if v is not None}
                # If empty, set to None
                if not filtered_user_context:
                    filtered_user_context = None
            
            product = product_service._ranked_result_to_product(ranked_result, query, pet_profile, filtered_user_context, unique_excluded_ingredients)
            products.append(product)
        except Exception as e:
            logger.error(f"⚠️ Error converting ranked result to product: {e}")
            continue
    
    search_analyzer_time = time.time() - search_analyzer_start
    logger.info(f"Product conversion took: {search_analyzer_time:.4f} seconds ({len(products)} products)")

    total_tool_time = time.time() - start
    logger.info(f"Total search_products time: {total_tool_time:.4f} seconds")
    
    # Log detailed timing breakdown
    evaluation_logger.log_timing(
        tool_execution_time=total_tool_time,
        product_search_time=product_search_time,
        ranking_time=ranking_time,
        search_analyzer_time=search_analyzer_time
    )
    
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
    
    article_search_time = time.time() - start
    logger.info(f"Article search completed in {article_search_time:.4f} seconds")
    
    # Log article search timing
    evaluation_logger.log_timing(article_search_time=article_search_time)
    
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
    """Format products for LLM with review synthesis, FAQ data, and dynamic category analysis"""
    if not products:
        return "No products found."
    
    # Dynamically extract category matches from search results
    category_matches = {}
    for product in products[:limit]:
        if hasattr(product, 'search_matches') and product.search_matches:
            for match in product.search_matches:
                if ':' in match.field:
                    category, value = match.field.split(':', 2)
                    category = category.strip()
                    value = value.strip()
                    if category and value:
                        if category not in category_matches:
                            category_matches[category] = set()
                        category_matches[category].add(value)
    
    # Format category information dynamically
    category_info = []
    for category, values in category_matches.items():
        category_info.append(f"{category}: {', '.join(sorted(values))}")
    
    lines = []
    if category_info:
        lines.append("**Category Matches Found:**")
        lines.append(", ".join(category_info))
        lines.append("")
    
    # Get top products with reviews or FAQs
    products_with_content = []
    for product in products:
        has_review_content = hasattr(product, 'what_customers_love') and product.what_customers_love
        has_faqs = hasattr(product, 'answered_faqs') and product.answered_faqs
        
        if has_review_content or has_faqs:
            products_with_content.append(product)
            if len(products_with_content) >= limit:
                break
    
    if not products_with_content:
        products_with_content = products[:5]
    
    lines.append("**Top Product Recommendations:**")
    for i, p in enumerate(products_with_content):
        product_line = f"{i+1}. {p.title}"
        
        if hasattr(p, 'what_customers_love') and p.what_customers_love:
            product_line += f"\n   What customers love: {p.what_customers_love}"
        
        if hasattr(p, 'what_to_watch_out_for') and p.what_to_watch_out_for:
            product_line += f"\n   What to watch out for: {p.what_to_watch_out_for}"
        
        if hasattr(p, 'answered_faqs') and p.answered_faqs:
            product_line += f"\n   Answered FAQs: {p.answered_faqs[:200]}..."
        
        lines.append(product_line)
    
    return "\n\n".join(lines)


def chat_stream_with_products(user_input: str, history: list, user_context: str = "", image_base64: Optional[str] = None, pet_profile: dict = None, user_context_data: dict = None):
    """
    Streaming version of the chat function that yields text chunks as they're generated.
    Only streams the final response, not during function calls.
    Returns a tuple of (generator, products, buttons) where generator yields text chunks, 
    products is the list of found products, and buttons are the extracted UI buttons.
    """
    start_time = time.time()
    logger.info(f"User context: {user_context}")
    logger.info(f"Pet profile: {pet_profile}")
    logger.info(f"User context data: {user_context_data}")
    logger.info(f"Streaming chat started - User message: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
    
    # Start evaluation logging
    _ = evaluation_logger.start_new_query(
        raw_user_query=user_input,
        user_context=user_context,
        has_image=bool(image_base64)
    )
    
    # Create system message with user context and button generation instructions
    system_msg = function_call_system_prompt.copy()
    system_msg["content"] += button_generation_prompt_addition
    
    if user_context:
        system_msg["content"] += f"\n\nCUSTOMER CONTEXT:\n{user_context}\n\nAbove are details about the customer based on their historical shopping behavior as well as their current pets. Enhance user query with brand preferences and dietary needs if applicable. Use this information if applicable to provide personalized recommendations and for any logical follow-ups."
    
    # Check whether the user_input is already part of history
    if user_input in [item["content"] for item in history]:
        # Create user message with optional image
        if image_base64:
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
            full_history = (
            [system_msg] + history + [user_message]
        )
        else:
            full_history = (
                [system_msg] + history
            )
    else:
        if image_base64:
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
            full_history = (
            [system_msg] + history + [user_message]
            )
        else:
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
    function_call_time = time.time() - llm_start
    logger.info(f"Streaming LLM initial response received in {function_call_time:.3f}s")
    
    # Log LLM timing
    evaluation_logger.log_timing(function_call_time=function_call_time)
    
    # Log chat history
    evaluation_logger.log_chat_history(full_history)
    
    products = []
    buttons = []
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
        
        # For simple message responses, yield the complete text and extract buttons
        def simple_generator():
            yield assistant_reply
        
        # Capture the streaming response for evaluation and button extraction
        def on_simple_complete(response: str, response_time: float):
            total_time = time.time() - start_time
            evaluation_logger.log_assistant_response(response)
            evaluation_logger.log_timing(llm_response_time=response_time, total_processing_time=total_time)
            evaluation_logger.save_log()
        
        generator = capture_streaming_response_with_buttons(simple_generator(), on_simple_complete)
        return generator, products, generator.extracted_buttons
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
                    
                    # Log tool call with actual execution time
                    evaluation_logger.log_tool_call(tool_call.name, args, tool_exec_time)
                    
                    # Log article results and timing
                    evaluation_logger.log_timing(article_search_time=tool_exec_time)
                    
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
                    
                    # Capture the streaming response for evaluation and button extraction
                    def on_article_complete(response: str, response_time: float):
                        total_time = time.time() - start_time
                        evaluation_logger.log_assistant_response(response)
                        evaluation_logger.log_timing(llm_response_time=response_time, total_processing_time=total_time)
                        evaluation_logger.save_log()
                    
                    generator = capture_streaming_response_with_buttons(article_generator(), on_article_complete)
                    # Extract buttons after streaming completes
                    return generator, products, generator.extracted_buttons
                    
                else:
                    # Add pet profile and user context to search_products arguments
                    if tool_call.name == "search_products":
                        args["pet_profile"] = pet_profile
                        args["user_context"] = user_context_data
                    
                    products = call_function(tool_call.name, args)
                    tool_exec_time = time.time() - tool_exec_start
                    logger.info(f"Streaming product search completed in {tool_exec_time:.3f}s - found {len(products)} products")
                    
                    # Log tool call info (timing is already logged by search_products function)
                    if evaluation_logger.current_log:
                        tool_call_data = {
                            "tool_name": tool_call.name,
                            "arguments": args,
                        }
                        evaluation_logger.current_log.tool_calls.append(tool_call_data)
                    
                    # Log product results
                    evaluation_logger.log_product_results(products, limit=10)
                    
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
                    
                    # Log context formatting time
                    evaluation_logger.log_timing(context_formatting_time=context_time)
                    
                    full_history.append({
                        "role": "user",
                        "content": f"""
- Carefully read the review theme synthesis to identify product trade-offs, standout features, or pain points across products.
- Reference the category matches found in the search results when providing recommendations.
- Ask 1-3 short, highly specific follow-up questions or make short statements that help the user narrow their choice.
- Only include questions if there's real ambiguity or a decision to make. Don't ask generic questions.
- Only use review-data to generate follow-ups.
- Do not repeat already answered or previously asked questions. Say "These look like great options based on the reviews — go with what fits your style or budget!" if no more questions or clarifications are left to be asked or made.
- Generate contextually relevant action buttons at the end of your response based on your recommendations and questions.

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
                    
                    # Capture the streaming response for evaluation and button extraction
                    def on_product_complete(response: str, response_time: float):
                        nonlocal buttons
                        total_time = time.time() - start_time
                        evaluation_logger.log_assistant_response(response)
                        evaluation_logger.log_timing(llm_response_time=response_time, total_processing_time=total_time)
                        evaluation_logger.save_log()
                    
                    generator = capture_streaming_response_with_buttons(product_generator(), on_product_complete)
                    # Extract buttons after streaming completes
                    return generator, products, generator.extracted_buttons
    
    # Fallback generator (this should never be reached in normal operation)
    def fallback_generator():
        yield "Sorry, I couldn't process your request."
    
    return fallback_generator(), products, []




