import pandas as pd
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import chromadb

# === Config ===
CSV_PATH = "all_chewy_products_with_qanda.csv"
REVIEW_SYNTH_PATH = "results.jsonl"
COLLECTION_NAME = "products"
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

# === Step 2: Build Item Variant Map ===
df_items = df[df['TYPE'] == 'Item']
items_grouped = df_items.groupby('PARENT_ID')[['NAME', 'PART_NUMBER', 'PRODUCT_ID']].agg(list).to_dict(orient='index')

items_dict = {
    parent_id: [
        {"NAME": n, "PART_NUMBER": p, "PRODUCT_ID": pid}
        for n, p, pid in zip(vals["NAME"], vals["PART_NUMBER"], vals["PRODUCT_ID"])
    ]
    for parent_id, vals in items_grouped.items()
}

# === Step 3: Filter for Parent Products ===
product_df = df[df['TYPE'] == 'Product'].fillna({
    "NAME": "",
    "DESCRIPTION_LONG": "",
    "CATEGORY_LEVEL1": "",
    "CATEGORY_LEVEL2": "",
    "CATEGORY_LEVEL3": "",
    "PRICE": 0.0,
    "RATING_AVG": 0.0,
    "RATING_CNT": 0.0,
    "ATTR_PET_TYPE": "",
    "ATTR_FOOD_FORM": "",
    "ATTR_SPECIAL_DIET": "",
    "INGREDIENTS": ""
})

# === Step 4: Load Review Synthesis JSONL ===
with open(REVIEW_SYNTH_PATH, "r") as f:
    review_map = {
        entry["product_id"]: entry
        for entry in map(json.loads, f)
    }

# === Step 5: Build Documents & Metadata ===
default_synth = {
    "what_customers_love": ["Insufficient reviews! No review synthesis"],
    "what_to_watch_out_for": ["Insufficient reviews! No review synthesis"],
    "should_you_buy_it": "Insufficient reviews! No review synthesis"
}

product_rows = product_df.to_dict(orient="records")
documents = []
metadatas = []
ids = []

for row in product_rows:
    part_number = row["PART_NUMBER"]
    product_id = row["PRODUCT_ID"]

    metadata = {
        "PRODUCT_ID": product_id,
        "PART_NUMBER": part_number,
        "CATEGORY_LEVEL1": row["CATEGORY_LEVEL1"],
        "CATEGORY_LEVEL2": row["CATEGORY_LEVEL2"],
        "CATEGORY_LEVEL3": row["CATEGORY_LEVEL3"],
        "PRICE": row["PRICE"],
        "RATING_AVG": row["RATING_AVG"],
        "RATING_CNT": row["RATING_CNT"],
        "ATTR_PET_TYPE": row["ATTR_PET_TYPE"],
        "ATTR_FOOD_FORM": row["ATTR_FOOD_FORM"],
        "items": json.dumps(items_dict.get(product_id, [])),
        "review_synthesis": json.dumps(review_map.get(part_number, default_synth)),
        "review_synthesis_flag": part_number in review_map,
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
                metadata[f"ingredienttag:{tag}"] = True

    documents.append(row["NAME"])
    metadatas.append(metadata)
    ids.append(product_id)

# === Step 6: Initialize ChromaDB & Embed ===
model = SentenceTransformer(EMBEDDING_MODEL)
client = chromadb.PersistentClient(path=CHROMADB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

# === Step 7: Batch Upload ===
for i in tqdm(range(0, len(documents), BATCH_SIZE), desc="Processing batches"):
    doc_batch = documents[i:i + BATCH_SIZE]
    meta_batch = metadatas[i:i + BATCH_SIZE]
    id_batch = ids[i:i + BATCH_SIZE]

    emb_batch = model.encode(doc_batch, batch_size=BATCH_SIZE, show_progress_bar=False)

    collection.upsert(
        documents=doc_batch,
        embeddings=emb_batch,
        metadatas=meta_batch,
        ids=id_batch,
    )

print("✅ Embedding complete and uploaded to ChromaDB.")
