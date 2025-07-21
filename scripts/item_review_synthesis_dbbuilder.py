import pandas as pd
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np

# === Config ===
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

CSV_PATH = os.path.join(project_root, "data", "backend", "reviews", "all_chewy_products_with_qanda.csv")
REVIEW_SYNTH_PATH = os.path.join(project_root, "data", "backend", "reviews", "results.jsonl")

COLLECTION_NAME = "review_synthesis"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMADB_PATH = os.path.join(project_root, "data", "databases", "chroma_db")
BATCH_SIZE = 1000

# === Step 1: Load Data ===
print("Loading CSV data...")
df = pd.read_csv(
    CSV_PATH,
    header=None,  # No header row in CSV
    names=[
        "PRODUCT_ID", "PART_NUMBER", "PARENT_ID", "PARENT_PART_NUMBER", "TYPE", "NAME", 
        "DESCRIPTION_LONG", "CATEGORY_LEVEL_1", "CATEGORY_LEVEL_2", "CATEGORY_LEVEL_3", 
        "PRICE", "RATING_AVG", "RATING_CNT", "ATTR_PET_TYPE", "ATTR_FOOD_FORM", 
        "ATTR_SPECIAL_DIET", "IS_FOOD_FLAG", "INGREDIENTS", "MERCH_CLASSIFICATION1", 
        "MERCH_CLASSIFICATION2", "PARENT_COMPANY", "LIFE_STAGE", "MERCH_CLASSIFICATION3", 
        "AUTOSHIP_PRICE", "AUTOSHIP_SAVE_DESCRIPTION", "PRODUCT_TYPE", "BREED_SIZE", 
        "LIFESTAGE", "PET_TYPES", "FULLIMAGE", "THUMBNAIL", "MERCH_CLASSIFICATION4", 
        "PURCHASE_BRAND", "CLEAN_NAME", "Unanswered FAQs", "Answered FAQs"
    ],
    dtype={
        "PRODUCT_ID": str,
        "PART_NUMBER": str,
        "PARENT_ID": str,
        "PARENT_PART_NUMBER": str
    },
    low_memory=False,
)

# === Step 2: Separate Products and Items ===
print("Separating products and items...")
products = df[df['TYPE'] == 'Product'].copy()
items = df[df['TYPE'] == 'Item'].copy()

print(f"Products: {len(products)}")
print(f"Items: {len(items)}")

# === Step 3: Load Review Synthesis ===
print("Loading review synthesis data...")
with open(REVIEW_SYNTH_PATH, "r") as f:
    review_entries = [json.loads(line) for line in f]

# Create review map using part numbers
review_map = {str(entry["product_id"]): entry for entry in review_entries}
print(f"Review synthesis entries: {len(review_entries)}")

# === Step 4: Create Product ID to Review Synthesis Mapping ===
print("Creating product ID to review synthesis mapping...")
product_id_to_review = {}
products_with_reviews = products[products['PART_NUMBER'].astype(str).isin(review_map.keys())]

for _, product in products_with_reviews.iterrows():
    part_number = str(product['PART_NUMBER'])
    if part_number in review_map:
        product_id_to_review[product['PRODUCT_ID']] = review_map[part_number]

print(f"Products with review synthesis: {len(product_id_to_review)}")

# === Step 5: Define Default Synthesis ===
default_synth = {
    "what_customers_love": ["Insufficient reviews! No review synthesis"],
    "what_to_watch_out_for": ["Insufficient reviews! No review synthesis"],
    "should_you_buy_it": "Insufficient reviews! No review synthesis"
}

# === Step 6: Dynamic Review Synthesis Backfill Function ===
def get_review_synthesis_for_item(item_row, product_id_to_review, review_map, products):
    """
    Get review synthesis for an item using dynamic backfill logic:
    1. First try: direct match using item's PART_NUMBER
    2. Second try: parent backfill using parent's review synthesis
    3. Third try: default synthesis
    """
    part_number = str(item_row['PART_NUMBER'])
    parent_id = item_row['PARENT_ID']
    
    # First try: direct match
    if part_number in review_map:
        return review_map[part_number], "direct"
    
    # Second try: parent backfill
    if pd.notna(parent_id) and parent_id in product_id_to_review:
        return product_id_to_review[parent_id], "parent_backfill"
    
    # Third try: default
    return default_synth, "default"

