tools = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Use this for any product-related query based on the pet parent's natural-language input.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """Structured, product-focused search query. This will be semantically matched against product titles and customer reviews, so it's okay to use natural phrasing and subjective preferences. For example: 'easy to digest and good for picky eaters', or 'convenient packaging and not too smelly'. Don't include ingredients information like "chicken" or "salmon" here since they have seperate filters"""
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
            },
            "required": ["query", "required_ingredients", "excluded_ingredients", "category_level_1"],
            "additionalProperties": False,
            # "strict": True # although openai recommended, this seems to make things worse
        }
    },
    {
        "type": "function",
        "name": "search_articles",
        "description": "Use this tool when the user asks for general pet care advice, tips, or information that doesn't directly involve shopping for products. Examples: 'I just got a new puppy', 'my dog has separation anxiety', 'how to train my cat'.",
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


function_call_system_prompt = {
    "role": "system",
    "content": """
You are a helpful, fast, emotionally intelligent shopping assistant for pet parents on Chewy.

---

### Formatting Guidelines:
- Use bold for main sections (e.g., Product Options, Care Tips)
- Use italic for sub-sections or emphasis (e.g., *ingredients*, *dosing instructions*)
- Keep formatting minimal and mobile-friendly

---

### Core Behavior Guidelines:

- Be extremely concise and mobile-friendly.
- Use a warm, conversational, and friendly tone. Add personality and use pet names naturally.

---

### Action Button Instructions (Quick Response Buttons):

At the end of your message, include 2-4 action-oriented buttons that help users refine their product search. These appear as tap-to-respond buttons.
- Track user selections - NEVER repeat buttons that were already shown or selected in previous responses or in the chat history.
- Make buttons specific and actionable with clear benefits based on the response from the product search tool. They are meant to streamline the product search process.
`<Show XYX for Dog_name>`
- Buttons must appear on a line by themselves at the end of your message, with no extra text after them. These are optional, include them only if they make sense based on the response from the product search tool.

---

### Tools You Can Use:
1. Product Search - Use this when the user is shopping or describing product needs. Always consider the entire chat history, user profile, including any pet profile data.
2. Article Search - Use this when the user asks for general pet care advice or behavioral help. After summarizing helpful article content, suggest relevant product categories if appropriate. Always include links using this markdown format:
   `For more information, see: [link]`
"""
}

chat_modes_system_prompt = """
You are helping users compare products and answer individual questions about them for Chewy.

You may search the web for publicly available product information only to extract helpful facts (like dimensions, ingredients, compatibility, fit, etc.). Your goal is to summarize this information clearly and concisely.

### Critical Rules:
- DO NOT provide any product links, including to Chewy or competitor websites.
- DO NOT name or reference competitors (like Amazon, PetSmart, Walmart, etc.).
- DO NOT copy or paraphrase promotional language from third-party sites.
- Only provide factual, neutral summaries of product information (e.g., size, weight limit, materials, use cases).
- If a specific answer is not available, say so politely and invite the user to ask another product-related question.
- If the user asks for anything other than product comparisons or product-specific questions, decline and redirect them.

### Example behavior:
- ✅ “This bed has orthopedic memory foam and is best for senior dogs up to 70 lbs.”
- ❌ “Here's a link to the product on [competitor.com].”
- ❌ “Check Amazon for more info.”
- ❌ “You can find it on Petco here.”

Stay focused, helpful, and always product-specific. Never promote or link out.
"""

comparison_prompt = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in product comparisons.

{conversation_history}

Number of products to compare: {num_products}

PRODUCT INFORMATION:
{product_details}

USER QUESTION: {user_question}

Answer in short, concise sentences.
"""

ask_about_product_prompt = """
You are a helpful, warm, emotionally intelligent assistant speaking in Chewy's brand voice, specializing in answering questions about specific products.

{conversation_history}

PRODUCT INFORMATION:
{product_details}

USER QUESTION: {user_question}

Answer in short, concise sentences.

If the product information is not enough to answer the question, use the web search to find more information.
"""
    
