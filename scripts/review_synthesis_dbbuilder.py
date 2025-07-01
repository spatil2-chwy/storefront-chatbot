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
    dtype={
        "PRODUCT_ID": str,
        "PART_NUMBER": str,
        "PARENT_ID": str,
        "PARENT_PART_NUMBER": str
    }
)

# === Step 2: Load Review Synthesis JSONL ===
with open(REVIEW_SYNTH_PATH, "r") as f:
    review_map = {
        entry["product_id"]: entry
        for entry in map(json.loads, f)
    }

print(f"📊 Review synthesis data loaded: {len(review_map)} entries")

# === Step 3: Filter for Parent Products ===
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

# === Step 4: Build Documents & Metadata for Review Synthesis ===
product_rows = product_df.to_dict(orient='records')
documents = []
metadatas = []
ids = []

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
        "THUMBNAIL": row["THUMBNAIL"],
        "FULLIMAGE": row["FULLIMAGE"],
        "ATTR_PET_TYPE": row["ATTR_PET_TYPE"],
        "ATTR_FOOD_FORM": row["ATTR_FOOD_FORM"],
        "unanswered_faqs": row["Unanswered FAQs"] or "",
        "answered_faqs": answered_faqs,
        "has_review_synthesis": has_review_synthesis,
    }

    # Add review synthesis data to metadata if available
    if has_review_synthesis:
        review_data = review_map[part_number]
        metadata["review_synthesis"] = json.dumps(review_data)
        metadata["what_customers_love"] = json.dumps(review_data.get('what_customers_love', []))
        metadata["what_to_watch_out_for"] = json.dumps(review_data.get('what_to_watch_out_for', []))
        metadata["should_you_buy_it"] = review_data.get('should_you_buy_it', '')
    else:
        metadata["review_synthesis"] = json.dumps({
            "what_customers_love": ["No review synthesis available"],
            "what_to_watch_out_for": ["No review synthesis available"],
            "should_you_buy_it": "No review synthesis available"
        })
        metadata["what_customers_love"] = json.dumps(["No review synthesis available"])
        metadata["what_to_watch_out_for"] = json.dumps(["No review synthesis available"])
        metadata["should_you_buy_it"] = "No review synthesis available"

    # Add special diet tags
    if row["ATTR_SPECIAL_DIET"]:
        for tag in map(str.strip, row["ATTR_SPECIAL_DIET"].split(',')):
            if tag:
                metadata[f"specialdiettag:{tag}"] = True

    # Add ingredient tags
    if row["INGREDIENTS"]:
        for tag in map(str.strip, row["INGREDIENTS"].split(',')):
            if tag:
                metadata[f"ingredienttag:{tag}"] = True

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

# === Step 5: Initialize ChromaDB & Embed ===
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
collection = client.create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

print(f"✅ Created collection: {COLLECTION_NAME}")

# === Step 6: Batch Upload ===
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