import chromadb
from sentence_transformers import SentenceTransformer
import os
from functools import lru_cache
import time

COLLECTION_NAME = "products"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Global variables for lazy initialization
_model = None
_client = None
_collection = None

def get_model():
    """Lazy load and cache the SentenceTransformer model"""
    global _model
    if _model is None:
        start_time = time.time()
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"Model loaded successfully in {time.time() - start_time:.4f} seconds")
    return _model

def get_collection():
    """Lazy load and cache the ChromaDB collection"""
    global _client, _collection
    if _collection is None:
        start_time = time.time()
        print("Initializing ChromaDB client...")
        # Get the absolute path to the chroma_db directory
        # current_dir =  # os.path.dirname(os.path.abspath(__file__))
        chroma_path = "./../scripts/chroma_db"  # os.path.join(current_dir, "../../scripts/chroma_db")
        _client = chromadb.PersistentClient(path=chroma_path)
        _collection = _client.get_collection(name=COLLECTION_NAME)
        print(f"ChromaDB collection loaded successfully in {time.time() - start_time:.4f} seconds")
    return _collection

@lru_cache(maxsize=100)
def encode_query(query: str):
    """Cache query encodings to avoid re-encoding the same queries"""
    start_time = time.time()
    result = get_model().encode([query])
    print(f"Query encoded in {time.time() - start_time:.4f} seconds")
    return result

# excluded ingredients feature on hold for now...
# def build_where_clause(required_ingredients: list, excluded_ingredients: list, special_diet_tags: list):
#     # build where clause for special diet and ingredients tags
#     if len(special_diet_tags) + len(required_ingredients) == 0 + len(excluded_ingredients):
#         where_clause = {}
#     elif len(special_diet_tags) + len(required_ingredients) + len(excluded_ingredients) == 1:
#         # if only one special diet or ingredient, use a single condition
#         if len(special_diet_tags) == 1:
#             where_clause = {f"specialdiettag:{special_diet_tags[0]}": {"$eq": True}}
#         elif len(required_ingredients) == 1:
#             where_clause = {f"ingredienttag:{required_ingredients[0]}": {"$eq": True}}
#         elif len(excluded_ingredients) == 1:
#             # what to do?
#             pass
#     else:
#         where_clause = {
#             "$and": [
#                 {
#                     f"specialdiettag:{diet}": {
#                         "$eq": True
#                     }
#                 } for diet in special_diet_tags
#             ] + [
#                 {
#                     f"ingredienttag:{ingredient}": {
#                         "$eq": True
#                     }
#                 } for ingredient in required_ingredients
#             ]  # what do do?
#         }

#     return where_clause

def build_where_clause(required_ingredients: list, special_diet_tags: list):
    # build where clause for special diet and ingredients tags
    if len(special_diet_tags) + len(required_ingredients) == 0:
        where_clause = {}
    elif len(special_diet_tags) + len(required_ingredients) == 1:
        # if only one special diet or ingredient, use a single condition
        if len(special_diet_tags) == 1:
            where_clause = {f"specialdiettag:{special_diet_tags[0]}": {"$eq": True}}
        else:
            where_clause = {f"ingredienttag:{required_ingredients[0]}": {"$eq": True}}
    else:
        where_clause = {
            "$and": [
                {
                    f"specialdiettag:{diet}": {
                        "$eq": True
                    }
                } for diet in special_diet_tags
            ] + [
                {
                    f"ingredienttag:{ingredient}": {
                        "$eq": True
                    }
                } for ingredient in required_ingredients
            ] 
        }

    return where_clause

def warmup():
    """Pre-load model and collection to avoid cold start delays"""
    print("Warming up search engine...")
    start_time = time.time()
    get_model()
    get_collection()
    # Test query to ensure everything is working
    encode_query("test query")
    print(f"Search engine warmed up in {time.time() - start_time:.4f} seconds")

def query_products(query: str, required_ingredients: list, excluded_ingredients: list, special_diet_tags: list):
    start_time = time.time()
    where_clause = build_where_clause(required_ingredients, special_diet_tags)
    if where_clause == {}:
        where_clause = None
    print(f"Where clause built in {time.time() - start_time:.4f} seconds") 
    
    collection = get_collection()
    query_start = time.time()
    query_embedding = encode_query(query)
    print(f"Query embedding retrieved in {time.time() - query_start:.4f} seconds")
    
    db_start = time.time()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=100,
        where=where_clause,
    )
    print(f"Database query completed in {time.time() - db_start:.4f} seconds")
    print(f"Total query_products time: {time.time() - start_time:.4f} seconds")
    return results

def rank_products(results):
    """Rank products by rating average and count"""
    start_time = time.time()
    # for now we can rank like this:
    sorted_results = sorted(
        zip(results['metadatas'][0], results['documents'][0], results['ids'][0], results['distances'][0]),
        key=lambda x: (-x[0].get('RATING_AVG', 0), x[0].get('RATING_CNT', 0))
    )
    print(f"Products ranked in {time.time() - start_time:.4f} seconds")
    return sorted_results

# testing
if __name__ == "__main__":
    special_diet_needs = []
    ingredient_needs = ['Chicken', 'Pumpkin']
    excluded_ingredients = []
    # where_clause = build_where_clause(ingredient_needs, special_diet_needs)
    # print(where_clause)
    # collection = get_collection()
    # results = collection.query(
    #     query_embeddings=encode_query("dog food"),
    #     n_results=100,
    #     where=where_clause,
    # )
    # print("Results:")
    # for doc, meta in zip(results['documents'], results['metadatas']):
    #     print(f"Document: {doc}, Metadata: {meta}")
    # print(f"Total results found: {len(results['documents'])}")

    results = query_products("dog food", ingredient_needs, excluded_ingredients, special_diet_needs)
    ranked_products = rank_products(results)
    print("Ranked Products:")
    for metadata, document, product_id, distance in ranked_products:
        print(f"Product ID: {product_id}, Metadata: {metadata}, Document: {document}, Distance: {distance}")
