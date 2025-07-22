import pandas as pd
import json
import os
from typing import List, Dict, Any
import random

def reformat_image_link(link):
    """
    Reformatting image links to be displayable on web
    """
    if not link or not isinstance(link, str) or not link.strip():
        return "https://via.placeholder.com/400x300?text=Image+Not+Found"
    
    link = link.strip()
    
    # If it's already a valid HTTP URL, return as is
    if link.startswith("http"):
        return link
    
    # Handle Amazon-style URLs (base,timestamp format)
    if "," in link:
        link = link.lstrip("//")
        parts = link.split(",")
        if len(parts) == 2:
            base, timestamp = parts
            formatted = f"https://{base}._AC_SL600_V{timestamp}_.jpg"
            return formatted
    
    # If it starts with //, add https:
    if link.startswith("//"):
        formatted = f"https:{link}"
        return formatted
    
    # If it's a relative path or other format, try to make it absolute
    if not link.startswith("http"):
        formatted = f"https://{link}"
        return formatted
    
    return "https://via.placeholder.com/400x300?text=Image+Not+Found"

# Define the project root path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, "data", "backend", "products")
output_dir = os.path.join(project_root, "data", "backend", "products")

def load_product_data() -> pd.DataFrame:
    """Load the product data from CSV file."""
    product_df_path = os.path.join(data_dir, "item_df.csv")
    if not os.path.exists(product_df_path):
        raise FileNotFoundError(f"Product data file not found: {product_df_path}")
    
    print(f"Loading product data from {product_df_path}")
    df = pd.read_csv(product_df_path)
    print(f"Loaded {len(df)} products")
    return df

def filter_products_by_category(df: pd.DataFrame, category: str, subcategory: str = None, limit: int = 8) -> pd.DataFrame:
    """Filter products by category and subcategory, returning random products."""
    if subcategory:
        filtered = df[
            (df['CATEGORY_LEVEL_1'] == category) &
            (df['CATEGORY_LEVEL_2'] == subcategory)
        ]
    else:
        filtered = df[df['CATEGORY_LEVEL_1'] == category]
    
    # Filter out products with no price or no image
    filtered = filtered[
        (filtered['PRICE'] > 0) &
        (filtered['THUMBNAIL'].notna()) &
        (filtered['THUMBNAIL'] != '')
    ]
    
    # Randomly sample products
    if len(filtered) > limit:
        filtered = filtered.sample(n=limit, random_state=42)
    else:
        filtered = filtered.head(limit)
    
    return filtered

def product_to_dict(row: pd.Series) -> Dict[str, Any]:
    """Convert a product row to a dictionary format suitable for the frontend."""
    # Get and format images
    thumbnail = str(row['THUMBNAIL']) if pd.notna(row['THUMBNAIL']) else ""
    fullimage = str(row['FULLIMAGE']) if pd.notna(row['FULLIMAGE']) else ""
    
    # Format images using the reformat_image_link function
    formatted_thumbnail = reformat_image_link(thumbnail)
    formatted_fullimage = reformat_image_link(fullimage)
    
    return {
        "id": int(row['PRODUCT_ID']),
        "title": str(row['CLEAN_NAME']) if pd.notna(row['CLEAN_NAME']) else str(row['NAME']),
        "brand": str(row['PURCHASE_BRAND']) if pd.notna(row['PURCHASE_BRAND']) else "Unknown Brand",
        "price": float(row['PRICE']) if pd.notna(row['PRICE']) else 0.0,
        "autoshipPrice": float(row['AUTOSHIP_PRICE']) if pd.notna(row['AUTOSHIP_PRICE']) else 0.0,
        "rating": float(row['RATING_AVG']) if pd.notna(row['RATING_AVG']) else 0.0,
        "reviewCount": int(row['RATING_CNT']) if pd.notna(row['RATING_CNT']) else 0,
        "image": formatted_thumbnail,
        "images": [formatted_fullimage] if formatted_fullimage else [],
        "description": str(row['DESCRIPTION_LONG']) if pd.notna(row['DESCRIPTION_LONG']) else "",
        "category_level_1": str(row['CATEGORY_LEVEL_1']) if pd.notna(row['CATEGORY_LEVEL_1']) else "",
        "category_level_2": str(row['CATEGORY_LEVEL_2']) if pd.notna(row['CATEGORY_LEVEL_2']) else "",
        "keywords": [],
        "search_matches": [],
        "inStock": True,
        "deal": False
    }