# === Step 6.5: Data Backfill Function ===
def backfill_item_data_from_parent(item_row, parent_lookup):
    """
    Backfill missing item data from parent product where safe to do so.
    Returns a copy of the item row with backfilled data.
    """
    item_data = item_row.copy()
    parent_id = item_row['PARENT_ID']
    
    if pd.notna(parent_id) and parent_id in parent_lookup:
        parent = parent_lookup[parent_id]
        
        # All fields to backfill
        fields_to_backfill = [
            'CATEGORY_LEVEL_1', 'CATEGORY_LEVEL_2', 'CATEGORY_LEVEL_3',
            'PURCHASE_BRAND', 'ATTR_PET_TYPE', 'ATTR_FOOD_FORM', 
            'ATTR_SPECIAL_DIET', 'IS_FOOD_FLAG', 'DESCRIPTION_LONG', 'INGREDIENTS'
        ]
        
        # Backfill fields if item is missing them
        for field in fields_to_backfill:
            if field in parent and (pd.isna(item_data[field]) or item_data[field] == '' or item_data[field] == 'nan'):
                item_data[field] = parent[field]
    
    # Ensure INGREDIENTS is always a string
    if pd.isna(item_data['INGREDIENTS']) or item_data['INGREDIENTS'] == '' or item_data['INGREDIENTS'] == 'nan':
        item_data['INGREDIENTS'] = ""
    else:
        item_data['INGREDIENTS'] = str(item_data['INGREDIENTS'])
    
    return item_data

# === Step 7: Filter and Prepare Items ===
print("Preparing items for processing...")
items_df = items.fillna({
    "NAME": "",
    "CLEAN_NAME": "",
    "DESCRIPTION_LONG": "",
    "CATEGORY_LEVEL_1": "",
    "CATEGORY_LEVEL_2": "",
    "CATEGORY_LEVEL_3": "",
    "PRICE": 0.0,
    "AUTOSHIP_PRICE": 0.0,
    "RATING_AVG": 0.0,
    "RATING_CNT": 0.0,
    "ATTR_PET_TYPE": "",
    "ATTR_FOOD_FORM": "",
    "ATTR_SPECIAL_DIET": "",
    "INGREDIENTS": "",
    "THUMBNAIL": "",
    "FULLIMAGE": "",
    "PURCHASE_BRAND": "",
    "Unanswered FAQs": "",
    "Answered FAQs": "",
})

# Ensure INGREDIENTS column is string type
items_df['INGREDIENTS'] = items_df['INGREDIENTS'].astype(str)

# === Step 8: Pre-compute Optimizations ===
print("Pre-computing parent and sibling mappings...")

# Create parent lookup dictionary for O(1) access
parent_lookup = {}
for _, parent in products.iterrows():
    parent_lookup[parent['PRODUCT_ID']] = {
        "PARENT_PRODUCT_ID": parent['PRODUCT_ID'],
        "PARENT_PART_NUMBER": parent['PART_NUMBER'],
        "PARENT_NAME": parent['NAME'],
        "PARENT_CLEAN_NAME": parent['CLEAN_NAME'],
        # Add fields for backfilling
        "CATEGORY_LEVEL_1": parent.get('CATEGORY_LEVEL_1', ''),
        "CATEGORY_LEVEL_2": parent.get('CATEGORY_LEVEL_2', ''),
        "CATEGORY_LEVEL_3": parent.get('CATEGORY_LEVEL_3', ''),
        "PURCHASE_BRAND": parent.get('PURCHASE_BRAND', ''),
        "ATTR_PET_TYPE": parent.get('ATTR_PET_TYPE', ''),
        "ATTR_FOOD_FORM": parent.get('ATTR_FOOD_FORM', ''),
        "ATTR_SPECIAL_DIET": parent.get('ATTR_SPECIAL_DIET', ''),
        "IS_FOOD_FLAG": parent.get('IS_FOOD_FLAG', ''),
        "DESCRIPTION_LONG": parent.get('DESCRIPTION_LONG', ''),
        "INGREDIENTS": parent.get('INGREDIENTS', '')
    }

# Pre-compute sibling items by parent_id to avoid repeated lookups
sibling_lookup = {}
# Handle pandas Series properly
parent_ids_series = items_df['PARENT_ID']
unique_parent_ids = parent_ids_series.dropna().unique()
for parent_id in tqdm(unique_parent_ids):
    mask = items_df['PARENT_ID'] == parent_id
    sibling_items = items_df[mask].to_dict(orient='records')
    sibling_lookup[parent_id] = sibling_items

print(f"✅ Pre-computed {len(parent_lookup)} parent mappings and {len(sibling_lookup)} sibling groups")

# === Step 9: Build Documents & Metadata for Items ===
print("Building documents and metadata for items...")
documents = []
metadatas = []
ids = []

# Track review synthesis statistics
items_with_direct_reviews = 0
items_with_parent_backfill = 0
items_with_default = 0
total_items = len(items_df)

# Pre-compute review synthesis for all items using vectorized operations
print("Pre-computing review synthesis for all items...")
review_synthesis_results = []

for _, row in items_df.iterrows():
    review_data, source = get_review_synthesis_for_item(row, product_id_to_review, review_map, products)
    review_synthesis_results.append((review_data, source))

