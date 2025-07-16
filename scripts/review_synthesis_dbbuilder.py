import pandas as pd
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np

# === Config ===
CSV_PATH = "all_chewy_products_with_qanda.csv"
REVIEW_SYNTH_PATH = "results.jsonl"

COLLECTION_NAME = "review_synthesis"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMADB_PATH = "chroma_db"
BATCH_SIZE = 1000

# === Step 1: Load Data ===
df = pd.read_csv(
    CSV_PATH,
    header=None,  # No header row in CSV
    names=[
        "PRODUCT_ID", "PART_NUMBER", "PARENT_ID", "PARENT_PART_NUMBER", "TYPE", "NAME", 
        "DESCRIPTION_LONG", "CATEGORY_LEVEL1", "CATEGORY_LEVEL2", "CATEGORY_LEVEL3", 
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
    low_memory=False
)

# === Step 2: Build Item Variant Map ===
df_items = df[df['TYPE'] == 'Item']

# Build items_dict using iterrows to avoid type checking issues
items_dict = {}
for parent_id, group in df_items.groupby('PARENT_ID'):
    items_dict[parent_id] = []
    for _, row in group.iterrows():
        items_dict[parent_id].append({
            "NAME": row["NAME"],
            "PART_NUMBER": row["PART_NUMBER"], 
            "PRODUCT_ID": row["PRODUCT_ID"]
        })

# Get first available images for each parent product from items
images_dict = {}
for parent_id, group in df_items.groupby('PARENT_ID'):
    # Get first non-null thumbnail and fullimage
    thumbnail = group['THUMBNAIL'].dropna().iloc[0] if group['THUMBNAIL'].dropna().size > 0 else None
    fullimage = group['FULLIMAGE'].dropna().iloc[0] if group['FULLIMAGE'].dropna().size > 0 else None
    
    images_dict[parent_id] = {
        "THUMBNAIL": thumbnail,
        "FULLIMAGE": fullimage
    }

# === Step 3: Load Review Synthesis JSONL ===
with open(REVIEW_SYNTH_PATH, "r") as f:
    review_map = {
        entry["product_id"]: entry
        for entry in map(json.loads, f)
    }

print(f"📊 Review synthesis data loaded: {len(review_map)} entries")

# === Step 3.5: Define Default Synthesis ===
default_synth = {
    "what_customers_love": ["Insufficient reviews! No review synthesis"],
    "what_to_watch_out_for": ["Insufficient reviews! No review synthesis"],
    "should_you_buy_it": "Insufficient reviews! No review synthesis"
}

# === Step 4: Filter for Parent Products ===
product_df = df[df['TYPE'] == 'Product'].fillna({
    "NAME": "",
    "CLEAN_NAME": "",
    "DESCRIPTION_LONG": "",
    "CATEGORY_LEVEL1": "",
    "CATEGORY_LEVEL2": "",
    "CATEGORY_LEVEL3": "",
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

# === Step 4.5: Fill Missing Thumbnails and Print Stats ===
# Track NaNs before filling
nan_before = product_df['THUMBNAIL'].isna().sum() + (product_df['THUMBNAIL'] == '').sum()

# Fill thumbnails from images_dict (based on item variants)
def fill_image(row, col):
    if not row[col]:  # empty string or NaN
        return images_dict.get(row['PRODUCT_ID'], {}).get(col, "")
    return row[col]

product_df['THUMBNAIL'] = product_df.apply(lambda row: fill_image(row, 'THUMBNAIL'), axis=1)
product_df['FULLIMAGE'] = product_df.apply(lambda row: fill_image(row, 'FULLIMAGE'), axis=1)

# Track NaNs after filling
nan_after = product_df['THUMBNAIL'].isna().sum() + (product_df['THUMBNAIL'] == '').sum()

print(f"🖼️ THUMBNAILs missing before fill: {nan_before}")
print(f"🖼️ THUMBNAILs missing after fill: {nan_after}")

# === Step 5: Build Documents & Metadata for Review Synthesis ===
product_rows = product_df.to_dict(orient='records')
documents = []
metadatas = []
ids = []

# save to csv
product_df.to_csv("product_df.csv", index=False)

# Track review synthesis statistics
products_with_reviews = 0
total_products = len(product_rows)

for row in product_rows:
    part_number = row["PART_NUMBER"]
    product_id = row["PRODUCT_ID"]
    
    # Check if this product has review synthesis
    has_review_synthesis = part_number in review_map
    if has_review_synthesis:
        products_with_reviews += 1
    
    # Get product name for embedding (always available)
    clean_name = row["CLEAN_NAME"] or row["NAME"] or f"Product {product_id}"
    if not clean_name or clean_name.strip() == "":
        clean_name = f"Product {product_id}"

    # add purchase brand to clean name if available: Brand: {row['PURCHASE_BRAND']}
    if row["PURCHASE_BRAND"]:
        clean_name += f" | Brand: {row['PURCHASE_BRAND']}"

    # Get answered FAQs (may or may not be available)
    answered_faqs = row.get("Answered FAQs", "") or ""

    # Build the combined text for embedding
    if has_review_synthesis:
        review_data = review_map[part_number]
        
        # Extract review synthesis data
        what_customers_love = review_data.get('what_customers_love', [])
        # what_to_watch_out_for = review_data.get('what_to_watch_out_for', [])
        
        # Convert lists to strings
        what_customers_love_str = ' '.join(what_customers_love) if isinstance(what_customers_love, list) else str(what_customers_love)
        # what_to_watch_out_for_str = ' '.join(what_to_watch_out_for) if isinstance(what_to_watch_out_for, list) else str(what_to_watch_out_for)
        
        # Create combined text for embedding
        combined_text = f"PRODUCT NAME: {clean_name}\n\nWHAT CUSTOMERS LOVE: {what_customers_love_str}"
        
        # Add answered FAQs if available
        if answered_faqs and answered_faqs.strip():
            combined_text += f"\n\nANSWERED FAQs: {answered_faqs}"
    else:
        # For products without review synthesis, use product name and answered FAQs if available
        combined_text = f"PRODUCT NAME: {clean_name}"
        if answered_faqs and answered_faqs.strip():
            combined_text += f"\n\nANSWERED FAQs: {answered_faqs}"

    metadata = {
        "PRODUCT_ID": product_id,
        "PART_NUMBER": part_number,
        "NAME": row["NAME"],
        "CLEAN_NAME": row["CLEAN_NAME"],
        "PURCHASE_BRAND": row["PURCHASE_BRAND"],
        "CATEGORY_LEVEL1": row["CATEGORY_LEVEL1"],
        "CATEGORY_LEVEL2": row["CATEGORY_LEVEL2"],
        "CATEGORY_LEVEL3": row["CATEGORY_LEVEL3"],
        "PRICE": row["PRICE"],
        "AUTOSHIP_PRICE": row["AUTOSHIP_PRICE"],
        "RATING_AVG": row["RATING_AVG"],
        "RATING_CNT": row["RATING_CNT"],
        "DESCRIPTION_LONG": row["DESCRIPTION_LONG"],
        "THUMBNAIL": row["THUMBNAIL"] if row["THUMBNAIL"] else images_dict.get(part_number, {}).get("THUMBNAIL", ""),
        "FULLIMAGE": row["FULLIMAGE"] if row["FULLIMAGE"] else images_dict.get(part_number, {}).get("FULLIMAGE", ""),
        "ATTR_PET_TYPE": row["ATTR_PET_TYPE"],
        "ATTR_FOOD_FORM": row["ATTR_FOOD_FORM"],
        "ATTR_SPECIAL_DIET": row["ATTR_SPECIAL_DIET"],
        "INGREDIENTS": row["INGREDIENTS"],
        "items": json.dumps(items_dict.get(product_id, [])),
        "review_synthesis": json.dumps(review_map.get(part_number, default_synth)),
        "review_synthesis_flag": has_review_synthesis,
        "unanswered_faqs": row["Unanswered FAQs"] or "",
        "answered_faqs": answered_faqs,
    }

    # Add special diet tags
    if row["ATTR_SPECIAL_DIET"]:
        for tag in map(str.strip, row["ATTR_SPECIAL_DIET"].split(',')):
            if tag:
                metadata[f"specialdiettag:{tag}"] = True

    # Add ingredient tags
    if row["INGREDIENTS"]:
        for tag in map(str.strip, row["INGREDIENTS"].split(',')):
            if tag:
                metadata[f"ingredienttag:{tag.lower()}"] = True

    # Add category tags
    if row["CATEGORY_LEVEL1"]:
        tag = row["CATEGORY_LEVEL1"].strip()
        if tag:
            metadata[f"categorytag1:{tag}"] = True
    if row["CATEGORY_LEVEL2"]:
        tag = row["CATEGORY_LEVEL2"].strip()
        if tag:
            metadata[f"categorytag2:{tag}"] = True

    documents.append(combined_text)
    metadatas.append(metadata)
    ids.append(product_id)

# Print review synthesis statistics
review_coverage = (products_with_reviews / total_products) * 100
print(f"📊 Review Synthesis Statistics:")
print(f"   Total products: {total_products}")
print(f"   Products with review synthesis: {products_with_reviews}")
print(f"   Coverage: {review_coverage:.1f}%")

print(f"✅ Prepared {len(documents)} documents for review synthesis embedding")

# === Step 6: Initialize ChromaDB & Embed ===
print("🔄 Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)

print("🔄 Initializing ChromaDB...")
client = chromadb.PersistentClient(path=CHROMADB_PATH)

# Delete existing review synthesis collection if it exists
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

# === Step 7: Batch Upload ===
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

print(f"✅ Successfully processed {total_processed} documents")

# Verify the upload
try:
    count = collection.count()
    print(f"✅ ChromaDB collection now contains {count} documents")
    
    # Test a query
    if count > 0:
        results = collection.query(
            query_texts=["customers love this product"],
            n_results=1
        )
        print(f"✅ Test query successful, found {len(results['ids'][0])} results")
        
except Exception as e:
    print(f"❌ Error verifying upload: {str(e)}")

print("✅ Review synthesis embedding process complete!") 