import pandas as pd
import json
import ast
from pathlib import Path

# === Config ===
CUSTOMERS_TSV_PATH = "data/core/customers.tsv"
PERSONAS_JSON_PATH = "data/core/user_personas_openai.json"
OUTPUT_TSV_PATH = "data/core/customers_with_personas.tsv"

def load_personas():
    """Load and parse the persona data from JSON"""
    with open(PERSONAS_JSON_PATH, 'r') as f:
        persona_strings = json.load(f)
    
    personas = []
    for persona_str in persona_strings:
        try:
            # Parse the string representation of the dictionary
            persona_dict = ast.literal_eval(persona_str)
            personas.append(persona_dict)
        except Exception as e:
            print(f"Error parsing persona: {e}")
            continue
    
    return personas

def extract_persona_fields(persona_dict):
    """Extract all persona fields from the persona dictionary"""
    persona = persona_dict.get('persona', {})
    filters = persona.get('filters', {})
    
    return {
        'persona_summary': persona.get('summary', ''),
        'preferred_brands': json.dumps(filters.get('preferred_brands', [])),
        'special_diet': json.dumps(filters.get('special_diet', [])),
        'possible_next_buys': filters.get('possible_next_buys', ''),
        'price_range_food': json.dumps(filters.get('price_range_food', {})),
        'price_range_treats': json.dumps(filters.get('price_range_treats', {})),
        'price_range_waste_management': json.dumps(filters.get('price_range_waste_management', {})),
        'price_range_beds': json.dumps(filters.get('price_range_beds', {})),
        'price_range_feeders': json.dumps(filters.get('price_range_feeders', {})),
        'price_range_leashes_and_collars': json.dumps(filters.get('price_range_leashes_and_collars', {}))
    }

def main():
    print("🔄 Loading personas...")
    personas = load_personas()
    print(f"✅ Loaded {len(personas)} personas")
    
    print("🔄 Loading customer data...")
    customers_df = pd.read_csv(CUSTOMERS_TSV_PATH, sep='\t')
    print(f"✅ Loaded {len(customers_df)} customers")
    
    print("🔄 Enhancing customer data with personas...")
    
    # Initialize persona columns with empty values
    persona_columns = [
        'persona_summary', 'preferred_brands', 'special_diet', 'possible_next_buys',
        'price_range_food', 'price_range_treats', 'price_range_waste_management',
        'price_range_beds', 'price_range_feeders', 'price_range_leashes_and_collars'
    ]
    
    for col in persona_columns:
        customers_df[col] = ''
    
    # Assign personas sequentially in batches of 10
    for i, customer_idx in enumerate(customers_df.index):
        persona_idx = i % len(personas)
        persona_fields = extract_persona_fields(personas[persona_idx])
        
        for field, value in persona_fields.items():
            customers_df.at[customer_idx, field] = value
    
    print("🔄 Saving enhanced customer data...")
    
    # Save with proper JSON handling - don't escape JSON strings
    customers_df.to_csv(OUTPUT_TSV_PATH, sep='\t', index=False, quoting=1)  # quoting=1 for QUOTE_ALL
    
    print(f"✅ Enhanced customer data saved to {OUTPUT_TSV_PATH}")
    print(f"📊 Total customers: {len(customers_df)}")
    print(f"🎯 Personas assigned: {len(personas)}")
    
    # Show sample of the enhanced data
    print("\n📋 Sample of enhanced data:")
    sample_cols = ['name', 'persona_summary', 'preferred_brands', 'special_diet']
    print(customers_df[sample_cols].head(3).to_string())

if __name__ == "__main__":
    main() 