print("✅ Pre-computed review synthesis for all items")

# Process items with pre-computed data and apply backfill
processed_items = []
for idx, (_, row) in enumerate(tqdm(items_df.iterrows(), desc="Building documents and metadata", total=len(items_df))):
    # Apply data backfill from parent
    row = backfill_item_data_from_parent(row, parent_lookup)
    processed_items.append(row)
    
    product_id = row["PRODUCT_ID"]
    part_number = row["PART_NUMBER"]
    
    # Get pre-computed review synthesis
    review_data, source = review_synthesis_results[idx]
    
    # Track statistics
    if source == "direct":
        items_with_direct_reviews += 1
    elif source == "parent_backfill":
        items_with_parent_backfill += 1
    else:
        items_with_default += 1
    
    # Get product name for embedding
    clean_name = row["CLEAN_NAME"] or row["NAME"] or f"Product {product_id}"
    if not clean_name or clean_name.strip() == "":
        clean_name = f"Product {product_id}"

    # Add purchase brand to clean name if available
    purchase_brand = row["PURCHASE_BRAND"]
    if purchase_brand and str(purchase_brand).strip():
        clean_name += f" | Brand: {purchase_brand}"

    # Get answered FAQs (may or may not be available)
    answered_faqs = str(row.get("Answered FAQs", "") or "")

    # Build the combined text for embedding
    if source != "default":
        # Extract review synthesis data
        what_customers_love = review_data.get('what_customers_love', [])
        
        # Convert lists to strings
        what_customers_love_str = ' '.join(what_customers_love) if isinstance(what_customers_love, list) else str(what_customers_love)
        
        # Create combined text for embedding
        combined_text = f"PRODUCT NAME: {clean_name}\n\nWHAT CUSTOMERS LOVE: {what_customers_love_str}"
        
        # Add answered FAQs if available
        if answered_faqs and answered_faqs.strip() and answered_faqs != "nan":
            combined_text += f"\n\nANSWERED FAQs: {answered_faqs}"
    else:
        # For items without review synthesis, use product name and answered FAQs if available
        combined_text = f"PRODUCT NAME: {clean_name}"
        if answered_faqs and answered_faqs.strip() and answered_faqs != "nan":
            combined_text += f"\n\nANSWERED FAQs: {answered_faqs}"

    # Get parent information and sibling items using pre-computed lookups
    parent_info = {}
    sibling_items = []
    parent_id = row['PARENT_ID']
    if pd.notna(parent_id):
        if parent_id in parent_lookup:
            parent_info = parent_lookup[parent_id]
        if parent_id in sibling_lookup:
            sibling_items = sibling_lookup[parent_id]

    metadata = {
        "PRODUCT_ID": product_id,
        "PART_NUMBER": part_number,
        "NAME": row["NAME"],
        "CLEAN_NAME": row["CLEAN_NAME"],
        "PURCHASE_BRAND": parent_info.get("PURCHASE_BRAND", ""),
        "CATEGORY_LEVEL_1": parent_info.get("CATEGORY_LEVEL_1", ""),
        "CATEGORY_LEVEL_2": parent_info.get("CATEGORY_LEVEL_2", ""),
        "CATEGORY_LEVEL_3": parent_info.get("CATEGORY_LEVEL_3", ""),
        "PRICE": row["PRICE"],
        "AUTOSHIP_PRICE": row["AUTOSHIP_PRICE"],
        "RATING_AVG": row["RATING_AVG"],
        "RATING_CNT": row["RATING_CNT"],
        "DESCRIPTION_LONG": parent_info.get("DESCRIPTION_LONG", ""),
        "THUMBNAIL": row["THUMBNAIL"],
        "FULLIMAGE": row["FULLIMAGE"],
        "ATTR_PET_TYPE": parent_info.get("ATTR_PET_TYPE", ""),
        "ATTR_FOOD_FORM": parent_info.get("ATTR_FOOD_FORM", ""),
        "ATTR_SPECIAL_DIET": parent_info.get("ATTR_SPECIAL_DIET", ""),
        "INGREDIENTS": str(parent_info.get("INGREDIENTS", "")),
        "review_synthesis": json.dumps(review_data),
        "review_synthesis_source": source,
        "review_synthesis_flag": source != "default",  # True if has review synthesis (direct or parent backfill)
        "unanswered_faqs": row["Unanswered FAQs"] or "",
        "answered_faqs": answered_faqs,
        "items": json.dumps(sibling_items),  # Include sibling items
        **parent_info  # Include parent information
    }

    # Add special diet tags
    special_diet = row["ATTR_SPECIAL_DIET"]
    if pd.notna(special_diet) and str(special_diet).strip() and str(special_diet) != "nan":
        for tag in map(str.strip, str(special_diet).split(',')):
            if tag:
                metadata[f"specialdiettag:{tag}"] = True

    # Add ingredient tags
    ingredients = row["INGREDIENTS"]
    if pd.notna(ingredients) and str(ingredients).strip() and str(ingredients) != "nan":
        for tag in map(str.strip, str(ingredients).split(',')):
            if tag:
                metadata[f"ingredienttag:{tag.lower()}"] = True

    # Add category tags
    category1 = row["CATEGORY_LEVEL_1"]
    if pd.notna(category1) and str(category1).strip() and str(category1) != "nan":
        tag = str(category1).strip()
        if tag:
            metadata[f"categorytag1:{tag}"] = True
    
    category2 = row["CATEGORY_LEVEL_2"]
    if pd.notna(category2) and str(category2).strip() and str(category2) != "nan":
        tag = str(category2).strip()
        if tag:
            metadata[f"categorytag2:{tag}"] = True

    documents.append(combined_text)
    metadatas.append(metadata)
    ids.append(product_id)

