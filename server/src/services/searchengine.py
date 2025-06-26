import chromadb
from sentence_transformers import SentenceTransformer
COLLECTION_NAME = "products"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

model = SentenceTransformer(EMBEDDING_MODEL)
client = chromadb.PersistentClient(path="./../scripts/chroma_db")
collection = client.get_collection(name="products")


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

def query_products(query: str, required_ingredients: list, excluded_ingredients:list, special_diet_tags: list):
    where_clause = build_where_clause(required_ingredients, special_diet_tags)
    print(where_clause)
    if where_clause == {}:
        where_clause = None 
    results = collection.query(
        query_embeddings=model.encode([query]),
        n_results=100,
        where=where_clause,
    )
    return results

def rank_products(results):
    # for now we can rank like this:
    sorted_results = sorted(
        zip(results['metadatas'][0], results['documents'][0], results['ids'][0], results['distances'][0]),
        key=lambda x: (-x[0].get('RATING_AVG', 0), x[0].get('RATING_CNT', 0))
    )
    return sorted_results

# testing
if __name__ == "__main__":
    special_diet_needs = []
    ingredient_needs = ['Chicken', 'Pumpkin']
    # where_clause = build_where_clause(ingredient_needs, special_diet_needs)
    # print(where_clause)
    # results = collection.query(
    #     query_embeddings=model.encode(["dog food"]),
    #     n_results=100,
    #     where=where_clause,
    # )
    # print("Results:")
    # for doc, meta in zip(results['documents'], results['metadatas']):
    #     print(f"Document: {doc}, Metadata: {meta}")
    # print(f"Total results found: {len(results['documents'])}")

    results = query_products("dog food", ingredient_needs, special_diet_needs)
    ranked_products = rank_products(results)
    print("Ranked Products:")
    for metadata, document, product_id, distance in ranked_products:
        print(f"Product ID: {product_id}, Metadata: {metadata}, Document: {document}, Distance: {distance}")
