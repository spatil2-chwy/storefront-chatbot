import json
import time
import logging
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
    logger.info(f"Searching products with query: '{query}', required ingredients: {required_ingredients}, excluded ingredients: {excluded_ingredients}, category level 1: {category_level_1}, category level 2: {category_level_2}")
    logger.info(f"Pet profile: {pet_profile}, User context: {user_context}")
    start = time.time()
    
    # Use ProductService to convert raw results to properly formatted Product objects
    from src.services.product_service import ProductService
    product_service = ProductService()
    
    # Use query_products for all searches (it handles empty filters fine)
    # This will automatically store the top 300 products in the buffer
    product_search_start = time.time()
    results = query_products(query, tuple(required_ingredients), tuple(excluded_ingredients), tuple(category_level_1), tuple(category_level_2))
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
            
            product = product_service._ranked_result_to_product(ranked_result, query, pet_profile, filtered_user_context)
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


def generate_dynamic_filter_buttons(products, pet_profile=None, user_context=None):
    """Dynamically generate relevant filter buttons based on search results and context"""
    if not products:
        return []
    
    # Extract available filters from search results dynamically
    available_filters = {}
    
    for product in products[:20]:  # Check first 20 products
        if hasattr(product, 'search_matches') and product.search_matches:
            for match in product.search_matches:
                if ':' in match.field:
                    category, value = match.field.split(':', 2)
                    category = category.strip()
                    value = value.strip()
                    
                    if category and value:
                        if category not in available_filters:
                            available_filters[category] = set()
                        available_filters[category].add(value)
    
    # Generate filter buttons dynamically
    buttons = []
    
    # Pet-specific filters based on pet profile
    if pet_profile:
        pet_type = pet_profile.get('type', '').lower()
        if pet_type:
            if 'dog' in pet_type:
                buttons.append('<Show Dog Options>')
            elif 'cat' in pet_type:
                buttons.append('<Show Cat Options>')
        
        # Size-based filters
        size = pet_profile.get('size', '').lower()
        if size:
            if any(word in size for word in ['small', 'mini', 'tiny']):
                buttons.append('<Show Small Breed Options>')
            elif any(word in size for word in ['large', 'giant', 'big']):
                buttons.append('<Show Large Breed Options>')
        
        # Life stage filters
        life_stage = pet_profile.get('life_stage', '').lower()
        if life_stage:
            if any(word in life_stage for word in ['senior', 'adult', 'mature']):
                buttons.append('<Show Senior Options>')
            elif any(word in life_stage for word in ['puppy', 'kitten', 'young']):
                buttons.append('<Show Puppy Options>')
    
    # Category-specific filters based on search results
    for category, values in available_filters.items():
        if len(values) > 0:
            # Take the most common value or first few values
            top_values = sorted(list(values))[:2]
            for value in top_values:
                if category.lower() in ['categories', 'category level 1', 'category level 2']:
                    buttons.append(f'<Show {value} Options>')
                elif category.lower() in ['product forms', 'food form']:
                    buttons.append(f'<Show {value} Options>')
                elif category.lower() in ['brands', 'brand']:
                    buttons.append(f'<Show {value} Options>')
    
    # Health-specific filters if health-related categories are found
    health_keywords = ['health', 'wellness', 'supplement', 'vitamin', 'joint', 'dental', 'digestive']
    for category, values in available_filters.items():
        if any(keyword in category.lower() for keyword in health_keywords):
            for value in values:
                if any(keyword in value.lower() for keyword in health_keywords):
                    buttons.append(f'<Show {value} Options>')
    
    return buttons[:6]  # Limit to 6 buttons to avoid overwhelming the user


