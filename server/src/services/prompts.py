COMPARISON_PROMPT_TEMPLATE = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in product comparisons.

{conversation_history}

Number of products to compare: {num_products}

PRODUCT INFORMATION:
{product_details}

USER QUESTION: {user_question}

Answer in short, concise sentences.
"""

def format_product_details(products):
    """
    Format product details for the comparison prompt.
    """
    formatted_details = []
    
    for i, product in enumerate(products, 1):
        details = f"PRODUCT {i}: {product.get('title', 'Unknown Product')}\n"
        details += f"  Brand: {product.get('brand', 'Unknown')}\n"
        
        # Handle price safely
        price = product.get('price', 0)
        price = price if price is not None else 0
        details += f"  Price: ${price:.2f}\n"
        
        # Handle autoship price safely
        if product.get('autoshipPrice'):
            autoship_price = product.get('autoshipPrice', 0)
            autoship_price = autoship_price if autoship_price is not None else 0
            details += f"  Autoship Price: ${autoship_price:.2f}\n"
        
        # Handle rating safely
        rating = product.get('rating', 0)
        rating = rating if rating is not None else 0
        review_count = product.get('reviewCount', 0)
        review_count = review_count if review_count is not None else 0
        details += f"  Rating: {rating:.1f} stars ({review_count} reviews)\n"
        
        if product.get('description'):
            details += f"  Description: {product.get('description', '')}\n"
            
        if product.get('keywords'):
            details += f"  Key Features: {', '.join(product.get('keywords', []))}\n"
            
        if product.get('category'):
            details += f"  Category: {product.get('category', '')}\n"
            
        formatted_details.append(details)
    
    return "\n".join(formatted_details)

def get_comparison_prompt(user_question: str, products: list, history: list = None) -> str:
    """
    Generate a comparison prompt for the given user question and products.
    """
    product_details = format_product_details(products)
    
    # Format conversation history
    conversation_history = ""
    if history and len(history) > 0:
        conversation_history = "CONVERSATION HISTORY:\n"
        for msg in history:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            conversation_history += f"{role}: {msg.get('content', '')}\n"
        conversation_history += "\n"
    
    return COMPARISON_PROMPT_TEMPLATE.format(
        conversation_history=conversation_history,
        num_products=len(products),
        product_details=product_details,
        user_question=user_question
    )

ASK_ABOUT_PRODUCT_PROMPT_TEMPLATE = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in answering questions about specific products.

{conversation_history}

PRODUCT INFORMATION:
{product_details}

USER QUESTION: {user_question}

Answer in short, concise sentences.
"""

def format_single_product_details(product):
    """
    Format product details for the ask about product prompt.
    """
    details = f"Title: {product.get('title', 'Unknown Product')}\n"
    details += f"Brand: {product.get('brand', 'Unknown')}\n"
    
    # Handle price safely
    price = product.get('price', 0)
    price = price if price is not None else 0
    details += f"Price: ${price:.2f}\n"
    
    # Handle autoship price safely
    if product.get('autoshipPrice'):
        autoship_price = product.get('autoshipPrice', 0)
        autoship_price = autoship_price if autoship_price is not None else 0
        details += f"Autoship Price: ${autoship_price:.2f}\n"
    
    # Handle rating safely
    rating = product.get('rating', 0)
    rating = rating if rating is not None else 0
    review_count = product.get('reviewCount', 0)
    review_count = review_count if review_count is not None else 0
    details += f"Rating: {rating:.1f} stars ({review_count} reviews)\n"
    
    if product.get('description'):
        details += f"Description: {product.get('description', '')}\n"
        
    if product.get('keywords'):
        details += f"Key Features: {', '.join(product.get('keywords', []))}\n"
        
    if product.get('category'):
        details += f"Category: {product.get('category', '')}\n"
    
    return details

def get_ask_about_product_prompt(user_question: str, product_data: dict, history: list = None) -> str:
    """
    Generate a prompt for the given user question and product data.
    """
    product_details = format_single_product_details(product_data)
    
    # Format conversation history
    conversation_history = ""
    if history and len(history) > 0:
        conversation_history = "CONVERSATION HISTORY:\n"
        for msg in history:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            conversation_history += f"{role}: {msg.get('content', '')}\n"
        conversation_history += "\n"
    
    return ASK_ABOUT_PRODUCT_PROMPT_TEMPLATE.format(
        conversation_history=conversation_history,
        user_question=user_question,
        product_details=product_details
    )
    