def generate_landing_products() -> Dict[str, Any]:
    """Generate landing page products for different categories."""
    df = load_product_data()
    
    # Define categories and their search terms
    categories = {
        "dog_food": {
            "name": "Dog Food",
            "description": "Premium nutrition for your furry friend",
            "search_query": "dog food",
            "category": "Dog",
            "subcategory": "Food"
        },
        "cat_food": {
            "name": "Cat Food", 
            "description": "Delicious meals for your feline companion",
            "search_query": "cat food",
            "category": "Cat",
            "subcategory": "Food"
        },
        "dog_toys": {
            "name": "Dog Toys",
            "description": "Fun and engaging toys for dogs",
            "search_query": "dog toys",
            "category": "Dog",
            "subcategory": "Toys"
        },
        "dog_beds": {
            "name": "Dog Beds",
            "description": "Cozy beds for restful sleep",
            "search_query": "dog beds",
            "category": "Dog",
            "subcategory": "Beds, Crates & Gear"
        },
        "dog_treats": {
            "name": "Dog Treats",
            "description": "Delicious treats for training and rewards",
            "search_query": "dog treats",
            "category": "Dog",
            "subcategory": "Treats"
        },
        "cat_litter": {
            "name": "Cat Litter & Accessories",
            "description": "Clean and comfortable litter solutions",
            "search_query": "cat litter",
            "category": "Cat",
            "subcategory": "Litter & Accessories"
        },
        "dog_health": {
            "name": "Dog Health & Wellness",
            "description": "Supplements and health products for dogs",
            "search_query": "dog health supplements",
            "category": "Dog",
            "subcategory": "Health & Wellness"
        },
        "cat_toys": {
            "name": "Cat Toys",
            "description": "Entertaining toys for feline friends",
            "search_query": "cat toys",
            "category": "Cat",
            "subcategory": "Toys"
        }
    }
    
    landing_products = {
        "categories": {},
        "generated_at": pd.Timestamp.now().isoformat()
    }
    
    # Generate products for each category
    for category_key, category_info in categories.items():
        print(f"Processing category: {category_info['name']}")
        
        # Get products for this category
        products_df = filter_products_by_category(
            df, 
            category_info['category'], 
            category_info['subcategory']
        )
        
        if len(products_df) == 0:
            print(f"  No products found for {category_info['name']}")
            continue
        
        # Convert to dictionary format
        products = [product_to_dict(row) for _, row in products_df.iterrows()]
        
        landing_products["categories"][category_key] = {
            "name": category_info['name'],
            "description": category_info['description'],
            "search_query": category_info['search_query'],
            "products": products
        }
        
        print(f"  Found {len(products)} products")
    
    return landing_products

def save_landing_products(landing_products: Dict[str, Any], filename: str = "landing_products.json"):
    """Save landing products to JSON file."""
    output_path = os.path.join(output_dir, filename)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(landing_products, f, indent=2)
    
    print(f"Saved landing products to {output_path}")
    
    # Print summary
    total_products = sum(len(cat['products']) for cat in landing_products['categories'].values())
    print(f"\nSummary:")
    print(f"  Categories: {len(landing_products['categories'])}")
    print(f"  Total category products: {total_products}")

def main():
    """Main function to generate and save landing products."""
    print("Generating landing page products...")
    
    try:
        landing_products = generate_landing_products()
        save_landing_products(landing_products)
        print("✅ Landing products generated successfully!")
        
    except Exception as e:
        print(f"❌ Error generating landing products: {e}")
        raise

if __name__ == "__main__":
    main() 