def extract_category_insights(products, pet_profile=None):
    """Extract insights about categories found in search results for better response generation"""
    if not products:
        return {}
    
    insights = {
        'matched_categories': {},
        'pet_relevant_categories': {},
        'top_categories': [],
        'category_benefits': {}
    }
    
    # Extract category matches
    category_counts = {}
    for product in products[:20]:
        if hasattr(product, 'search_matches') and product.search_matches:
            for match in product.search_matches:
                if ':' in match.field:
                    category, value = match.field.split(':', 2)
                    category = category.strip()
                    value = value.strip()
                    
                    if category and value:
                        key = f"{category}: {value}"
                        category_counts[key] = category_counts.get(key, 0) + 1
                        
                        if category not in insights['matched_categories']:
                            insights['matched_categories'][category] = set()
                        insights['matched_categories'][category].add(value)
    
    # Find top categories by frequency
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    insights['top_categories'] = [cat for cat, count in sorted_categories[:5]]
    
    # Identify pet-relevant categories
    if pet_profile:
        pet_type = pet_profile.get('type', '').lower()
        size = pet_profile.get('size', '').lower()
        life_stage = pet_profile.get('life_stage', '').lower()
        
        for category, values in insights['matched_categories'].items():
            category_lower = category.lower()
            
            # Pet type relevance
            if pet_type and any(pet_word in category_lower for pet_word in ['pet type', 'pet types']):
                insights['pet_relevant_categories']['pet_type'] = list(values)
            
            # Size relevance
            if size and any(size_word in category_lower for size_word in ['size', 'breed size']):
                insights['pet_relevant_categories']['size'] = list(values)
            
            # Life stage relevance
            if life_stage and any(stage_word in category_lower for stage_word in ['life stage', 'life stages']):
                insights['pet_relevant_categories']['life_stage'] = list(values)
            
            # Form relevance (important for small breeds)
            if 'small' in size and any(form_word in category_lower for form_word in ['form', 'food form']):
                insights['pet_relevant_categories']['form'] = list(values)
    
    return insights


def analyze_query_for_categories(user_input, pet_profile=None):
    """Analyze user query to identify relevant categories and context"""
    if not user_input:
        return {}
    
    analysis = {
        'query_keywords': [],
        'health_focus': [],
        'size_considerations': [],
        'life_stage_focus': [],
        'form_preferences': []
    }
    
    query_lower = user_input.lower()
    
    # Extract keywords from query
    words = query_lower.split()
    analysis['query_keywords'] = [word for word in words if len(word) > 2]
    
    # Identify health-related focus
    health_keywords = ['supplement', 'vitamin', 'joint', 'dental', 'digestive', 'skin', 'coat', 'allergy', 'sensitive']
    analysis['health_focus'] = [keyword for keyword in health_keywords if keyword in query_lower]
    
    # Identify size considerations
    size_keywords = ['small', 'large', 'mini', 'giant', 'tiny', 'big']
    analysis['size_considerations'] = [keyword for keyword in size_keywords if keyword in query_lower]
    
    # Identify life stage focus
    stage_keywords = ['puppy', 'kitten', 'senior', 'adult', 'young', 'old']
    analysis['life_stage_focus'] = [keyword for keyword in stage_keywords if keyword in query_lower]
    
    # Identify form preferences
    form_keywords = ['chew', 'tablet', 'powder', 'liquid', 'soft', 'hard', 'treat']
    analysis['form_preferences'] = [keyword for keyword in form_keywords if keyword in query_lower]
    
    # Add pet profile context
    if pet_profile:
        pet_type = pet_profile.get('type', '').lower()
        size = pet_profile.get('size', '').lower()
        life_stage = pet_profile.get('life_stage', '').lower()
        
        if pet_type:
            analysis['query_keywords'].append(pet_type)
        if size:
            analysis['query_keywords'].append(size)
        if life_stage:
            analysis['query_keywords'].append(life_stage)
    
    return analysis