# Save processed items to CSV with proper string handling
item_csv_path = os.path.join(project_root, "data", "backend", "products", "item_df.csv")
os.makedirs(os.path.dirname(item_csv_path), exist_ok=True)
processed_df = pd.DataFrame(processed_items)
processed_df.to_csv(item_csv_path, index=False)
print(f"✅ Saved processed items dataframe to: {item_csv_path}")

# Print review synthesis statistics
print(f"📊 Review Synthesis Statistics:")
print(f"   Total items: {total_items}")
print(f"   Items with direct review synthesis: {items_with_direct_reviews} ({items_with_direct_reviews/total_items*100:.1f}%)")
print(f"   Items with parent backfill: {items_with_parent_backfill} ({items_with_parent_backfill/total_items*100:.1f}%)")
print(f"   Items with default synthesis: {items_with_default} ({items_with_default/total_items*100:.1f}%)")
print(f"   Total coverage: {(items_with_direct_reviews + items_with_parent_backfill)/total_items*100:.1f}%")

print(f"✅ Prepared {len(documents)} item documents for embedding")

# === Step 9: Initialize ChromaDB & Embed ===
print("🔄 Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)

print("🔄 Initializing ChromaDB...")
client = chromadb.PersistentClient(path=CHROMADB_PATH)

# Delete existing item review synthesis collection if it exists
try:
    client.delete_collection(name=COLLECTION_NAME)
    print(f"🗑️  Deleted existing collection: {COLLECTION_NAME}")
except:
    pass

# Create new collection with proper embedding function
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

print(f"✅ Created collection: {COLLECTION_NAME}")

# === Step 10: Batch Upload ===
print("🔄 Starting batch embedding and upload...")
total_processed = 0

for i in tqdm(range(0, len(documents), BATCH_SIZE), desc="Processing batches"):
    doc_batch = documents[i:i + BATCH_SIZE]
    meta_batch = metadatas[i:i + BATCH_SIZE]
    id_batch = ids[i:i + BATCH_SIZE]

    try:
        # Generate embeddings
        emb_batch = model.encode(doc_batch, batch_size=32, show_progress_bar=False)
        
        # Convert to list format for ChromaDB
        emb_batch_list = emb_batch.tolist()
        
        # Validate embeddings
        if len(emb_batch_list) != len(doc_batch):
            print(f"❌ Embedding count mismatch: {len(emb_batch_list)} vs {len(doc_batch)}")
            continue
            
        # Upload to ChromaDB
        collection.upsert(
            documents=doc_batch,
            embeddings=emb_batch_list,
            metadatas=meta_batch,
            ids=id_batch,
        )
        
        total_processed += len(doc_batch)
        
    except Exception as e:
        print(f"❌ Error processing batch {i//BATCH_SIZE + 1}: {str(e)}")
        continue

print(f"✅ Successfully processed {total_processed} item documents")

# Verify the upload
try:
    count = collection.count()
    print(f"✅ ChromaDB collection now contains {count} item documents")
    
    # Test a query
    if count > 0:
        results = collection.query(
            query_texts=["customers love this product"],
            n_results=1
        )
        if results and 'ids' in results and results['ids'] and results['ids'][0]:
            print(f"✅ Test query successful, found {len(results['ids'][0])} results")
            
            # Show sample result
            if results['metadatas'] and results['metadatas'][0]:
                sample_id = results['ids'][0][0]
                sample_metadata = results['metadatas'][0][0]
                print(f"Sample result:")
                print(f"  ID: {sample_id}")
                print(f"  Name: {sample_metadata.get('NAME', 'N/A')}")
                print(f"  Review source: {sample_metadata.get('review_synthesis_source', 'N/A')}")
        
except Exception as e:
    print(f"❌ Error verifying upload: {str(e)}")

print("✅ Item review synthesis embedding process complete!") 