tools = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Searches for pet products like food, toys, and accessories based on a natural language query and filters. ",
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
                # special diet tags with enums
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


def search_products(query: str, required_ingredients: list):
    return ([required_ingredients], "Products succesfully retrieved and are being displayed to the user!")

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





from openai import OpenAI
client = OpenAI()

history = [{"role": "system", "content": "You are a helpful assistant that can search for pet products."},
           {"role": "user", "content": "I need some puppy food that contains chicken and peas."}]


response = client.responses.create(
    model="gpt-4o-mini",
    input=history,
    tools=tools
)

print(response.output)

history = [{"role": "system", "content": "You are a helpful assistant that can search for pet products."},
           {"role": "user", "content": "I need some puppy food "}]


response = client.responses.create(
    model="gpt-4o-mini",
    input=history,
    tools=tools
)

print(response.output)

history = [{"role": "system", "content": "You are a helpful assistant that can search for pet products."},
           {"role": "user", "content": "I need some puppy food, he cant have corn or grain"}]


response = client.responses.create(
    model="gpt-4o-mini",
    input=history,
    tools=tools
)

print(response.output)

history = [{"role": "system", "content": "You are a helpful assistant that can search for pet products."},
           {"role": "user", "content": "i need a dog bed for my big dog"}]


response = client.responses.create(
    model="gpt-4o-mini",
    input=history,
    tools=tools
)

print(response.output)