def chat_stream_with_products(user_input: str, history: list, user_context: str = "", image_base64: Optional[str] = None, pet_profile: dict = None, user_context_data: dict = None):
    """
    Streaming version of the chat function that yields text chunks as they're generated.
    Only streams the final response, not during function calls.
    Returns a tuple of (generator, products) where generator yields text chunks and products is the list of found products.
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
    
    # Create system message with user context if provided
    system_msg = function_call_system_prompt.copy()
    if user_context:
        system_msg["content"] += f"\n\nCUSTOMER CONTEXT:\n{user_context}\n\nAbove are details about the customer based on their historical shopping behavior as well as their current pets. Enhance user query with brand preferences and dietary needs if applicable. Use this information if applicable to provide personalized recommendations and for any logical follow-ups."
    
        # check whether the user_input is already part of history
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
        
        # Capture the streaming response for evaluation
        def on_simple_complete(response: str, response_time: float):
            total_time = time.time() - start_time
            evaluation_logger.log_assistant_response(response)
            evaluation_logger.log_timing(llm_response_time=response_time, total_processing_time=total_time)
            evaluation_logger.save_log()
        
        return capture_streaming_response(simple_generator(), on_simple_complete), products
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
                    
                    # Capture the streaming response for evaluation
                    def on_article_complete(response: str, response_time: float):
                        total_time = time.time() - start_time
                        evaluation_logger.log_assistant_response(response)
                        evaluation_logger.log_timing(llm_response_time=response_time, total_processing_time=total_time)
                        evaluation_logger.save_log()
                    
                    return capture_streaming_response(article_generator(), on_article_complete), products
                    
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
                    
                    # Generate dynamic filter buttons based on search results
                    filter_buttons = generate_dynamic_filter_buttons(products, pet_profile, user_context_data)
                    filter_context = f"\n\nAvailable Filters: {', '.join(filter_buttons)}" if filter_buttons else ""
                    
                    # Extract category insights for better response generation
                    category_insights = extract_category_insights(products, pet_profile)
                    insights_context = ""
                    if category_insights:
                        if category_insights['matched_categories']:
                            insights_context += f"\n\nCategory Matches: {category_insights['matched_categories']}"
                        if category_insights['pet_relevant_categories']:
                            insights_context += f"\n\nPet-Relevant Categories: {category_insights['pet_relevant_categories']}"
                        if category_insights['top_categories']:
                            insights_context += f"\n\nTop Categories: {category_insights['top_categories'][:3]}"
                    
                    # Analyze user query for category relevance
                    query_analysis = analyze_query_for_categories(user_input, pet_profile)
                    query_context = ""
                    if query_analysis:
                        if query_analysis['health_focus']:
                            query_context += f"\n\nHealth Focus: {query_analysis['health_focus']}"
                        if query_analysis['size_considerations']:
                            query_context += f"\n\nSize Considerations: {query_analysis['size_considerations']}"
                        if query_analysis['form_preferences']:
                            query_context += f"\n\nForm Preferences: {query_analysis['form_preferences']}"
                    
                    full_history.append({
                        "role": "user",
                        "content": f"""
- Carefully read the review theme synthesis to identify product trade-offs, standout features, or pain points across products.
- Reference the category matches found in the search results when providing recommendations.
- Ask 1-3 short, highly specific follow-up questions or make short statements that help the user narrow their choice.
- Only include questions if there's real ambiguity or a decision to make. Don't ask generic questions.
- Only use review-data to generate follow-ups.
- Do not repeat already answered or previously asked questions. Say "These look like great options based on the reviews — go with what fits your style or budget!" if no more questions or clarifications are left to be asked or made.
- Use the available filters to suggest relevant next steps when appropriate.

Product Reviews: {product_context}{filter_context}{insights_context}{query_context}

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
                    
                    # Capture the streaming response for evaluation
                    def on_product_complete(response: str, response_time: float):
                        total_time = time.time() - start_time
                        evaluation_logger.log_assistant_response(response)
                        evaluation_logger.log_timing(llm_response_time=response_time, total_processing_time=total_time)
                        evaluation_logger.save_log()
                    
                    return capture_streaming_response(product_generator(), on_product_complete), products
    
    # Fallback generator (this should never be reached in normal operation)
    def fallback_generator():
        yield "Sorry, I couldn't process your request."
    
    return fallback_generator(), products