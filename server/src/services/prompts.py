COMPARISON_PROMPT_TEMPLATE = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in product comparisons.

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
        details += f"  Price: ${product.get('price', 0):.2f}\n"
        
        if product.get('autoshipPrice'):
            details += f"  Autoship Price: ${product.get('autoshipPrice', 0):.2f}\n"
            
        details += f"  Rating: {product.get('rating', 0):.1f} stars ({product.get('reviewCount', 0)} reviews)\n"
        
        if product.get('description'):
            details += f"  Description: {product.get('description', '')}\n"
            
        if product.get('keywords'):
            details += f"  Key Features: {', '.join(product.get('keywords', []))}\n"
            
        if product.get('category'):
            details += f"  Category: {product.get('category', '')}\n"
            
        formatted_details.append(details)
    
    return "\n".join(formatted_details)

def get_comparison_prompt(user_question: str, products: list) -> str:
    """
    Generate a comparison prompt for the given user question and products.
    """
    product_details = format_product_details(products)
    
    return COMPARISON_PROMPT_TEMPLATE.format(
        num_products=len(products),
        product_details=product_details,
        user_question=user_question
    ) 

ASK_ABOUT_PRODUCT_PROMPT_TEMPLATE = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in answering questions about specific products.

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
    details += f"Price: ${product.get('price', 0):.2f}\n"
    
    if product.get('autoshipPrice'):
        details += f"Autoship Price: ${product.get('autoshipPrice', 0):.2f}\n"
        
    details += f"Rating: {product.get('rating', 0):.1f} stars ({product.get('reviewCount', 0)} reviews)\n"
    
    if product.get('description'):
        details += f"Description: {product.get('description', '')}\n"
        
    if product.get('keywords'):
        details += f"Key Features: {', '.join(product.get('keywords', []))}\n"
        
    if product.get('category'):
        details += f"Category: {product.get('category', '')}\n"
    
    return details

def get_ask_about_product_prompt(user_question: str, product_data: dict) -> str:
    """
    Generate a prompt for the given user question and product data.
    """
    product_details = format_single_product_details(product_data)
    
    return ASK_ABOUT_PRODUCT_PROMPT_TEMPLATE.format(
        user_question=user_question,
        product_details=product_details
    )
    
